import json
from decimal import Decimal
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from netbox.views import generic

from .models import FiberVendor, FiberRoute, FiberDropPoint, parse_core_string
from .forms import (
    FiberVendorForm, FiberVendorFilterForm,
    FiberRouteForm, FiberRouteFilterForm,
    FiberDropPointForm, FiberDropPointFilterForm
)
from .tables import FiberVendorTable, FiberRouteTable, FiberDropPointTable
from .filtersets import FiberVendorFilterSet, FiberRouteFilterSet, FiberDropPointFilterSet


# =====================================================================
# Fiber Vendor Views
# =====================================================================

class FiberVendorListView(generic.ObjectListView):
    queryset = FiberVendor.objects.all().annotate(
        route_count=Count('fiber_routes')
    )
    table = FiberVendorTable
    filterset = FiberVendorFilterSet
    filterset_form = FiberVendorFilterForm
    template_name = 'netbox_fiber/fibervendor_list.html'


class FiberVendorView(generic.ObjectView):
    queryset = FiberVendor.objects.all()
    template_name = 'netbox_fiber/fibervendor.html'

    def get_extra_context(self, request, instance):
        routes = instance.fiber_routes.all()
        total_km = routes.aggregate(total=Sum('total_length_km'))['total'] or Decimal('0.000')
        total_cores = routes.aggregate(total=Sum('total_cores'))['total'] or 0
        route_table = FiberRouteTable(routes)
        route_table.configure(request)
        return {
            'routes': routes,
            'total_km': total_km,
            'total_cores': total_cores,
            'route_table': route_table,
        }


class FiberVendorEditView(generic.ObjectEditView):
    queryset = FiberVendor.objects.all()
    form = FiberVendorForm


class FiberVendorDeleteView(generic.ObjectDeleteView):
    queryset = FiberVendor.objects.all()


# =====================================================================
# Fiber Route Views
# =====================================================================

class FiberRouteListView(generic.ObjectListView):
    queryset = FiberRoute.objects.all().select_related('vendor', 'start_site', 'end_site')
    table = FiberRouteTable
    filterset = FiberRouteFilterSet
    filterset_form = FiberRouteFilterForm
    template_name = 'netbox_fiber/fiberroute_list.html'


class FiberRouteView(generic.ObjectView):
    queryset = FiberRoute.objects.all().select_related('vendor', 'start_site', 'end_site')
    template_name = 'netbox_fiber/fiberroute.html'

    def get_extra_context(self, request, instance):
        drop_points = instance.get_ordered_drop_points()
        all_points = instance.get_all_points()
        core_map = instance.get_core_map()

        start_dp = instance.start_point_obj
        end_dp = instance.end_point_obj
        start_url = start_dp.site.get_absolute_url() if (start_dp and start_dp.site) else (instance.start_site.get_absolute_url() if instance.start_site else None)
        end_url = end_dp.site.get_absolute_url() if (end_dp and end_dp.site) else (instance.end_site.get_absolute_url() if instance.end_site else None)

        # Build linear schematic data for frontend rendering
        schematic_nodes = [
            {
                'id': 'start',
                'name': instance.start_point_display,
                'point_name': 'Starting Point',
                'type': 'start',
                'km': float(start_dp.distance_km) if (start_dp and start_dp.distance_km) else 0.0,
                'url': start_url,
                'dropped_cores': instance.parsed_start_cores,
            }
        ]
        for idx, dp in enumerate(drop_points, start=1):
            schematic_nodes.append({
                'id': f'dp_{dp.pk}',
                'name': dp.site_display,
                'point_name': f'Drop Point #{idx} ({dp.get_point_type_display()})',
                'type': 'drop',
                'point_type': dp.get_point_type_display(),
                'km': float(dp.distance_km) if dp.distance_km else None,
                'url': dp.site.get_absolute_url() if dp.site else dp.get_absolute_url(),
                'dropped_cores': dp.parsed_dropped_cores,
            })
        schematic_nodes.append({
            'id': 'end',
            'name': instance.end_point_display,
            'point_name': 'End Point',
            'type': 'end',
            'km': float(end_dp.distance_km) if (end_dp and end_dp.distance_km) else (float(instance.total_length_km) if instance.total_length_km else 0.0),
            'url': end_url,
            'dropped_cores': instance.parsed_end_cores,
        })

        return {
            'drop_points': drop_points,
            'all_points': all_points,
            'drop_points_table': FiberDropPointTable(all_points),
            'core_map': core_map,
            'schematic_nodes': schematic_nodes,
            'schematic_nodes_json': json.dumps(schematic_nodes),
            'total_cores_range': list(range(1, instance.total_cores + 1)),
        }


