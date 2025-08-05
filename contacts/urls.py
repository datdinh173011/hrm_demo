from django.urls import path
from contacts.views.contact import ContactListAPIView

app_name = 'contacts'

urlpatterns = [
    path('contacts/', ContactListAPIView.as_view(), name='contact-list')
]
