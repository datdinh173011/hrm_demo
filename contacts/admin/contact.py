from django.contrib import admin
from django.utils.html import format_html
from contacts.models import Contact, ContactProperty


class ContactPropertyInline(admin.TabularInline):
    model = ContactProperty
    extra = 0
    readonly_fields = ('id', 'created_at', 'updated_at')
    fields = (
        'property', 'singleline_value', 'richtext_value', 
        'singleoption_value', 'created_at', 'updated_at'
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'property', 'singleoption_value'
        )


@admin.register(Contact)  
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_full_name', 'get_email', 'get_department', 
        'get_status', 'created_at', 'updated_at'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('id',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [ContactPropertyInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'created_by', 'changed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'contactpropertys__property',
            'contactpropertys__singleoption_value'
        )

    def get_full_name(self, obj):
        """Get contact's full name from properties"""
        first_name = self._get_property_value(obj, 'first_name')
        last_name = self._get_property_value(obj, 'last_name')
        
        if first_name and last_name:
            return f"{first_name} {last_name}"
        elif first_name:
            return first_name
        elif last_name:
            return last_name
        return "N/A"
    get_full_name.short_description = 'Full Name'

    def get_email(self, obj):
        """Get contact's email from properties"""
        email = self._get_property_value(obj, 'email')
        if email:
            return format_html('<a href="mailto:{}">{}</a>', email, email)
        return "N/A"
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'contactpropertys__singleline_value'

    def get_department(self, obj):
        """Get contact's department from properties"""
        department = self._get_property_value(obj, 'department', is_option=True)
        return department or "N/A"
    get_department.short_description = 'Department'

    def get_status(self, obj):
        """Get contact's status from properties"""
        status = self._get_property_value(obj, 'status', is_option=True)
        if status:
            color = {
                'ACTIVE': 'green',
                'INACTIVE': 'red', 
                'PENDING': 'orange'
            }.get(status, 'black')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, status
            )
        return "N/A"
    get_status.short_description = 'Status'

    def _get_property_value(self, obj, slug, is_option=False):
        """Helper to get property value by slug"""
        for contact_property in obj.contactpropertys.all():
            if contact_property.property.slug == slug:
                if is_option and contact_property.singleoption_value:
                    return contact_property.singleoption_value.value
                elif not is_option and contact_property.singleline_value:
                    return contact_property.singleline_value
        return None

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True