class FiberRouteEditView(generic.ObjectEditView):
    queryset = FiberRoute.objects.all()
    form = FiberRouteForm


class FiberRouteDeleteView(generic.ObjectDeleteView):
    queryset = FiberRoute.objects.all()


# =====================================================================
# Fiber Drop Point Views
# =====================================================================

class FiberDropPointListView(generic.ObjectListView):
    queryset = FiberDropPoint.objects.all().select_related('fiber_route', 'site')
    table = FiberDropPointTable
    filterset = FiberDropPointFilterSet
    filterset_form = FiberDropPointFilterForm
    template_name = 'netbox_fiber/fiberdroppoint_list.html'


class FiberDropPointView(generic.ObjectView):
    queryset = FiberDropPoint.objects.all().select_related('fiber_route', 'site')
    template_name = 'netbox_fiber/fiberdroppoint.html'

    def get_extra_context(self, request, instance):
        return {
            'parsed_dropped_cores': instance.parsed_dropped_cores,
            'parsed_passed_cores': instance.parsed_passed_cores,
        }


class FiberDropPointEditView(generic.ObjectEditView):
    queryset = FiberDropPoint.objects.all()
    form = FiberDropPointForm
    template_name = 'netbox_fiber/fiberdroppoint_edit.html'


class FiberDropPointDeleteView(generic.ObjectDeleteView):
    queryset = FiberDropPoint.objects.all()


# =====================================================================
# Dedicated Vendor View (Page to view Fibers based on Vendor Selection)
# =====================================================================

class VendorFiberView(View):
    """
    Dedicated view allowing users to select a vendor from a dropdown and view
    all associated fiber routes, statistics, drop points, and topology.
    """
    def get(self, request):
        vendors = FiberVendor.objects.all().order_by('name')
        selected_vendor_id = request.GET.get('vendor_id')

        selected_vendor = None
        routes = FiberRoute.objects.none()
        total_km = Decimal('0.000')
        total_cores = 0
        total_drop_points = 0

        if selected_vendor_id:
            try:
                selected_vendor = FiberVendor.objects.get(pk=selected_vendor_id)
                routes = selected_vendor.fiber_routes.all().select_related('start_site', 'end_site').prefetch_related('drop_points')
            except (FiberVendor.DoesNotExist, ValueError):
                selected_vendor = None

        if not selected_vendor and vendors.exists():
            selected_vendor = vendors.first()
            routes = selected_vendor.fiber_routes.all().select_related('start_site', 'end_site').prefetch_related('drop_points')

        if selected_vendor:
            total_km = routes.aggregate(total=Sum('total_length_km'))['total'] or Decimal('0.000')
            total_cores = routes.aggregate(total=Sum('total_cores'))['total'] or 0
            total_drop_points = FiberDropPoint.objects.filter(fiber_route__in=routes).count()

        # Build route breakdown cards data
        route_cards = []
        for r in routes:
            ordered_dp = list(r.get_ordered_drop_points())
            route_cards.append({
                'route': r,
                'drop_points': ordered_dp,
                'core_map': r.get_core_map(),
                'start_cores': r.parsed_start_cores,
                'end_cores': r.parsed_end_cores,
            })

        context = {
            'vendors': vendors,
            'selected_vendor': selected_vendor,
            'routes': routes,
            'route_cards': route_cards,
            'total_km': total_km,
            'total_cores': total_cores,
            'total_drop_points': total_drop_points,
            'total_routes': routes.count(),
        }
        return render(request, 'netbox_fiber/vendor_view.html', context)


