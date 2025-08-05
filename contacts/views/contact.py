import django_filters
from django.db.models import Q, Prefetch
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes

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
                    Q(
                        contactproperty__property=property_obj,
                        contactproperty__singleoption_value__code=value
                    ) | Q(
                        contactproperty__property=property_obj,
                        contactproperty__singleoption_value__value__icontains=value
                    )
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


@extend_schema_view(
    get=extend_schema(
        tags=['Contacts'],
        summary='List contacts with dynamic filtering',
        description='''
        Retrieve a paginated list of contacts with powerful dynamic filtering and display control.
        
        ## Dynamic Property Filtering
        You can filter by any contact property using URL parameters. The system automatically detects the property type and applies the appropriate filter.
        
        **Property Types:**
        - `singleline`: Text fields (first_name, last_name, email, phone_number, location)  
        - `textarea`: Long text fields (notes, descriptions)
        - `option`: Select fields (department, status, position)
        
        ## Display Control
        Use the `display` parameter to control which fields are returned in the response.
        
        ## Rate Limiting
        This endpoint is rate limited to 100 requests per 5 minutes per IP address.
        ''',
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search across all contact properties (first_name, last_name, email, phone_number, department, status, position)',
                examples=[
                    OpenApiExample('Search for John', value='john'),
                    OpenApiExample('Search for Manager', value='manager'),
                    OpenApiExample('No search', value='null'),
                ]
            ),
            OpenApiParameter(
                name='display',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Comma-separated list of property slugs to display in response',
                examples=[
                    OpenApiExample('Basic info', value='first_name,last_name,email'),
                    OpenApiExample('Work info', value='department,location,position'),
                    OpenApiExample('All fields', value='first_name,last_name,email,phone_number,location,department,status,position'),
                ]
            ),
            OpenApiParameter(
                name='first_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by first name (partial match)',
                examples=[OpenApiExample('Filter by John', value='john')]
            ),
            OpenApiParameter(
                name='last_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by last name (partial match)',
                examples=[OpenApiExample('Filter by Smith', value='smith')]
            ),
            OpenApiParameter(
                name='email',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by email address (partial match)',
                examples=[OpenApiExample('Filter by domain', value='@company.com')]
            ),
            OpenApiParameter(
                name='department',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by department code or name',
                examples=[
                    OpenApiExample('IT Department', value='it'),
                    OpenApiExample('HR Department', value='hr'),
                    OpenApiExample('Sales Department', value='sales'),
                ]
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by employee status',
                examples=[
                    OpenApiExample('Active employees', value='active'),
                    OpenApiExample('Inactive employees', value='inactive'),
                    OpenApiExample('Pending employees', value='pending'),
                ]
            ),
            OpenApiParameter(
                name='location',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by location/office',
                examples=[OpenApiExample('New York office', value='new york')]
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number for pagination',
                examples=[OpenApiExample('First page', value=1)]
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of items per page (max 100)',
                examples=[OpenApiExample('20 per page', value=20)]
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=ContactSerializer,
                description='Successfully retrieved contacts',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "count": 1500,
                            "next": "http://127.0.0.1:8000/api/v1/contacts/?page=2",
                            "previous": None,
                            "results": [
                                {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "created_at": "2023-01-15T10:30:00Z",
                                    "updated_at": "2023-01-15T10:30:00Z",
                                    "first_name": "John",
                                    "last_name": "Doe",
                                    "email": "john.doe@company.com",
                                    "department": {
                                        "code": "it",
                                        "value": "IT",
                                        "id": "456e7890-e89b-12d3-a456-426614174001"
                                    },
                                    "status": {
                                        "code": "active",
                                        "value": "ACTIVE",
                                        "id": "789e0123-e89b-12d3-a456-426614174002"
                                    }
                                }
                            ]
                        }
                    )
                ]
            ),
            429: OpenApiResponse(
                description='Rate limit exceeded',
                examples=[
                    OpenApiExample(
                        'Rate Limited',
                        value={
                            "error": "Rate limit exceeded",
                            "message": "Too many requests. Maximum 100 requests per 300 seconds.",
                            "retry_after": 180,
                            "remaining_requests": 0,
                            "limit": 100,
                            "window_seconds": 300
                        }
                    )
                ]
            )
        }
    )
)
class ContactListAPIView(generics.ListAPIView):
    """
    Dynamic contact list API that accepts any property slug as filter
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
