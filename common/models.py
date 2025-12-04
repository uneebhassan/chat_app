from django.db import models
import uuid


class UUIDTimeStampedModelMixin(models.Model):
    """
    Base model that stores created_at, updated_at, and id (which is
    a uuid string).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True  # this is an abstract model
