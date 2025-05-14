from django import forms
from .models import Transaction, Category, User
from django.contrib.auth.models import User
import re

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

class SignupForm(forms.Form):
    username = forms.CharField(max_length=150)
    identifier = forms.CharField(label="Email yoki telefon", max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu username allaqachon mavjud.")
        return username

    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier')
        if not self.is_email(identifier) and not self.is_phone(identifier):
            raise forms.ValidationError("Noto‘g‘ri email yoki telefon raqam.")
        return identifier    

    def is_email(self, identifier):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, identifier) is not None

    def is_phone(self, identifier):
        phone_regex = r'^\+?[\d\s\-]+$'
        return re.match(phone_regex, identifier) is not None