# =====================================================================
# NetBox Topology View (Display Fiber Like in Topology View on Netbox)
# =====================================================================

class FiberTopologyView(View):
    """
    Renders an interactive NetBox-styled Topology View of fiber routes,
    sites, and drop points with vendor filtering and core visualization.
    """
    def get(self, request):
        vendors = FiberVendor.objects.all().order_by('name')
        selected_vendor_id = request.GET.get('vendor_id', '')
        selected_route_id = request.GET.get('route_id', '')

        routes = FiberRoute.objects.all().select_related('vendor', 'start_site', 'end_site').prefetch_related('drop_points')

        if selected_vendor_id:
            try:
                routes = routes.filter(vendor_id=int(selected_vendor_id))
            except ValueError:
                pass

        if selected_route_id:
            try:
                routes = routes.filter(id=int(selected_route_id))
            except ValueError:
                pass

        total_routes = routes.count()
        total_km = routes.aggregate(total=Sum('total_length_km'))['total'] or Decimal('0.000')

        context = {
            'vendors': vendors,
            'selected_vendor_id': selected_vendor_id,
            'selected_route_id': selected_route_id,
            'total_routes': total_routes,
            'total_km': total_km,
        }
        return render(request, 'netbox_fiber/topology.html', context)


class FiberTopologyDataAPI(View):
    """
    JSON API endpoint returning nodes and edges formatted for Vis.js / Cytoscape topology diagrams.
    """
    def get(self, request):
        vendor_id = request.GET.get('vendor_id')
        route_id = request.GET.get('route_id')

        routes = FiberRoute.objects.all().select_related('vendor', 'start_site', 'end_site').prefetch_related('drop_points')

        if vendor_id:
            try:
                routes = routes.filter(vendor_id=int(vendor_id))
            except ValueError:
                pass

        if route_id:
            try:
                routes = routes.filter(id=int(route_id))
            except ValueError:
                pass

        nodes = {}
        edges = []

        def get_or_create_node(name, node_type='site', site_obj=None, subtitle=''):
            node_id = f"node_{name.strip().lower().replace(' ', '_')}"
            if node_id not in nodes:
                color_map = {
                    'start_site': {'background': '#198754', 'border': '#146c43', 'highlight': {'background': '#20c997', 'border': '#0f5132'}},
                    'end_site': {'background': '#0d6efd', 'border': '#0a58ca', 'highlight': {'background': '#3d8bfd', 'border': '#084298'}},
                    'site': {'background': '#0dcaf0', 'border': '#0aa2c0', 'highlight': {'background': '#6edff6', 'border': '#055160'}},
                    'joint_box': {'background': '#ffc107', 'border': '#cc9a06', 'highlight': {'background': '#ffcd39', 'border': '#997404'}},
                    'odf': {'background': '#6f42c1', 'border': '#59359a', 'highlight': {'background': '#8c68cd', 'border': '#3d246c'}},
                    'other': {'background': '#6c757d', 'border': '#495057', 'highlight': {'background': '#adb5bd', 'border': '#343a40'}},
                }
                c = color_map.get(node_type, color_map['site'])
                nodes[node_id] = {
                    'id': node_id,
                    'label': name,
                    'title': f"<b>{name}</b><br>Type: {node_type.replace('_', ' ').title()}<br>{subtitle}",
                    'color': c,
                    'shape': 'dot',
                    'size': 24 if 'site' in node_type else 18,
                    'site_id': site_obj.pk if site_obj else None,
                    'node_type': node_type,
                }
            return node_id

        for route in routes:
            start_name = route.start_point_display
            end_name = route.end_point_display

            start_node_id = get_or_create_node(
                start_name,
                node_type='start_site',
                site_obj=route.start_site,
                subtitle=f"Starting Point of {route.name} | Cores Dropped: {route.start_cores_dropped or 'None'}"
            )
            end_node_id = get_or_create_node(
                end_name,
                node_type='end_site',
                site_obj=route.end_site,
                subtitle=f"End Point of {route.name} | Cores Dropped: {route.end_cores_dropped or 'None'}"
            )

            drop_points = list(route.get_ordered_drop_points())
            if not drop_points:
                # Direct route from Start to End
                edges.append({
                    'id': f"route_{route.pk}_direct",
                    'from': start_node_id,
                    'to': end_node_id,
                    'label': f"{route.name}\n({route.total_cores} Cores, {route.total_length_km} KM)",
                    'title': f"<b>{route.name}</b><br>Vendor: {route.vendor.name}<br>Type: {route.get_cable_type_display()}<br>Cores: {route.total_cores}<br>Length: {route.total_length_km} KM",
                    'width': max(2, min(8, int(route.total_cores / 4))),
                    'color': {'color': '#0d6efd', 'highlight': '#ffc107'},
                    'arrows': 'to;from',
                    'route_id': route.pk,
                })
            else:
                # Route through intermediate drop points
                chain = [start_node_id]
                for dp in drop_points:
                    dp_node_id = get_or_create_node(
                        dp.site_display,
                        node_type=dp.point_type,
                        site_obj=dp.site,
                        subtitle=f"Drop Point on {route.name}<br>Dropped Cores: {dp.dropped_cores}<br>KM: {dp.distance_km or 'N/A'}"
                    )
                    chain.append(dp_node_id)
                chain.append(end_node_id)

                for i in range(len(chain) - 1):
                    src = chain[i]
                    dst = chain[i + 1]
                    edges.append({
                        'id': f"route_{route.pk}_seg_{i}",
                        'from': src,
                        'to': dst,
                        'label': f"{route.name}" if i == 0 else "",
                        'title': f"<b>{route.name} (Segment {i + 1})</b><br>Vendor: {route.vendor.name}<br>Total Cores: {route.total_cores}<br>Total Route KM: {route.total_length_km} KM",
                        'width': max(2, min(8, int(route.total_cores / 4))),
                        'color': {'color': '#0d6efd', 'highlight': '#ffc107'},
                        'arrows': 'to;from',
                        'route_id': route.pk,
                    })

        return JsonResponse({
            'nodes': list(nodes.values()),
            'edges': edges,
            'summary': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'total_routes': routes.count(),
            }
        })


