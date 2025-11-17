import re
from django import forms
from .models import User
from .models import Profile
from django.core.exceptions import ValidationError

from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import User
import re

# Name validator (already provided)
def validate_name(value):
    value = value.strip()
    if len(value) < 2:
        raise ValidationError("Name must be at least 2 characters.")
    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ]+([ '-.][A-Za-zÀ-ÖØ-öø-ÿ]+)*$", value):
        raise ValidationError(
            "Name can only contain letters, spaces, dots, and hyphens. Each word must start with a letter."
        )

# Email validator
email_validator = RegexValidator(
    regex=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
    message="Enter a valid email address."
)

class RegistrationForm(forms.ModelForm):
    name = forms.CharField(
        validators=[validate_name],
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'})
    )
    email = forms.EmailField(
        validators=[email_validator],
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )

    class Meta:
        model = User
        fields = ['name', 'email']

    
class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    otp = forms.CharField(label='OTP', max_length=6)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic']
        widgets = {
            'profile_pic': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class OTPChangeForm(forms.ModelForm):
    otp = forms.CharField(
        label="New OTP / PIN",
        min_length=4, max_length=6, strip=True,
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-lg border border-gray-600 bg-gray-800 text-white px-4 py-3",
            "placeholder": "Enter new OTP/PIN"
        })
    )
    class Meta:
        model = User
        fields = ["otp"]



