from rest_framework import generics, permissions
from news.models import Article, Publisher
from .serializers import ArticleSerializer
from rest_framework.response import Response
from django.db.models import Q

class PublisherArticlesList(generics.ListAPIView):
    """
    GET /api/publishers/<pk>/articles/
    Returns approved articles for a publisher.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]  # publisher articles can be public (change if needed)

    def get_queryset(self):
        publisher_pk = self.kwargs['pk']
        return Article.objects.filter(publisher_id=publisher_pk, approved_by_editor=True).order_by('-created_at')


class JournalistArticlesList(generics.ListAPIView):
    """
    GET /api/journalists/<pk>/articles/
    Returns approved articles for a journalist (author).
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        journalist_pk = self.kwargs['pk']
        return Article.objects.filter(author_id=journalist_pk, approved_by_editor=True).order_by('-created_at')


class SubscriptionsArticlesList(generics.ListAPIView):
    """
    GET /api/subscriptions/articles/
    Returns approved articles for the authenticated user's subscriptions.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # user subscribed publishers and journalists (custom fields)
        return Article.objects.filter(
            approved_by_editor=True
        ).filter(
            (Q(publisher__in=user.subscribed_publishers.all())) |
            (Q(author__in=user.subscribed_journalists.all()))
        ).order_by('-created_at')
