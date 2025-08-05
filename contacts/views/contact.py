import django_filters
from django.db.models import Q, Prefetch
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend


from contacts.models import Contact, ContactProperty, Property
from contacts.serializers.contact import ContactSerializer


class ContactFilter(django_filters.FilterSet):
    """Dynamic filter that accepts any property slug as a filter parameter"""
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Contact
        fields = ['search']

    def filter_queryset(self, queryset):
        """Custom filter method that handles dynamic property filtering"""
        # First apply the standard filters
        queryset = super().filter_queryset(queryset)

        # Then apply custom property filters
        for param, value in self.request.GET.items():
            if param not in ['search', 'page', 'page_size', 'display'] and value and value.lower() != 'null':
                queryset = self._filter_by_property_slug(
                    queryset, param, value)

        return queryset

    def _filter_by_property_slug(self, queryset, slug, value):
        """Filter by any property slug"""
        try:
            property_obj = Property.objects.get(slug=slug)

            if property_obj.type == 'singleline':
                return queryset.filter(
                    contactproperty__property=property_obj,
                    contactproperty__singleline_value__icontains=value
                ).distinct()

            elif property_obj.type == 'textarea':
                return queryset.filter(
                    contactproperty__property=property_obj,
                    contactproperty__richtext_value__icontains=value
                ).distinct()

            elif property_obj.type == 'option':
                return queryset.filter(
                    Q(contactproperty__property=property_obj,
                      contactproperty__singleoption_value__code=value) |
                    Q(contactproperty__property=property_obj,
                      contactproperty__singleoption_value__value__icontains=value)
                ).distinct()

        except Property.DoesNotExist:
            pass

        return queryset

    def filter_search(self, queryset, name, value):
        """Search across all property values"""
        if not value or value.lower() == 'null':
            return queryset

        search_query = Q()

        # Search in all singleline properties
        search_query |= Q(
            contactproperty__property__type='singleline',
            contactproperty__singleline_value__icontains=value
        )

        # Search in all textarea properties
        search_query |= Q(
            contactproperty__property__type='textarea',
            contactproperty__richtext_value__icontains=value
        )

        # Search in all option properties
        search_query |= Q(
            contactproperty__property__type='option',
            contactproperty__singleoption_value__value__icontains=value
        )

        return queryset.filter(search_query).distinct()


class ContactPagination(PageNumberPagination):
    """Custom pagination for contacts"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ContactListAPIView(generics.ListAPIView):
    """
    Dynamic contact list API that accepts any property slug as filter

    Query Parameters:
    - search: Search across all property values
    - display: Comma-separated list of property slugs to display
    - {any_property_slug}: Filter by any property slug (e.g., first_name=john, department=it)
    - page: Page number for pagination
    - page_size: Number of items per page (max 100)

    Examples:
    - /api/v1/contacts/?first_name=john&department=it&display=first_name,last_name,email
    - /api/v1/contacts/?location=new york&status=active&display=department,location,position
    """
    serializer_class = ContactSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContactFilter
    pagination_class = ContactPagination

    def get_queryset(self):
        """Optimized queryset with prefetch for better performance"""
        return Contact.objects.prefetch_related(
            Prefetch(
                'contactpropertys',
                queryset=ContactProperty.objects.select_related(
                    'property', 'singleoption_value'
                )
            )
        ).distinct()

    def get_serializer_context(self):
        """Add request context to serializer for dynamic field handling"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        """Custom list method with enhanced metadata"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data)
            return response_data

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
        })
