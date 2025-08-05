from rest_framework import serializers
from contacts.models import Contact, ContactProperty, Property


class ContactSerializer(serializers.ModelSerializer):
    """Completely dynamic serializer that creates fields based on display parameter"""

    class Meta:
        model = Contact
        fields = ['id', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        """Initialize serializer with dynamic fields based on display parameter"""
        super().__init__(*args, **kwargs)

        # Get display fields from request context
        request = self.context.get('request')
        display_fields = []

        if request:
            display_param = request.query_params.get('display', '')
            if display_param:
                display_fields = [
                    field.strip() for field in display_param.split(',') if field.strip()]

        # If no display fields specified, show all available properties
        if not display_fields:
            display_fields = list(
                Property.objects.values_list('slug', flat=True))

        # Create dynamic fields for each requested property
        for field_slug in display_fields:
            try:
                property_obj = Property.objects.get(slug=field_slug)
                self.fields[field_slug] = serializers.SerializerMethodField()

                # Create the dynamic method for this field
                method_name = f'get_{field_slug}'
                # Bind the method to this instance
                import types
                getter_func = self._create_property_getter(property_obj)
                setattr(self, method_name, types.MethodType(getter_func, self))

            except Property.DoesNotExist:
                # Skip non-existent properties
                continue

    def _create_property_getter(self, property_obj):
        """Create a getter method for a specific property"""

        def getter(self, obj):
            """Get the value for this property"""
            try:
                contact_property = obj.contactpropertys.get(
                    property=property_obj)

                if property_obj.type == 'singleline':
                    return contact_property.singleline_value

                elif property_obj.type == 'textarea':
                    return contact_property.richtext_value

                elif property_obj.type == 'option':
                    if contact_property.singleoption_value:
                        return {
                            'code': contact_property.singleoption_value.code,
                            'value': contact_property.singleoption_value.value,
                            'id': str(contact_property.singleoption_value.id)
                        }
                    return None

            except ContactProperty.DoesNotExist:
                return None

            return None

        return getter


class ContactPropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer for showing all properties in detail view"""
    property_name = serializers.CharField(
        source='property.name', read_only=True)
    property_slug = serializers.CharField(
        source='property.slug', read_only=True)
    property_type = serializers.CharField(
        source='property.type', read_only=True)

    class Meta:
        model = ContactProperty
        fields = [
            'property_name', 'property_slug', 'property_type',
            'singleline_value', 'richtext_value', 'singleoption_value'
        ]

    def to_representation(self, instance):
        """Return only the appropriate value based on property type"""
        data = super().to_representation(instance)

        # Only include the value that matches the property type
        if instance.property.type == 'singleline':
            value = data.get('singleline_value')
        elif instance.property.type == 'textarea':
            value = data.get('richtext_value')
        elif instance.property.type == 'option':
            if instance.singleoption_value:
                value = {
                    'code': instance.singleoption_value.code,
                    'value': instance.singleoption_value.value,
                    'id': str(instance.singleoption_value.id)
                }
            else:
                value = None
        else:
            value = None

        return {
            'property_name': data['property_name'],
            'property_slug': data['property_slug'],
            'property_type': data['property_type'],
            'value': value
        }
