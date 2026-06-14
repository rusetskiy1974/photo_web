from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
import logging
import requests
from django.core.files.base import ContentFile


logger = logging.getLogger(__name__)
User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get("email")

        if not email:
            return

        google_flow = request.session.get("google_flow", "login")

        # Якщо це LOGIN, але такого юзера ще нема — НЕ створюємо акаунт
        if google_flow == "login" and not User.objects.filter(email=email).exists():
            messages.warning(request, "To register via Google, \
            go to the Registration section and select Google registration with the desired role.")
            raise ImmediateHttpResponse(redirect("users:login"))

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        user.is_active = True

        # Перший юзер = admin
        if not User.objects.exclude(pk=user.pk).exists():
            user.role = User.Role.ADMIN
            user.is_staff = True
            user.is_superuser = True
        else:
            google_role = request.session.get("google_role")

            # Роль ставимо тільки при REGISTER
            if google_role in [User.Role.CLIENT, User.Role.PHOTOGRAPHER]:
                user.role = google_role
            else:
                user.role = User.Role.CLIENT
        # avatar from Google
        picture = sociallogin.account.extra_data.get("picture")

        logger.info(f"Google extra_data: {sociallogin.account.extra_data}")
        logger.info(f"Google picture URL: {picture}")

        if picture and not user.avatar:
            try:
                response = requests.get(
                    picture,
                    timeout=10,
                    headers={"User-Agent": "Mozilla/5.0"}
                )

                logger.info(f"Google avatar status: {response.status_code}")

                if response.status_code == 200:
                    avatar_file = ContentFile(
                        response.content,
                        name=f"user_{user.id}_google_avatar.jpg"
                    )
                    user.upload_image(avatar_file)

                    logger.info(f"Avatar uploaded to Cloudinary: {user.avatar}")
                else:
                    logger.warning(f"Google avatar download failed: {response.status_code}")

            except Exception as e:
                logger.exception(f"Google avatar upload error for {user.email}: {e}")
        user.save()
        return user