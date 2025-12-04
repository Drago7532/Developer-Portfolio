from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Article, Newsletter

class Command(BaseCommand):
    help = 'Set up default roles and permissions'

    def handle(self, *args, **kwargs):
        # Create groups
        reader_group, _ = Group.objects.get_or_create(name='Reader')
        editor_group, _ = Group.objects.get_or_create(name='Editor')
        journalist_group, _ = Group.objects.get_or_create(name='Journalist')

        # Get content types
        article_ct = ContentType.objects.get_for_model(Article)
        newsletter_ct = ContentType.objects.get_for_model(Newsletter)

        # Reader permissions (view only)
        view_article = Permission.objects.get(codename='view_article', content_type=article_ct)
        view_newsletter = Permission.objects.get(codename='view_newsletter', content_type=newsletter_ct)
        reader_group.permissions.set([view_article, view_newsletter])

        # Editor permissions (view, change, delete)
        change_article = Permission.objects.get(codename='change_article', content_type=article_ct)
        delete_article = Permission.objects.get(codename='delete_article', content_type=article_ct)
        change_newsletter = Permission.objects.get(codename='change_newsletter', content_type=newsletter_ct)
        delete_newsletter = Permission.objects.get(codename='delete_newsletter', content_type=newsletter_ct)
        editor_group.permissions.set([
            view_article, change_article, delete_article,
            view_newsletter, change_newsletter, delete_newsletter
        ])

        # Journalist permissions (add, view, change, delete)
        add_article = Permission.objects.get(codename='add_article', content_type=article_ct)
        add_newsletter = Permission.objects.get(codename='add_newsletter', content_type=newsletter_ct)
        journalist_group.permissions.set([
            add_article, view_article, change_article, delete_article,
            add_newsletter, view_newsletter, change_newsletter, delete_newsletter
        ])

        self.stdout.write(self.style.SUCCESS("Roles and permissions have been successfully set up."))
