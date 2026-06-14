import os
from django.conf import settings
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token

User = get_user_model()

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        token = account_activation_token.make_token(instance)

        message = f"Вітаємо на сайті фотографа ! \n\n" \
                  f"Для активації вашого профілю перейдіть за посиланням:\n" \
                  f"http://127.0.0.1:8000/activate/{uid}/{token}/"

        send_mail(
            subject="Підтвердження реєстрації на сайті фотографа",
            message=message,
            from_email="sergrus1974@gmail.com",
            recipient_list=[instance.email],
            fail_silently=False,
        )


@receiver(post_migrate)
def ensure_socialapp_and_site(sender, **kwargs):
    """Автоініціалізація SocialApp(Google) + Site після міграцій у DEV/локально."""
    # Працюємо лише в DEV або якщо явно дозволено
    if not (getattr(settings, "DEBUG", False) or os.getenv("AUTO_INIT_SOCIAL") == "1"):
        return

    # Потрібні ключі — інакше пропускаємо без падіння
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not secret:
        return

    try:
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp
    except Exception as e:
        print(e)
        # Якщо пакети ще не готові (на ранніх етапах) — тихо виходимо
        return

    # Визначаємо домен і ім’я сайту для локалки
    site_id = int(os.getenv("SITE_ID", getattr(settings, "SITE_ID", 1)))
    domain = os.getenv("SITE_DOMAIN", "localhost:8000")
    name = os.getenv("SITE_NAME", "Photo Web")

    site, _ = Site.objects.update_or_create(
        id=site_id,
        defaults={"domain": domain, "name": name},
    )

    app, _ = SocialApp.objects.update_or_create(
        provider="google",
        defaults={
            "name": "Google",
            "client_id": client_id,
            "secret": secret,
        },
    )
    app.sites.set([site])
    app.save()