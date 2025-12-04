from django.urls import path
from .views import PublisherArticlesList, JournalistArticlesList, SubscriptionsArticlesList

urlpatterns = [
    path('publishers/<int:pk>/articles/', PublisherArticlesList.as_view(), name='api-publisher-articles'),
    path('journalists/<int:pk>/articles/', JournalistArticlesList.as_view(), name='api-journalist-articles'),
    path('subscriptions/articles/', SubscriptionsArticlesList.as_view(), name='api-subscriptions-articles'),
]
