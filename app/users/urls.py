from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path

from . import views 

app_name ='users'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('sign-in-with-google/', views.sign_in_with_google, name='sign_in_with_google'),
    path('auth-receiver/', views.auth_receiver, name='auth_receiver'),
    # path('accounts/google/login/', views.google_login_auto_redirect, name='google_login_auto_redirect'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout, name='logout'),
    path('my_photos/', views.my_photos, name='my_photos'),
    path('handle_photos/', views.handle_photos, name='handle_photos'),
    path('reset-password/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                          success_url='users/reset-password/complete/'),
         name='password_reset_confirm'),
    path('reset-password-complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]
