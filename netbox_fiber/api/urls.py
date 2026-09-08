from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()
router.register('vendors', views.FiberVendorViewSet)
router.register('routes', views.FiberRouteViewSet)
router.register('drop-points', views.FiberDropPointViewSet)

urlpatterns = router.urls
