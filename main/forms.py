from django import forms
from django.contrib.auth.models import User

from .models import JobListing

class JobListingForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ['title', 'description', 'company_name', 'location', 'employment_type', 'company_logo', 'skills']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.TextInput(attrs={'placeholder': 'e.g., Python, Django, SQL'}),
        }


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    user_type = forms.ChoiceField(
        choices=[('job_seeker', 'Job Seeker'), ('employer', 'Employer')],
        widget=forms.Select,
        label="Register as"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check if the passwords match
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        # more validation for password

        return cleaned_data

class SkillsInputForm(forms.Form):
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Skills",
        help_text="List your skills separated by commas."
    )

class JobApplicationForm(forms.Form):
    full_name = forms.CharField(
        max_length=255,
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'Your Full Name'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email Address'})
    )
    phone_number = forms.CharField(
        max_length=15,
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': 'Your Phone Number'})
    )
    location = forms.CharField(
        max_length=255,
        label="Location",
        widget=forms.TextInput(attrs={'placeholder': 'Your Current Location'})
    )
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write a brief cover letter'}),
        label="Cover Letter"
    )
    cv = forms.FileField(label="Upload CV", help_text="Upload your CV in PDF format.")