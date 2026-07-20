from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.models import PhotographerProfile
from .models import Booking
from .forms import BookingForm


class CreateBookingView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/create_booking.html"
    success_url = reverse_lazy("users:cabinet")

    def dispatch(self, request, *args, **kwargs):
        self.photographer = get_object_or_404(
            PhotographerProfile,
            pk=self.kwargs["pk"]
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.client = self.request.user.client_profile
        form.instance.photographer = self.photographer
        return super().form_valid(form)
