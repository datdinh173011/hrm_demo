from django.contrib import admin
from django.utils.html import format_html
from contacts.models import Property, Option


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0
    fields = ('code', 'value', 'order')
    ordering = ('order', 'value')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'get_type_badge', 'get_options_count', 
        'created_at', 'updated_at'
    )
    list_filter = ('type', 'created_at', 'updated_at')
    search_fields = ('name', 'slug')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [OptionInline]
    
    fieldsets = (
        ('Property Information', {
            'fields': ('name', 'slug', 'type')
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
        return super().get_queryset(request).prefetch_related('options')

    def get_type_badge(self, obj):
        """Display property type with color coding"""
        colors = {
            'singleline': '#2196F3',  # Blue
            'textarea': '#4CAF50',    # Green  
            'option': '#FF9800'       # Orange
        }
        color = colors.get(obj.type, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.type.upper()
        )
    get_type_badge.short_description = 'Type'
    get_type_badge.admin_order_field = 'type'

    def get_options_count(self, obj):
        """Display number of options for option-type properties"""
        if obj.type == 'option':
            count = obj.options.count()
            if count > 0:
                return format_html(
                    '<span style="color: #2196F3; font-weight: bold;">{} options</span>',
                    count
                )
            else:
                return format_html(
                    '<span style="color: #f44336;">No options</span>'
                )
        return format_html('<span style="color: #757575;">N/A</span>')
    get_options_count.short_description = 'Options'

    def get_inline_instances(self, request, obj=None):
        """Only show options inline for option-type properties"""
        if obj and obj.type == 'option':
            return super().get_inline_instances(request, obj)
        return []

    def save_model(self, request, obj, form, change):
        """Auto-populate slug from name if not provided"""
        if not obj.slug and obj.name:
            import re
            obj.slug = re.sub(r'[^a-zA-Z0-9_]', '_', obj.name.lower().strip())
        
        if not change:  # New object
            obj.created_by = request.user
        obj.changed_by = request.user
        
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True