from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Tag(models.Model):

    label = models.CharField(max_length=255)


class TaggedItem(models.Model):
    """Columns: Object, Tag"""

    # To define a generic relationship, we need to define three fields:
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    tag = models.ForeignKey(to=Tag, on_delete=models.CASCADE)
    # `CASCASE`: because if a tag is deleted, delete all the records where an object is tagged with tag, meaning removing that tag from all the objects
