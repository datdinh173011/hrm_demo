from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModelPropertyManager(models.Manager):
    pass


class BaseModelProperty(models.Model):
    id = models.BigAutoField(
        _("id"), auto_created=True, primary_key=True, editable=False)
    property = models.ForeignKey(
        "contacts.Property", blank=True, null=True, on_delete=models.CASCADE,
        related_name="%(class)ss", related_query_name="%(class)s")

    # Type fields and options
    slug = models.CharField(
        max_length=32, default=None, blank=True, null=True)
    variant = models.CharField(
        max_length=32, default=None, blank=True, null=True)

    # Value fields
    singleline_value = models.CharField(
        max_length=255, default=None, blank=True, null=True)
    richtext_value = models.TextField(default=None, blank=True, null=True)
    singleoption_value = models.ForeignKey(
        "contacts.Option", default=None, blank=True, null=True, on_delete=models.CASCADE,
        related_name="single_option_%(class)ss", related_query_name="single_option_%(class)s")
    multipleoption_value = models.ManyToManyField(
        "contacts.Option", blank=True, related_name="multiple_option_%(class)ss",
        related_query_name="multiple_option_%(class)s")

    # history
    created_by = models.ForeignKey(
        "account.User", blank=True, null=True, on_delete=models.SET_NULL,
        related_name="created_%(class)ss", related_query_name="created_%(class)s")
    changed_by = models.ForeignKey(
        "account.User", blank=True, null=True, on_delete=models.SET_NULL,
        related_name="changed_%(class)ss", related_query_name="changed_%(class)s")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BaseModelPropertyManager()

    class Meta:
        abstract = True
        verbose_name = _("Base Model Property")
        verbose_name_plural = _("Base Model Properties")
