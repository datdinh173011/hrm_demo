"""
Django admin configuration for contacts app.

This file imports all admin configurations from the admin/ directory.
Each model has its own dedicated admin file for better organization.
"""

from contacts.admin.contact import ContactAdmin
from contacts.admin.property import PropertyAdmin
from contacts.admin.option import OptionAdmin
from contacts.admin.contact_property import ContactPropertyAdmin
