from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = (
            "title",
            "description",
            "shooting_date",
            "start_time",
            "end_time",
            "location",
        )