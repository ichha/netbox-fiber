from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from ..models import FiberVendor, FiberRoute, FiberDropPoint


class FiberVendorSerializer(NetBoxModelSerializer):
    class Meta:
        model = FiberVendor
        fields = (
            'id', 'url', 'display', 'name', 'slug', 'contact_name',
            'contact_phone', 'contact_email', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated'
        )


class FiberDropPointSerializer(NetBoxModelSerializer):
    class Meta:
        model = FiberDropPoint
        fields = (
            'id', 'url', 'display', 'fiber_route', 'site', 'name',
            'point_type', 'sequence', 'distance_km', 'dropped_cores',
            'passed_cores', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated'
        )


class FiberRouteSerializer(NetBoxModelSerializer):
    drop_points = FiberDropPointSerializer(many=True, read_only=True)

    class Meta:
        model = FiberRoute
        fields = (
            'id', 'url', 'display', 'name', 'vendor', 'cable_type',
            'total_length_km', 'total_cores', 'start_site', 'start_site_name',
            'start_cores_dropped', 'end_site', 'end_site_name', 'end_cores_dropped',
            'status', 'description', 'comments', 'drop_points',
            'tags', 'custom_fields', 'created', 'last_updated'
        )
