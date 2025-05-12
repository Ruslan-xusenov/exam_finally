from django import forms
from .models import Transaction, Category, UserProfile
from django.contrib.auth.models import User

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'description']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'profile_picture']

class SignupForm(forms.Form):
    identifier = forms.CharField(
        label="Email yoki telefon raqam",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email yoki telefon raqam'})
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parol'})
    )
    confirm_password = forms.CharField(
        label="Parolni tasdiqlang",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parolni tasdiqlang'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Parollar mos emas!")
        return cleaned_data

    def is_email(self):
        identifier = self.cleaned_data.get('identifier')
        return '@' in identifier if identifier else False