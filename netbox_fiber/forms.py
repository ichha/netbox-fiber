from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField, TagFilterField, SlugField
from dcim.models import Site
from .models import FiberVendor, FiberRoute, FiberDropPoint, parse_core_string

try:
    from utilities.forms.rendering import FieldSet
except ImportError:
    try:
        from utilities.forms import FieldSet
    except ImportError:
        FieldSet = None


class FiberVendorForm(NetBoxModelForm):
    slug = SlugField(slug_source='name')

    class Meta:
        model = FiberVendor
        fields = (
            'name', 'slug', 'contact_name', 'contact_phone', 'contact_email',
            'description', 'comments', 'tags',
        )

    if FieldSet:
        fieldsets = (
            FieldSet('name', 'slug', 'tags', name='Vendor Details'),
            FieldSet('contact_name', 'contact_phone', 'contact_email', name='Contact Information'),
            FieldSet('description', name='Description'),
        )


class FiberRouteForm(NetBoxModelForm):
    vendor = DynamicModelChoiceField(
        queryset=FiberVendor.objects.all(),
        required=True,
        label='Vendor'
    )
    class Meta:
        model = FiberRoute
        fields = (
            'name', 'vendor', 'cable_type', 'status', 'total_length_km', 'total_cores',
            'description', 'comments', 'tags',
        )

    if FieldSet:
        fieldsets = (
            FieldSet('name', 'vendor', 'cable_type', 'status', 'tags', name='General Route Information'),
            FieldSet('total_length_km', 'total_cores', name='Cable Capacity & Distance'),
            FieldSet('description', 'comments', name='Additional Notes'),
        )


try:
    from netbox.forms import NetBoxModelImportForm
except ImportError:
    try:
        from netbox.forms import NetBoxModelCSVForm as NetBoxModelImportForm
    except ImportError:
        from utilities.forms import CSVModelForm as NetBoxModelImportForm


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
    point_type = forms.ChoiceField(
        choices=FiberDropPoint.POINT_TYPE_CHOICES,
        initial='drop',
        required=True,
        label='Point Type',
        help_text='Designate whether this is a Starting Point, Intermediate Station/Joint, or End Point'
    )

    class Meta:
        model = FiberDropPoint
        fields = (
            'fiber_route', 'site', 'name', 'point_type',
            'distance_km', 'description', 'comments', 'tags',
        )

    if FieldSet:
        fieldsets = (
            FieldSet('fiber_route', 'site', 'name', 'point_type', 'tags', name='Route & Location'),
            FieldSet('distance_km', name='Position'),
            FieldSet('description', 'comments', name='Notes'),
        )

    def clean(self):
        super().clean()
        cleaned_data = getattr(self, 'cleaned_data', None)
        if not cleaned_data:
            return self.cleaned_data

        fiber_route = cleaned_data.get('fiber_route')
        point_type = cleaned_data.get('point_type')

        # Check uniqueness of Starting and End points on the route
        if fiber_route and point_type in ['start', 'end']:
            existing_same_type = FiberDropPoint.objects.filter(
                fiber_route=fiber_route,
                point_type=point_type
            )
            if self.instance and self.instance.pk:
                existing_same_type = existing_same_type.exclude(pk=self.instance.pk)
            if existing_same_type.exists():
                role_label = 'Starting Point' if point_type == 'start' else 'End Point'
                self.add_error(
                    'point_type',
                    f"Route '{fiber_route.name}' already has a {role_label} ('{existing_same_type.first().site_display}'). Each route can only have one {role_label}."
                )

        return self.cleaned_data


# --- Bulk Import Forms ---

class FiberVendorImportForm(NetBoxModelImportForm):
    class Meta:
        model = FiberVendor
        fields = ('name', 'slug', 'contact_name', 'contact_phone', 'contact_email', 'description', 'comments')


