from django.urls import path
from .views import CreateBookingView

app_name = "bookings"

urlpatterns = [
    path(
        "photographer/<int:pk>/create/",
        CreateBookingView.as_view(),
        name="create_booking"
    ),
]