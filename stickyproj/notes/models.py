from django.db import models
from django.urls import reverse


class Note(models.Model):
    note_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Make pycharm (and other linters) recognise objects
    objects:models.Manager["Note"]

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.title or 'Untitled'} ({self.timestamp:%Y-%m-%d %H:%M}"

    def get_absolute_url(self):
        return reverse('notes:note_detail', kwargs={'pk': self.pk})
