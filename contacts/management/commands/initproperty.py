import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from contacts.models import Property, Option


class Command(BaseCommand):
    help = 'Initialize default properties and options for contacts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing properties and options before creating new ones',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING(
                'Deleting existing properties and options...'))
            Option.objects.all().delete()
            Property.objects.all().delete()

        # Load default data from JSON file
        json_file_path = os.path.join(
            settings.BASE_DIR, 'contacts', 'default_data', 'property_contact.json'
        )

        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    f'Default data file not found: {json_file_path}')
            )
            return

        contact_properties = data.get('contact', [])
        created_properties = 0
        created_options = 0

        for prop_data in contact_properties:
            # Create or get property
            property_obj, created = Property.objects.get_or_create(
                slug=prop_data['slug'],
                defaults={
                    'name': prop_data['name'],
                    'type': prop_data['type']
                }
            )

            if created:
                created_properties += 1
                self.stdout.write(f'Created property: {property_obj.name}')
            else:
                self.stdout.write(
                    f'Property already exists: {property_obj.name}')

            # Create options if property type is 'option'
            if prop_data['type'] == 'option' and 'settings' in prop_data:
                options_data = prop_data['settings'].get('options', [])

                for idx, option_data in enumerate(options_data):
                    option_obj, option_created = Option.objects.get_or_create(
                        property=property_obj,
                        code=option_data['value'],
                        defaults={
                            'value': option_data['name'],
                            'order': idx
                        }
                    )

                    if option_created:
                        created_options += 1
                        self.stdout.write(
                            f'  Created option: {option_obj.value}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized {created_properties} properties and {created_options} options'
            )
        )
