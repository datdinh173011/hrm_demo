import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from contacts.models.base import BaseModel

TYPE_CHOICES = [
    ('string', 'String'),
    ('text', 'Text'),
    ('option', 'Option'),
]


class Property(BaseModel):
    # params
    slug = models.SlugField(
        default="",
        max_length=100, validators=[MinLengthValidator(1)],
        blank=True, db_index=True)
    name = models.CharField(
        max_length=100, validators=[MinLengthValidator(1)],
        blank=False, db_index=True)

    # type property
    type = models.CharField(
        max_length=100, validators=[MinLengthValidator(1)],
        blank=False, db_index=True, choices=TYPE_CHOICES)

    class Meta:
        unique_together = [
            ["slug", "type"],
        ]

    def __str__(self):
        return self.name
