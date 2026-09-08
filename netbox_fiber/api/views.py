from netbox.api.viewsets import NetBoxModelViewSet
from ..models import FiberVendor, FiberRoute, FiberDropPoint
from ..filtersets import FiberVendorFilterSet, FiberRouteFilterSet, FiberDropPointFilterSet
from .serializers import FiberVendorSerializer, FiberRouteSerializer, FiberDropPointSerializer


class FiberVendorViewSet(NetBoxModelViewSet):
    queryset = FiberVendor.objects.all()
    serializer_class = FiberVendorSerializer
    filterset_class = FiberVendorFilterSet


class FiberRouteViewSet(NetBoxModelViewSet):
    queryset = FiberRoute.objects.all().prefetch_related('drop_points')
    serializer_class = FiberRouteSerializer
    filterset_class = FiberRouteFilterSet


class FiberDropPointViewSet(NetBoxModelViewSet):
    queryset = FiberDropPoint.objects.all()
    serializer_class = FiberDropPointSerializer
    filterset_class = FiberDropPointFilterSet
