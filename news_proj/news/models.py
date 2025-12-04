from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

# Create your models here.
ROLE_CHOICES = (
    ('reader', 'Reader'),
    ('editor', 'Editor'),
    ('journalist', 'Journalist'),
)

class Publisher(models.Model):
    name = models.CharField(max_length=255)
    journalists = models.ManyToManyField('CustomUser', blank=True, related_name='publishers_journalists')
    editors = models.ManyToManyField('CustomUser', blank=True, related_name='editor_publisher')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Fields for Readers
    subscribed_publishers = models.ManyToManyField(Publisher, blank=True, related_name='subscribed_readers')
    subscribed_journalists = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='reader_followers')

    # Fields for Journalists
    published_articles = models.ManyToManyField('Article', blank=True, related_name='journalist_article')
    published_newsletters = models.ManyToManyField('Newsletter', blank=True, related_name='journalist_newsletters')

    def save(self, *args, **kwargs):
        # Save first to ensure the object has an ID
        super().save(*args, **kwargs)

        # Ensure readers/journalists fields are mutually exclusive
        if self.role == 'journalist':
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()
        elif self.role == 'reader':
            self.published_articles.clear()
            self.published_newsletters.clear()



class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    approved_by_editor = models.BooleanField(default=False)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='articles')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles_authored')

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='newsletters')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='newsletters_authored')
    approved_by_editor = models.BooleanField(default=False)

    def __str__(self):
        return self.title
