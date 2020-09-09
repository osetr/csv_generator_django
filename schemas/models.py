from djongo import models
from accounts.models import User
from datetime import datetime
import uuid


class Schema(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=64)
    separator = models.CharField(max_length=10)
    date = models.DateTimeField(default=datetime.now(), editable=False)
    columns = models.JSONField()

    def __str__(self):
        return "%s by %s" % (self.name, self.author)


class Processing(models.Model):
    file_id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, default=None)
    date = models.DateTimeField(default=datetime.now(), editable=False)
    file_ready = models.BooleanField(default=False)
    rows = models.IntegerField()

    def __str__(self):
        return "schema %s with %s rows" % (self.schema.id, self.rows)
