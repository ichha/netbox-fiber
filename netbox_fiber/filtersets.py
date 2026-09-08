from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from .models import FiberVendor, FiberRoute, FiberDropPoint


class FiberVendorFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = FiberVendor
        fields = ('id', 'name', 'slug')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(contact_name__icontains=value) |
            Q(description__icontains=value)
        )


class FiberRouteFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = FiberRoute
        fields = (
            'id', 'name', 'vendor_id', 'cable_type', 'status',
            'start_site_id', 'end_site_id'
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(vendor__name__icontains=value) |
            Q(start_site_name__icontains=value) |
            Q(end_site_name__icontains=value) |
            Q(description__icontains=value)
        )


class FiberDropPointFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = FiberDropPoint
        fields = ('id', 'name', 'fiber_route_id', 'site_id', 'point_type')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(fiber_route__name__icontains=value) |
            Q(dropped_cores__icontains=value) |
            Q(description__icontains=value)
        )
