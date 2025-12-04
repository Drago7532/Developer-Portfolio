from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from .models import Article, CustomUser
import requests
from requests_oauthlib import OAuth1

# ✅ Store previous approval state
@receiver(pre_save, sender=Article)
def cache_previous_article_state(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Article.objects.get(pk=instance.pk)
        instance._previous_approved_state = old_instance.approved_by_editor
    else:
        instance._previous_approved_state = False


@receiver(post_save, sender=Article)
def article_approved_handler(sender, instance, created, **kwargs):
    """
    Fires ONLY when article changes from NOT approved -> approved.
    """

    # Only trigger when approval state changes
    previously_approved = getattr(instance, "_previous_approved_state", False)

    if previously_approved or not instance.approved_by_editor:
        return  # Not a real approval event

    # Ensure publisher exists
    if not instance.publisher:
        print("X POSTING BLOCKED: Article has no publisher")
        return

    # =========================
    # EMAIL NOTIFICATIONS
    # =========================

    publisher_subs = CustomUser.objects.filter(
        subscribed_publishers=instance.publisher
    )

    journalist_subs = CustomUser.objects.filter(
        subscribed_journalists=instance.author
    )

    users = (publisher_subs | journalist_subs).distinct()
    emails = [u.email for u in users if u.email]

    if emails:
        send_mail(
            subject=f"New Article Published: {instance.title}",
            message=(
                f"{instance.title}\n\n"
                f"By: {instance.author.get_full_name() or instance.author.username}\n\n"
                f"{instance.content}\n\n"
                f"Publisher: {instance.publisher.name}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True
        )

    # ===============
    # TWITTER POSTING
    # ===============

    if not settings.ENABLE_X_POSTING:
        print("X Posting Disabled")
        return

    auth = OAuth1(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_KEY_SECRET,
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_TOKEN_SECRET
    )

    payload = {
        "text": f"{instance.title}\n\n{instance.content[:240]}"
    }

    try:
        response = requests.post(
            "https://api.twitter.com/2/tweets",
            auth=auth,
            json=payload,
            timeout=10
        )

        if response.status_code == 201:
            print("Tweet successfully posted for:", instance.title)
        else:
            print("X API ERROR:", response.status_code, response.text)

    except requests.RequestException as e:
        print("X CONNECTION ERROR:", str(e))
