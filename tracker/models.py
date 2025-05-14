from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    type_choices = [
        ('income', 'Kirim'),
        ('expense', 'Chiqim')
    ]
    type = models.CharField(max_length=7, choices=type_choices)
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'

    TYPE_CHOICES = [
        (INCOME, 'Kirim'),
        (EXPENSE, 'Chiqim'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default=INCOME)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.type} - {self.amount} so‘m'