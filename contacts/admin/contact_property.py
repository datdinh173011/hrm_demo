from django.contrib import admin
from django.utils.html import format_html
from contacts.models import ContactProperty


@admin.register(ContactProperty)
class ContactPropertyAdmin(admin.ModelAdmin):
    list_display = (
        'get_contact_info', 'get_property_info', 'get_value_display', 
        'created_at', 'updated_at'
    )
    list_filter = (
        'property__type', 'property__name', 'created_at', 'updated_at'
    )
    search_fields = (
        'contact__id', 'property__name', 'property__slug',
        'singleline_value', 'richtext_value'
    )
    readonly_fields = ('id', 'created_at', 'updated_at')
    raw_id_fields = ('contact', 'singleoption_value')
    
    fieldsets = (
        ('Relationship', {
            'fields': ('contact', 'property')
        }),
        ('Property Values', {
            'fields': (
                'singleline_value', 'richtext_value', 'singleoption_value'
            ),
            'description': 'Only fill the field that matches the property type'
        }),
        ('Meta Information', {
            'fields': ('slug', 'variant'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('id', 'created_by', 'changed_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'contact', 'property', 'singleoption_value', 'created_by', 'changed_by'
        )

    def get_contact_info(self, obj):
        """Display contact information"""
        if obj.contact:
            # Try to get contact name from other properties
            try:
                contact_properties = ContactProperty.objects.filter(
                    contact=obj.contact
                ).select_related('property', 'singleoption_value')
                
                first_name = None
                last_name = None
                
                for cp in contact_properties:
                    if cp.property.slug == 'first_name' and cp.singleline_value:
                        first_name = cp.singleline_value
                    elif cp.property.slug == 'last_name' and cp.singleline_value:
                        last_name = cp.singleline_value
                
                if first_name or last_name:
                    name = f"{first_name or ''} {last_name or ''}".strip()
                    return format_html(
                        '<strong>{}</strong><br><small style="color: #666;">ID: {}</small>',
                        name, str(obj.contact.id)[:8]
                    )
            except Exception:
                pass
            
            return format_html(
                '<strong>Contact</strong><br><small style="color: #666;">ID: {}</small>',
                str(obj.contact.id)[:8]
            )
        return "No Contact"
    get_contact_info.short_description = 'Contact'
    get_contact_info.admin_order_field = 'contact'

    def get_property_info(self, obj):
        """Display property information with type badge"""
        if obj.property:
            colors = {
                'singleline': '#2196F3',
                'textarea': '#4CAF50',
                'option': '#FF9800'
            }
            color = colors.get(obj.property.type, '#757575')
            
            return format_html(
                '<strong>{}</strong><br>'
                '<span style="background-color: {}; color: white; padding: 2px 6px; '
                'border-radius: 2px; font-size: 10px;">{}</span>',
                obj.property.name, color, obj.property.type.upper()
            )
        return "No Property"
    get_property_info.short_description = 'Property'
    get_property_info.admin_order_field = 'property__name'

    def get_value_display(self, obj):
        """Display the actual value based on property type"""
        if not obj.property:
            return "No Property"
        
        if obj.property.type == 'singleline' and obj.singleline_value:
            value = obj.singleline_value
            if len(value) > 50:
                value = value[:47] + "..."
            return format_html('<span style="color: #2196F3;">{}</span>', value)
        
        elif obj.property.type == 'textarea' and obj.richtext_value:
            value = obj.richtext_value
            if len(value) > 100:
                value = value[:97] + "..."
            return format_html('<span style="color: #4CAF50;">{}</span>', value)
        
        elif obj.property.type == 'option' and obj.singleoption_value:
            return format_html(
                '<span style="color: #FF9800; font-weight: bold;">{}</span>',
                obj.singleoption_value.value
            )
        
        return format_html('<span style="color: #f44336;">No Value</span>')
    get_value_display.short_description = 'Value'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize foreign key fields"""
        if db_field.name == "singleoption_value":
            # Only show options that belong to option-type properties
            kwargs["queryset"] = db_field.related_model.objects.select_related(
                'property'
            ).filter(property__type='option')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Auto-populate audit fields and validate data"""
        if not change:  # New object
            obj.created_by = request.user
        obj.changed_by = request.user
        
        # Clear inappropriate value fields based on property type
        if obj.property:
            if obj.property.type != 'singleline':
                obj.singleline_value = None
            if obj.property.type != 'textarea':
                obj.richtext_value = None
            if obj.property.type != 'option':
                obj.singleoption_value = None
        
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True