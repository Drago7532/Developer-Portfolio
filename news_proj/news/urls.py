from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    path('', views.public_articles, name='public_articles'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),

    # Journalist actions
    path('article/create/', views.create_article, name='create_article'),
    path('journalist/articles/', views.my_articles, name='my_articles'),

    path('journalist/article/create/', views.create_article, name='create_article'),
    path('journalist/newsletter/create/', views.create_newsletter, name='create_newsletter'),

    path('journalist/article/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('journalist/article/<int:article_id>/', views.view_article, name='view_article'),
    path('journalist/article/<int:article_id>/delete/', views.delete_article, name='delete_article'),

    path('journalist/newsletters/', views.my_newsletters, name='my_newsletters'),

    path('journalist/newsletter/<int:newsletter_id>/view/', views.view_newsletter, name='view_newsletter'),
    path('journalist/newsletter/<int:newsletter_id>/edit/', views.edit_newsletter, name='edit_newsletter'),
    path('journalist/newsletter/<int:newsletter_id>/delete/', views.delete_newsletter, name='delete_newsletter'),


    # Editor Actions
    path('editor/review/', views.article_review_list, name='article_review_list'),
    path('editor/review/<int:article_id>/', views.approve_article, name='approve_article'),

    # Editor actions for newsletters
    path('editor/newsletters/', views.newsletter_review_list, name='newsletter_review_list'),
    path('editor/newsletters/<int:newsletter_id>/approve/', views.approve_newsletter, name='approve_newsletter'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('newsletters/', views.all_newsletters, name='all_newsletters'),
    path('articles/', views.all_articles, name='all_articles'),


    # Public newsletters
    path('newsletter/<int:newsletter_id>/', views.view_newsletter_public, name='view_newsletter_public'),


    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Subscriptions
    path('all_publishers/', views.all_publishers, name='all_publishers'),
    path('subscribe/publisher/<int:publisher_id>/', views.subscribe_publisher, name='subscribe_publisher'),
    path('unsubscribe/publisher/<int:publisher_id>/', views.unsubscribe_publisher, name='unsubscribe_publisher'),
    path('subscribe/journalist/<int:journalist_id>/', views.subscribe_journalist, name='subscribe_journalist'),
    path('unsubscribe/journalist/<int:journalist_id>/', views.unsubscribe_journalist, name='unsubscribe_journalist'),
    path('subscriptions/', views.subscription_feed, name='subscription_feed'),
path("api/subscriptions/", views.subscription_feed_api, name="subscription_feed_api"),
]
