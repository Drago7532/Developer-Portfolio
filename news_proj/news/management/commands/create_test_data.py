from django.core.management.base import BaseCommand
from news.models import CustomUser, Publisher, Article
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Create initial test data"

    def handle(self, *args, **kwargs):
        # Publisher
        pub, _ = Publisher.objects.get_or_create(name="Tech Daily")

        # Journalist
        journalist, created = CustomUser.objects.get_or_create(
            username="john",
            defaults={"email": "john@example.com"}
        )
        if created:
            journalist.set_password("1234")
            journalist.save()

        group = Group.objects.get(name="Journalist")
        journalist.groups.add(group)

        # Article
        Article.objects.get_or_create(
            title="Breaking News: Django App Test",
            author=journalist,
            publisher=pub,
            defaults={"content": "This is a test article.", "approved_by_editor": False}
        )

        self.stdout.write(self.style.SUCCESS("Test data created successfully."))
