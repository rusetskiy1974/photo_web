from django.urls import path

from . import views 

app_name ='users'

urlpatterns = [
    path('login/', views.login, name='login'),
    
    # path('accounts/google/login/', views.google_login_auto_redirect, name='google_login_auto_redirect'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout, name='logout'),
    
    
]
