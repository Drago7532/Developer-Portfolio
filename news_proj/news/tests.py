from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from news.models import Article, Publisher

User = get_user_model()


@override_settings(ENABLE_X_POSTING=False)
class SubscriptionFeedAPITest(TestCase):
    def setUp(self):
        # Create publishers
        self.publisher1 = Publisher.objects.create(name="Publisher 1")
        self.publisher2 = Publisher.objects.create(name="Publisher 2")

        # Create users
        self.reader = User.objects.create_user(username="reader", password="pass123", role="reader")
        self.journalist1 = User.objects.create_user(username="journalist1", password="pass123", role="journalist")
        self.journalist2 = User.objects.create_user(username="journalist2", password="pass123", role="journalist")

        # Assign journalist to publisher
        self.publisher1.journalists.add(self.journalist1)
        self.publisher2.journalists.add(self.journalist2)

        # Create articles
        self.article1 = Article.objects.create(
            title="Article by Pub1",
            content="Content 1",
            publisher=self.publisher1,
            author=self.journalist1,
            approved_by_editor=True
        )
        self.article2 = Article.objects.create(
            title="Article by Pub2",
            content="Content 2",
            publisher=self.publisher2,
            author=self.journalist2,
            approved_by_editor=True
        )
        self.article3 = Article.objects.create(
            title="Unapproved Article",
            content="Content 3",
            publisher=self.publisher1,
            author=self.journalist1,
            approved_by_editor=False
        )

        # Subscribe reader to publisher1 and journalist2
        self.reader.subscribed_publishers.add(self.publisher1)
        self.reader.subscribed_journalists.add(self.journalist2)

        # API client
        self.client.login(username="reader", password="pass123")

    def test_subscription_feed_returns_correct_articles(self):
        url = reverse("news:subscription_feed_api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        titles = [article["title"] for article in response.json()]
        self.assertIn("Article by Pub1", titles)
        self.assertIn("Article by Pub2", titles)
        self.assertNotIn("Unapproved Article", titles)

    def test_subscription_feed_empty_for_no_subscriptions(self):
        reader2 = User.objects.create_user(username="reader2", password="pass123", role="reader")
        self.client.logout()
        self.client.login(username="reader2", password="pass123")

        url = reverse("news:subscription_feed_api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)
