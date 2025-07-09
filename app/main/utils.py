from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import render

from .forms import ContactForm


def sending_mail(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        try:
            email = EmailMessage(
                subject="New Contact Request",
                body=(
                    f"Date: {form.cleaned_data['date']}\n"
                    f"Name: {form.cleaned_data['name']}\n"
                    f"Email: {form.cleaned_data['email']}\n"
                    f"Message:\n{form.cleaned_data['message']}"
                ),
                from_email=form.cleaned_data['email'],
                to=['sergrus1974@gmail.com'],
                reply_to=[form.cleaned_data['email']],
            )
            email.send()
            messages.success(request, "Email sent successfully.")
            return ContactForm()

        except Exception as e:
            messages.error(request, f"Email sending failed: {str(e)}")
    else:
        messages.warning(request, "Please input correct value in form.")
    return form