class FiberRouteCoreAvailabilityAPI(View):
    """
    API endpoint returning core availability and existing allocations for a fiber route.
    Used by the Drop Point form dynamic core selection widget.
    Query parameters:
      - route_id: Primary key of FiberRoute
      - drop_point_id: Optional PK of current FiberDropPoint (to exclude its own allocated cores when editing)
    """
    def get(self, request):
        route_id = request.GET.get('route_id')
        current_dp_id = request.GET.get('drop_point_id')

        if not route_id:
            return JsonResponse({'error': 'route_id is required'}, status=400)

        route = get_object_or_404(FiberRoute, pk=route_id)
        total_cores = route.total_cores

        # Find other drop points for this route
        drop_points = FiberDropPoint.objects.filter(fiber_route=route)
        if current_dp_id:
            drop_points = drop_points.exclude(pk=current_dp_id)

        allocated_cores = {}
        for dp in drop_points:
            for c in dp.parsed_dropped_cores:
                allocated_cores[c] = {
                    'point_id': dp.pk,
                    'point_name': dp.site_display,
                    'point_type': dp.get_point_type_display(),
                }

        # Current drop point's own cores (if editing)
        current_cores = []
        if current_dp_id:
            curr_dp = FiberDropPoint.objects.filter(pk=current_dp_id).first()
            if curr_dp:
                current_cores = curr_dp.parsed_dropped_cores

        return JsonResponse({
            'route_id': route.pk,
            'route_name': route.name,
            'total_cores': total_cores,
            'cores': list(range(1, total_cores + 1)),
            'allocated_cores': allocated_cores,
            'current_cores': current_cores,
        })

