from django.urls import path
from netbox.views import generic
from . import models, views

urlpatterns = [
    # Fiber Vendors
    path('vendors/', views.FiberVendorListView.as_view(), name='fibervendor_list'),
    path('vendors/add/', views.FiberVendorEditView.as_view(), name='fibervendor_add'),
    path('vendors/<int:pk>/', views.FiberVendorView.as_view(), name='fibervendor'),
    path('vendors/<int:pk>/edit/', views.FiberVendorEditView.as_view(), name='fibervendor_edit'),
    path('vendors/<int:pk>/delete/', views.FiberVendorDeleteView.as_view(), name='fibervendor_delete'),
    path('vendors/<int:pk>/changelog/', generic.ObjectChangeLogView.as_view(), name='fibervendor_changelog', kwargs={'model': models.FiberVendor}),

    # Fiber Routes
    path('routes/', views.FiberRouteListView.as_view(), name='fiberroute_list'),
    path('routes/add/', views.FiberRouteEditView.as_view(), name='fiberroute_add'),
    path('routes/<int:pk>/', views.FiberRouteView.as_view(), name='fiberroute'),
    path('routes/<int:pk>/edit/', views.FiberRouteEditView.as_view(), name='fiberroute_edit'),
    path('routes/<int:pk>/delete/', views.FiberRouteDeleteView.as_view(), name='fiberroute_delete'),
    path('routes/<int:pk>/changelog/', generic.ObjectChangeLogView.as_view(), name='fiberroute_changelog', kwargs={'model': models.FiberRoute}),

    # Fiber Drop Points
    path('drop-points/', views.FiberDropPointListView.as_view(), name='fiberdroppoint_list'),
    path('drop-points/add/', views.FiberDropPointEditView.as_view(), name='fiberdroppoint_add'),
    path('drop-points/<int:pk>/', views.FiberDropPointView.as_view(), name='fiberdroppoint'),
    path('drop-points/<int:pk>/edit/', views.FiberDropPointEditView.as_view(), name='fiberdroppoint_edit'),
    path('drop-points/<int:pk>/delete/', views.FiberDropPointDeleteView.as_view(), name='fiberdroppoint_delete'),
    path('drop-points/<int:pk>/changelog/', generic.ObjectChangeLogView.as_view(), name='fiberdroppoint_changelog', kwargs={'model': models.FiberDropPoint}),

    # Dedicated Vendor-Based Fiber Explorer Page
    path('vendor-view/', views.VendorFiberView.as_view(), name='vendor_view'),

    # Topology View
    path('topology/', views.FiberTopologyView.as_view(), name='topology_view'),
    path('api/topology-data/', views.FiberTopologyDataAPI.as_view(), name='topology_data_api'),
]
