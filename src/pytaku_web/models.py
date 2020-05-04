from django.contrib.postgres.fields import ArrayField
from django.db import models


class Title(models.Model):
    class Meta:
        db_table = "title"

    site = models.CharField(max_length=50)
    original_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    alt_names = ArrayField(models.CharField(max_length=255), default=list)
    cover = models.CharField(max_length=255)
    descriptions = ArrayField(models.TextField(), default=list)  # paragraphs
    publication_status = models.CharField(max_length=100)
    authors = ArrayField(models.CharField(max_length=100), default=list)
    tags = ArrayField(models.CharField(max_length=50), default=list)

    def __str__(self):
        return f"{self.name} ({self.id})"


class Chapter(models.Model):
    class Meta:
        db_table = "chapter"
        constraints = [
            models.UniqueConstraint(
                fields=["title", "ordering"], name="unique_order_within_title"
            )
        ]

    original_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name="chapters")
    num_major = models.PositiveIntegerField()
    num_minor = models.PositiveIntegerField(null=True, blank=True)
    pages = ArrayField(models.TextField(), default=list)

    def __str__(self):
        return f"{self.name} ({self.id})"

    @property
    def next_chapter(self):
        try:
            return Title.chapters.get(ordering=self.ordering + 1)
        except Chapter.DoesNotExist:
            return None

    @property
    def prev_chapter(self):
        # premature optimzation: avoid unnecessary db query
        if self.ordering == 0:
            return None

        try:
            return Title.chapters.get(ordering=self.ordering - 1)
        except Chapter.DoesNotExist:
            return None
