from django.db import models
from django.utils.translation import gettext_lazy as _
from contacts.models.base_property import BaseModelProperty


class ContactProperty(BaseModelProperty):
    contact = models.ForeignKey(
        "contacts.Contact", blank=True, null=True, on_delete=models.CASCADE,
        related_name="%(class)ss", related_query_name="%(class)s")

    class Meta:
        unique_together = [
            ["property", "contact"],
        ]