class FiberRouteImportForm(NetBoxModelImportForm):
    vendor = forms.ModelChoiceField(
        queryset=FiberVendor.objects.all(),
        to_field_name='name',
        required=True,
        help_text='Vendor Name'
    )
    start_site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Starting NetBox Site Name (optional)'
    )
    end_site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Ending NetBox Site Name (optional)'
    )
    cable_type = forms.CharField(
        required=False,
        initial='adss',
        help_text='Cable installation type (e.g. adss, underground, aerial, armored)'
    )
    status = forms.CharField(
        required=False,
        initial='active',
        help_text='Route status (e.g. active, planned, maintenance)'
    )

    class Meta:
        model = FiberRoute
        fields = (
            'name', 'vendor', 'start_site', 'start_site_name',
            'end_site', 'end_site_name', 'cable_type', 'status',
            'total_length_km', 'total_cores', 'description', 'comments'
        )

    def clean_cable_type(self):
        val = str(self.cleaned_data.get('cable_type') or 'adss').strip().lower()
        mapping = {
            'adss': 'adss',
            'adss (all-dielectric self-supporting)': 'adss',
            'underground': 'underground',
            'underground / duct': 'underground',
            'duct': 'underground',
            'armored': 'armored',
            'direct buried / armored': 'armored',
            'buried': 'armored',
            'aerial': 'aerial',
            'aerial / figure-8': 'aerial',
            'figure-8': 'aerial',
            'figure 8': 'aerial',
            'submarine': 'submarine',
            'submarine / underwater': 'submarine',
            'underwater': 'submarine',
            'indoor': 'indoor',
            'indoor / riser': 'indoor',
            'riser': 'indoor',
            'other': 'other',
        }
        for k, v in mapping.items():
            if val == k or val.startswith(k):
                return v
        valid_keys = [c[0] for c in FiberRoute.CABLE_TYPE_CHOICES]
        if val in valid_keys:
            return val
        raise forms.ValidationError(f"Invalid cable_type '{val}'. Valid choices are: {', '.join(valid_keys)}")

    def clean_status(self):
        val = str(self.cleaned_data.get('status') or 'active').strip().lower()
        mapping = {
            'active': 'active',
            'planned': 'planned',
            'maintenance': 'maintenance',
            'under maintenance': 'maintenance',
            'decommissioned': 'decommissioned',
            'damaged': 'damaged',
            'damaged / cut': 'damaged',
            'cut': 'damaged',
        }
        for k, v in mapping.items():
            if val == k or val.startswith(k):
                return v
        valid_keys = [s[0] for s in FiberRoute.STATUS_CHOICES]
        if val in valid_keys:
            return val
        raise forms.ValidationError(f"Invalid status '{val}'. Valid choices are: {', '.join(valid_keys)}")


class FiberDropPointImportForm(NetBoxModelImportForm):
    fiber_route = forms.ModelChoiceField(
        queryset=FiberRoute.objects.all(),
        to_field_name='name',
        required=True,
        help_text='Route Name'
    )
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        required=False,
        help_text='NetBox Site Name (optional)'
    )
    point_type = forms.CharField(
        required=False,
        initial='drop',
        help_text='Point type (intermediate, drop, start, end)'
    )

    class Meta:
        model = FiberDropPoint
        fields = ('fiber_route', 'site', 'name', 'point_type', 'distance_km', 'description', 'comments')

    def clean_point_type(self):
        val = str(self.cleaned_data.get('point_type') or 'drop').strip().lower()
        mapping = {
            'drop': 'drop',
            'intermediate': 'drop',
            'intermediate drop point': 'drop',
            'start': 'start',
            'starting point': 'start',
            'end': 'end',
            'end point': 'end',
        }
        for k, v in mapping.items():
            if val == k or val.startswith(k):
                return v
        return 'drop'


# --- Filter Forms ---

class FiberVendorFilterForm(NetBoxModelFilterSetForm):
    model = FiberVendor
    name = forms.CharField(required=False)
    tag = TagFilterField(model)


class FiberRouteFilterForm(NetBoxModelFilterSetForm):
    model = FiberRoute
    q = forms.CharField(
        required=False,
        label='Search'
    )
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
