from django.contrib.auth.views import (PasswordResetDoneView,
                                       PasswordResetConfirmView,
                                       PasswordResetCompleteView)
from django.urls import path, reverse_lazy

from . import views 

app_name ='users'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('cabinet/', views.UserCabinetView.as_view(), name='cabinet'),
    path('registration/', views.RegisterView.as_view(), name='registration'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('edit_profile/', views.UserEditView.as_view(), name='edit_profile'),
    path("google/login/", views.google_login, name="google_login"),
    path("google/register/client/", views.google_register_client, name="google_register_client"),
    path("google/register/photographer/", views.google_register_photographer, name="google_register_photographer"),
    path('sign-out/', views.sign_out, name='sign_out'),
    path('logout/', views.logout, name='logout'),
    path('my_photos/', views.my_photos, name='my_photos'),
    path('handle_photos/', views.handle_photos, name='handle_photos'),
    path('reset-password/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                          success_url=reverse_lazy('users:password_reset_complete') ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
    PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
    name='password_reset_complete'),
    path('password/change', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done', views.password_change_done, name='password_change_done'),

]
