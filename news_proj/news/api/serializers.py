from rest_framework import serializers
from news.models import Article, Publisher
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ('id', 'name', 'description')

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')

class ArticleSerializer(serializers.ModelSerializer):
    publisher = PublisherSerializer(read_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'approved_by_editor', 'publisher', 'author', 'created_at', 'updated_at')
