import uuid

from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Option(models.Model):
    id = models.UUIDField(
        _("id"), primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(
        "contacts.Property", blank=True, null=True, on_delete=models.CASCADE,
        related_name="%(class)ss", related_query_name="%(class)s")
    code = models.CharField(max_length=100, blank=True, default="")
    value = models.CharField(
        max_length=100, validators=[MinLengthValidator(1)],
        blank=False, db_index=True)
    order = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        blank=True)

    class Meta:
        unique_together = [
            ["property", "code"],
        ]

    def __str__(self):
        return self.value
