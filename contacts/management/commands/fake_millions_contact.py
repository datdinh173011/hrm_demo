import random
import string
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from contacts.models import Contact, Property, Option, ContactProperty
from faker import Faker

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Generate millions of fake contacts with properties'

    def add_arguments(self, parser):
        parser.add_argument(
            'count',
            type=int,
            help='Number of contacts to create (e.g., 1000000 for 1 million)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to create in each batch (default: 100)'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing contacts before creating new ones'
        )

    def handle(self, *args, **options):
        count = options['count']
        batch_size = options['batch_size']

        if options['reset']:
            self.stdout.write(self.style.WARNING(
                'Deleting existing contacts...'))
            ContactProperty.objects.all().delete()
            Contact.objects.all().delete()

        # Get or create a user for audit fields
        user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@example.com',
                'first_name': 'System',
                'last_name': 'User'
            }
        )

        # Get all properties and their options
        properties = list(Property.objects.all())
        if not properties:
            self.stdout.write(
                self.style.ERROR(
                    'No properties found. Please run "python manage.py initproperty" first.'
                )
            )
            return

        # Cache options for option-type properties
        property_options = {}
        for prop in properties:
            if prop.type == 'option':
                property_options[prop.id] = list(prop.options.all())

        self.stdout.write(f'Starting to create {count:,} fake contacts...')

        created_contacts = 0
        created_properties = 0

        # Process in batches
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            current_batch_size = batch_end - batch_start

            try:
                with transaction.atomic():
                    # Create contacts in bulk
                    contacts_to_create = []
                    for i in range(current_batch_size):
                        contact = Contact(
                            created_by=user,
                            changed_by=user
                        )
                        contacts_to_create.append(contact)

                    # Bulk create contacts
                    contacts = Contact.objects.bulk_create(contacts_to_create)
                    created_contacts += len(contacts)

                    # Create contact properties in smaller chunks
                    contact_properties_to_create = []

                    for contact in contacts:
                        # Create properties for each contact
                        for prop in properties:
                            contact_prop = ContactProperty(
                                contact=contact,
                                property=prop,
                                created_by=user,
                                changed_by=user
                            )

                            # Generate fake data based on property type and slug
                            if prop.type == 'singleline':
                                contact_prop.singleline_value = self._generate_singleline_value(
                                    prop.slug)
                            elif prop.type == 'textarea':
                                contact_prop.richtext_value = fake.text(
                                    max_nb_chars=500)
                            elif prop.type == 'option' and prop.id in property_options:
                                options = property_options[prop.id]
                                if options:
                                    contact_prop.singleoption_value = random.choice(
                                        options)

                            contact_properties_to_create.append(contact_prop)

                    # Bulk create contact properties
                    ContactProperty.objects.bulk_create(
                        contact_properties_to_create, batch_size=500)
                    created_properties += len(contact_properties_to_create)
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error in batch {batch_start//batch_size + 1}: {e}')
                )
                continue

            # Progress update
            progress = (batch_end / count) * 100
            self.stdout.write(
                f'Progress: {batch_end:,}/{count:,} contacts ({progress:.1f}%) - '
                f'Batch {batch_start//batch_size + 1} completed'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_contacts:,} contacts with '
                f'{created_properties:,} properties'
            )
        )

    def _generate_singleline_value(self, slug):
        """Generate appropriate fake data based on property slug"""
        if slug == 'first_name':
            return fake.first_name()
        elif slug == 'last_name':
            return fake.last_name()
        elif slug == 'email':
            return fake.email()
        elif slug == 'phone_number':
            return fake.phone_number()
        elif slug == 'location':
            return fake.city()
        else:
            # Default random string for unknown slugs
            return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
