import uuid

from django.db import models
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _


class BaseModelManager(models.Manager):
    pass


class BaseModel(models.Model):
    id = models.UUIDField(
        _("id"), primary_key=True, default=uuid.uuid4, editable=False)
    # history
    created_by = models.ForeignKey(
        "users.User", blank=True, null=True, on_delete=models.SET_NULL,
        related_name="created_%(class)ss", related_query_name="created_%(class)s")
    changed_by = models.ForeignKey(
        "users.User", blank=True, null=True, on_delete=models.SET_NULL,
        related_name="changed_%(class)ss", related_query_name="changed_%(class)s")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BaseModelManager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        try:
            return super().delete(*args, **kwargs)
        except IntegrityError:
            model_name = self._meta.model_name
            properties = getattr(self, model_name + "propertys").all()
            for property in properties:
                property.delete()
            return super().delete(*args, **kwargs)
