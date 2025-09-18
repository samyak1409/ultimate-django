from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Tag(models.Model):

    label = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.label


# Custom Manager to reduce repetitive code while querying:
class TaggedItemCustomManager(models.Manager):

    def get_for(self, model: models.Model, object_id: int):
        content_type = ContentType.objects.get_for_model(model)
        return TaggedItem.objects.select_related("tag").filter(
            content_type=content_type, object_id=object_id
        )


class TaggedItem(models.Model):

    # To define a generic relationship, we need to define three fields:
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    tag = models.ForeignKey(to=Tag, on_delete=models.CASCADE)
    # `CASCADE`: because if a tag is deleted, delete all the records where an object is tagged with tag, meaning removing that tag from all the objects

    # Custom manager:
    objects = TaggedItemCustomManager()
