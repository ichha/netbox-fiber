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
        help_text='Designate whether this is a Starting Point, Intermediate Drop, or End Point'
    )
    dropped_cores = forms.CharField(
        max_length=255,
        required=False,
        label='Dropped Cores',
        help_text="Cores dropped / spliced at this point (e.g. '3, 4' or '3-4')"
    )

    class Meta:
        model = FiberDropPoint
        fields = (
            'fiber_route', 'site', 'name', 'point_type', 'sequence',
            'distance_km', 'dropped_cores', 'passed_cores',
            'description', 'comments', 'tags',
        )

    if FieldSet:
        fieldsets = (
            FieldSet('fiber_route', 'site', 'name', 'point_type', 'tags', name='Route & Location'),
            FieldSet('sequence', 'distance_km', name='Sequence & Position'),
            FieldSet('dropped_cores', 'passed_cores', name='Core Drop Allocation'),
            FieldSet('description', 'comments', name='Notes'),
        )

    def clean(self):
        super().clean()
        cleaned_data = getattr(self, 'cleaned_data', None)
        if not cleaned_data:
            return self.cleaned_data

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

        if fiber_route and dropped_cores_str:
            selected_cores = parse_core_string(dropped_cores_str)
            total_cores = fiber_route.total_cores

            # Check valid core bounds
            invalid_cores = [c for c in selected_cores if c < 1 or c > total_cores]
            if invalid_cores:
                self.add_error(
                    'dropped_cores',
                    f"Selected core(s) {invalid_cores} are out of bounds. Route '{fiber_route.name}' only has {total_cores} cores."
                )

            # Check conflicts only against other consuming drop points (Intermediate Drop and End Point)
            # Starting Point originates cores and does not conflict with downstream drops
            if point_type in ['drop', 'end']:
                other_consuming = FiberDropPoint.objects.filter(
                    fiber_route=fiber_route,
                    point_type__in=['drop', 'end']
                )
                if self.instance and self.instance.pk:
                    other_consuming = other_consuming.exclude(pk=self.instance.pk)

                for other in other_consuming:
                    other_cores = set(other.parsed_dropped_cores)
                    conflicts = [c for c in selected_cores if c in other_cores]
                    if conflicts:
                        conflict_str = ", ".join(f"Core {c}" for c in conflicts)
                        self.add_error(
                            'dropped_cores',
                            f"{conflict_str} is already dropped at '{other.site_display}' ({other.get_point_type_display()}). Each core can only be dropped once along the route."
                        )
                        break

        # Validate passed cores
        passed_cores_str = cleaned_data.get('passed_cores')

        if point_type == 'end':
            # End points do not have outgoing passed cores
            cleaned_data['passed_cores'] = ''
        elif fiber_route and dropped_cores_str and passed_cores_str and point_type != 'start':
            selected_drops = set(parse_core_string(dropped_cores_str))
            selected_passes = set(parse_core_string(passed_cores_str))
            overlap = selected_drops.intersection(selected_passes)
            if overlap:
                overlap_str = ", ".join(f"Core {c}" for c in sorted(list(overlap)))
                self.add_error(
                    'passed_cores',
                    f"{overlap_str} cannot be both Dropped and Passed through at this point."
                )

        return self.cleaned_data


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
