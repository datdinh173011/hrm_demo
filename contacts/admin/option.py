from django.contrib import admin
from django.utils.html import format_html
from contacts.models import Option


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = (
        'value', 'code', 'get_property_info', 'order', 'get_usage_count'
    )
    list_filter = ('property__type', 'property__name')
    search_fields = ('value', 'code', 'property__name', 'property__slug')
    readonly_fields = ('id', 'get_usage_count')
    list_editable = ('order',)
    ordering = ('property__name', 'order', 'value')
    
    fieldsets = (
        ('Option Information', {
            'fields': ('property', 'code', 'value', 'order')
        }),
        ('System Information', {
            'fields': ('id', 'get_usage_count'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property')

    def get_property_info(self, obj):
        """Display property information with type badge"""
        if obj.property:
            return format_html(
                '<strong>{}</strong><br><small style="color: #666;">Slug: {}</small>',
                obj.property.name,
                obj.property.slug
            )
        return "No Property"
    get_property_info.short_description = 'Property'
    get_property_info.admin_order_field = 'property__name'

    def get_usage_count(self, obj):
        """Display how many times this option is used"""
        try:
            # Count usage in ContactProperty singleoption_value
            from contacts.models import ContactProperty
            count = ContactProperty.objects.filter(singleoption_value=obj).count()
            
            if count > 0:
                return format_html(
                    '<span style="color: #2196F3; font-weight: bold;">{} contacts</span>',
                    count
                )
            else:
                return format_html('<span style="color: #757575;">Not used</span>')
        except Exception:
            return "N/A"
    get_usage_count.short_description = 'Usage'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter properties to only show option-type properties"""
        if db_field.name == "property":
            kwargs["queryset"] = db_field.related_model.objects.filter(type='option')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Auto-populate code from value if not provided"""
        if not obj.code and obj.value:
            import re
            obj.code = re.sub(r'[^a-zA-Z0-9_]', '_', obj.value.lower().strip())
        
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        """Allow delete only if option is not being used"""
        if obj:
            try:
                from contacts.models import ContactProperty
                usage_count = ContactProperty.objects.filter(singleoption_value=obj).count()
                return usage_count == 0
            except Exception:
                return False
        return True

    def delete_model(self, request, obj):
        """Override delete to check usage before deletion"""
        try:
            from contacts.models import ContactProperty
            usage_count = ContactProperty.objects.filter(singleoption_value=obj).count()
            if usage_count > 0:
                from django.contrib import messages
                messages.error(
                    request, 
                    f'Cannot delete option "{obj.value}" because it is used by {usage_count} contacts.'
                )
                return
        except Exception:
            pass
        
        super().delete_model(request, obj)