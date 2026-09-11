from decimal import Decimal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from netbox.views import generic

from .models import FiberVendor, FiberRoute, FiberDropPoint
from .forms import (
    FiberVendorForm, FiberVendorFilterForm, FiberVendorImportForm,
    FiberRouteForm, FiberRouteFilterForm, FiberRouteImportForm,
    FiberDropPointForm, FiberDropPointFilterForm, FiberDropPointImportForm
)
from .tables import FiberVendorTable, FiberRouteTable, FiberDropPointTable
from .filtersets import FiberVendorFilterSet, FiberRouteFilterSet, FiberDropPointFilterSet


def get_paginated_data(queryset, request, default_per_page=25):
    """
    Helper function to paginate querysets consistently with NetBox standards.
    Supports user-specified per_page (10, 25, 50, 100, 250, 500) and page numbers.
    """
    try:
        per_page = int(request.GET.get('per_page', default_per_page))
        if per_page not in [10, 25, 50, 100, 250, 500]:
            per_page = default_per_page
    except (ValueError, TypeError):
        per_page = default_per_page

    paginator = Paginator(queryset, per_page)
    page_num = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj, paginator, per_page


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
        try:
            context = super().get_extra_context(request, instance)
        except (AttributeError, TypeError):
            context = {}

        routes = instance.fiber_routes.all()
        total_km = routes.aggregate(total=Sum('total_length_km'))['total'] or Decimal('0.000')
        total_cores = routes.aggregate(total=Sum('total_cores'))['total'] or 0
        route_table = FiberRouteTable(routes)
        route_table.configure(request)

        context.update({
            'routes': routes,
            'total_km': total_km,
            'total_cores': total_cores,
            'route_table': route_table,
        })
        return context


class FiberVendorEditView(generic.ObjectEditView):
    queryset = FiberVendor.objects.all()
    form = FiberVendorForm


class FiberVendorDeleteView(generic.ObjectDeleteView):
    queryset = FiberVendor.objects.all()


class FiberVendorBulkImportView(generic.BulkImportView):
    queryset = FiberVendor.objects.all()
    model_form = FiberVendorImportForm


# =====================================================================
# Fiber Route Views
# =====================================================================

class FiberRouteListView(generic.ObjectListView):
    queryset = FiberRoute.objects.all().select_related('vendor', 'start_site', 'end_site').prefetch_related('drop_points')
    table = FiberRouteTable
    filterset = FiberRouteFilterSet
    filterset_form = FiberRouteFilterForm
    template_name = 'netbox_fiber/fiberroute_list.html'

    def get_extra_context(self, request):
        try:
            context = super().get_extra_context(request)
        except (AttributeError, TypeError):
            context = {}

        qs = self.queryset.all()
        if self.filterset:
            try:
                filter_obj = self.filterset(request.GET, queryset=qs)
                if filter_obj.is_valid():
                    qs = filter_obj.qs
            except Exception:
                qs = self.queryset.all()

        page_obj, paginator, per_page = get_paginated_data(qs, request)

        route_cards = []
        for r in page_obj.object_list:
            ordered_dp = list(r.get_ordered_drop_points())
            route_cards.append({
                'route': r,
                'drop_points': ordered_dp,
            })

        context.update({
            'route_cards': route_cards,
            'page_obj': page_obj,
            'paginator': paginator,
            'per_page': per_page,
            'search_query': request.GET.get('q', '').strip(),
        })
        return context


class FiberRouteView(generic.ObjectView):
    queryset = FiberRoute.objects.all().select_related('vendor', 'start_site', 'end_site').prefetch_related('drop_points')
    template_name = 'netbox_fiber/fiberroute.html'

    def get_extra_context(self, request, instance):
        try:
            context = super().get_extra_context(request, instance)
        except (AttributeError, TypeError):
            context = {}

        drop_points = list(instance.get_ordered_drop_points())
        all_points = list(instance.get_all_points())
        drop_points_table = FiberDropPointTable(all_points)
        drop_points_table.configure(request)

        context.update({
            'drop_points': drop_points,
            'all_points': all_points,
            'drop_points_table': drop_points_table,
        })
        return context


class FiberRouteEditView(generic.ObjectEditView):
    queryset = FiberRoute.objects.all()
    form = FiberRouteForm


class FiberRouteDeleteView(generic.ObjectDeleteView):
    queryset = FiberRoute.objects.all()


class FiberRouteBulkImportView(generic.BulkImportView):
    queryset = FiberRoute.objects.all()
    model_form = FiberRouteImportForm


# =====================================================================
# Fiber Drop Point (Route Station / Joint) Views
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


class FiberDropPointEditView(generic.ObjectEditView):
    queryset = FiberDropPoint.objects.all()
    form = FiberDropPointForm


class FiberDropPointDeleteView(generic.ObjectDeleteView):
    queryset = FiberDropPoint.objects.all()


class FiberDropPointBulkImportView(generic.BulkImportView):
    queryset = FiberDropPoint.objects.all()
    model_form = FiberDropPointImportForm


# =====================================================================
# Dedicated Vendor View (Vendor Fiber Explorer)
# =====================================================================

class VendorFiberView(View):
    """
    Dedicated view allowing users to select a vendor from a dropdown and view
    all associated fiber routes, search by route/site name, and paginate results.
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
            all_vendor_routes = selected_vendor.fiber_routes.all()
            total_km = all_vendor_routes.aggregate(total=Sum('total_length_km'))['total'] or Decimal('0.000')
            total_cores = all_vendor_routes.aggregate(total=Sum('total_cores'))['total'] or 0
            total_drop_points = FiberDropPoint.objects.filter(fiber_route__in=all_vendor_routes).count()

        # Search within vendor routes
        search_query = request.GET.get('q', '').strip()
        if search_query and routes.exists():
            routes = routes.filter(
                Q(name__icontains=search_query) |
                Q(start_site__name__icontains=search_query) |
                Q(start_site_name__icontains=search_query) |
                Q(end_site__name__icontains=search_query) |
                Q(end_site_name__icontains=search_query) |
                Q(drop_points__name__icontains=search_query) |
                Q(drop_points__site__name__icontains=search_query) |
                Q(description__icontains=search_query)
            ).distinct()

        # Pagination for vendor explorer
        page_obj, paginator, per_page = get_paginated_data(routes, request)

        route_cards = []
        for r in page_obj.object_list:
            ordered_dp = list(r.get_ordered_drop_points())
            route_cards.append({
                'route': r,
                'drop_points': ordered_dp,
            })

        context = {
            'vendors': vendors,
            'selected_vendor': selected_vendor,
            'routes': routes,
            'route_cards': route_cards,
            'page_obj': page_obj,
            'paginator': paginator,
            'per_page': per_page,
            'search_query': search_query,
            'total_km': total_km,
            'total_cores': total_cores,
            'total_drop_points': total_drop_points,
            'total_routes': selected_vendor.fiber_routes.count() if selected_vendor else 0,
        }
        return render(request, 'netbox_fiber/vendor_view.html', context)
