import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from .models import FiberVendor, FiberRoute, FiberDropPoint


class FiberVendorFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )

    class Meta:
        model = FiberVendor
        fields = ('id', 'name', 'slug')

    def search(self, queryset, name, value):
        if not value or not value.strip():
            return queryset
        val = value.strip()
        return queryset.filter(
            Q(name__icontains=val) |
            Q(contact_name__icontains=val) |
            Q(description__icontains=val)
        )


class FiberRouteFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )

    class Meta:
        model = FiberRoute
        fields = (
            'id', 'name', 'vendor_id', 'cable_type', 'status',
            'start_site_id', 'end_site_id'
        )

    def search(self, queryset, name, value):
        if not value or not value.strip():
            return queryset
        val = value.strip()
        return queryset.filter(
            Q(name__icontains=val) |
            Q(start_site__name__icontains=val) |
            Q(start_site_name__icontains=val) |
            Q(end_site__name__icontains=val) |
            Q(end_site_name__icontains=val) |
            Q(drop_points__name__icontains=val) |
            Q(drop_points__site__name__icontains=val) |
            Q(vendor__name__icontains=val) |
            Q(description__icontains=val)
        ).distinct()


class FiberDropPointFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )

    class Meta:
        model = FiberDropPoint
        fields = ('id', 'name', 'fiber_route_id', 'site_id', 'point_type')

    def search(self, queryset, name, value):
        if not value or not value.strip():
            return queryset
        val = value.strip()
        return queryset.filter(
            Q(name__icontains=val) |
            Q(site__name__icontains=val) |
            Q(fiber_route__name__icontains=val) |
            Q(description__icontains=val)
        )
