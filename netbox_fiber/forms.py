from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField, TagFilterField
from dcim.models import Site
from .models import FiberVendor, FiberRoute, FiberDropPoint, parse_core_string


class FiberVendorForm(NetBoxModelForm):
    class Meta:
        model = FiberVendor
        fields = (
            'name', 'slug', 'contact_name', 'contact_phone', 'contact_email',
            'description', 'comments', 'tags',
        )

    fieldsets = (
        ('Vendor Details', ('name', 'slug', 'tags')),
        ('Contact Information', ('contact_name', 'contact_phone', 'contact_email')),
        ('Description', ('description', 'comments')),
    )


class FiberRouteForm(NetBoxModelForm):
    vendor = DynamicModelChoiceField(
        queryset=FiberVendor.objects.all(),
        required=True,
        label='Vendor'
    )
    start_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Starting Point Site'
    )
    end_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='End Point Site'
    )

    # Optional quick-add for multiple drop points at once
    quick_drop_points = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Thameldanda, 3-4, 5.2\nAdamghat, 5-6, 10.5\nGajuri, 1-2, 14.855'
        }),
        required=False,
        label='Quick Add Multiple Drop Points',
        help_text="Format per line: Name / Site, Dropped Cores, [Optional KM Distance]. Automatically creates drop points."
    )

    class Meta:
        model = FiberRoute
        fields = (
            'name', 'vendor', 'cable_type', 'status', 'total_length_km', 'total_cores',
            'start_site', 'start_site_name', 'start_cores_dropped',
            'end_site', 'end_site_name', 'end_cores_dropped',
            'description', 'comments', 'tags',
        )

    fieldsets = (
        ('General Route Information', (
            'name', 'vendor', 'cable_type', 'status', 'tags'
        )),
        ('Cable Capacity & Distance', (
            'total_length_km', 'total_cores'
        )),
        ('Starting Point', (
            'start_site', 'start_site_name', 'start_cores_dropped'
        )),
        ('End Point', (
            'end_site', 'end_site_name', 'end_cores_dropped'
        )),
        ('Drop Points (Quick Entry)', (
            'quick_drop_points',
        )),
        ('Additional Notes', (
            'description', 'comments'
        )),
    )

    def save(self, commit=True):
        instance = super().save(commit=commit)
        quick_dp = self.cleaned_data.get('quick_drop_points', '').strip()
        if quick_dp and commit:
            self._process_quick_drop_points(instance, quick_dp)
        return instance

    def _process_quick_drop_points(self, route, quick_dp_text):
        """
        Parses multi-line text input to create drop points along the route.
        Format: Name, Dropped Cores, [Optional Distance KM]
        """
        lines = [line.strip() for line in quick_dp_text.split('\n') if line.strip()]
        start_seq = route.drop_points.count() + 1
        for idx, line in enumerate(lines, start=start_seq):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                name = parts[0]
                dropped = parts[1]
                distance = None
                if len(parts) >= 3:
                    try:
                        distance = float(parts[2])
                    except ValueError:
                        distance = None

                # Check if matches NetBox Site by name
                site_match = Site.objects.filter(name__iexact=name).first()

                FiberDropPoint.objects.create(
                    fiber_route=route,
                    name=name,
                    site=site_match,
                    sequence=idx,
                    distance_km=distance,
                    dropped_cores=dropped
                )


class FiberDropPointForm(NetBoxModelForm):
    fiber_route = DynamicModelChoiceField(
        queryset=FiberRoute.objects.all(),
        required=True,
        label='Fiber Route'
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='NetBox Site'
    )

    class Meta:
        model = FiberDropPoint
        fields = (
            'fiber_route', 'site', 'name', 'point_type', 'sequence',
            'distance_km', 'dropped_cores', 'passed_cores',
            'description', 'comments', 'tags',
        )

    fieldsets = (
        ('Route & Location', ('fiber_route', 'site', 'name', 'point_type', 'tags')),
        ('Sequence & Position', ('sequence', 'distance_km')),
        ('Core Drop Allocation', ('dropped_cores', 'passed_cores')),
        ('Notes', ('description', 'comments')),
    )


# --- Filter Forms ---

class FiberVendorFilterForm(NetBoxModelFilterSetForm):
    model = FiberVendor
    name = forms.CharField(required=False)
    tag = TagFilterField(model)


class FiberRouteFilterForm(NetBoxModelFilterSetForm):
    model = FiberRoute
    vendor = DynamicModelChoiceField(
        queryset=FiberVendor.objects.all(),
        required=False
    )
    cable_type = forms.MultipleChoiceField(
        choices=FiberRoute.CABLE_TYPE_CHOICES,
        required=False
    )
    status = forms.MultipleChoiceField(
        choices=FiberRoute.STATUS_CHOICES,
        required=False
    )
    start_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    end_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    tag = TagFilterField(model)


class FiberDropPointFilterForm(NetBoxModelFilterSetForm):
    model = FiberDropPoint
    fiber_route = DynamicModelChoiceField(
        queryset=FiberRoute.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    point_type = forms.MultipleChoiceField(
        choices=FiberDropPoint.POINT_TYPE_CHOICES,
        required=False
    )
    tag = TagFilterField(model)
