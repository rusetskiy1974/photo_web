from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={
                                  'class': 'form-input',
                                  'placeholder': 'Your Name'
                                   }))
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={
                                   'class': 'form-input',
                                   'placeholder': 'E-mail'
                                     }))
    date = forms.CharField(required=True,
                           widget=forms.TextInput(attrs={
                                   'class': 'form-input',
                                   'data-time-picker': 'date',
                                   'placeholder': 'Event Date'
                                    }))
    message = forms.CharField(required=True,
                           widget=forms.Textarea(attrs={
                                    'class': 'form-input',
                                    'placeholder': 'Your Message'
                                }))
