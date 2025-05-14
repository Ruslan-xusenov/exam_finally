from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils.timezone import make_aware
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm, UserForm, SignupForm
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import date, datetime, timedelta
import random
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from .utils import is_email, is_phone
from django.contrib.auth import login 

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def contact(request):
    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')


@login_required
def index(request):
    today = date.today()
    transactions = Transaction.objects.filter(user=request.user, date__month=today.month)
    income = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income - expenses
    context = {
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'recent_transactions': transactions.order_by('-date')[:5]
    }
    return render(request, 'index.html', context)


@login_required
def statistics(request):
    today = date.today()
    start_date = today.replace(day=1)
    end_date = today
    one_day_ago = today - timedelta(days=1)
    one_day_transactions = Transaction.objects.filter(user=request.user, date__date=one_day_ago)
    one_day_income = one_day_transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    one_day_expenses = one_day_transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    one_day_balance = one_day_income - one_day_expenses
    transactions = Transaction.objects.filter(user=request.user, date__range=[start_date, end_date])
    income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income - expenses
    one_year_ago = today - timedelta(days=365)
    one_year_transactions = Transaction.objects.filter(user=request.user, date__gte=one_year_ago)
    one_year_income = one_year_transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    one_year_expenses = one_year_transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    one_year_balance = one_year_income - one_year_expenses

    context = {
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'one_day_income': one_day_income,
        'one_day_expenses': one_day_expenses,
        'one_day_balance': one_day_balance,
        'one_year_income': one_year_income,
        'one_year_expenses': one_year_expenses,
        'one_year_balance': one_year_balance,
        'transactions': transactions.order_by('-date')
    }

    return render(request, 'statistics.html', context)


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'add_transaction.html', {'form': form})


@login_required
def view_transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transactions.html', {'transactions': transactions})


@login_required
def categories(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})


@login_required
def reports(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    transactions = Transaction.objects.filter(user=request.user)
    if start_date and end_date:
        start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
        transactions = transactions.filter(date__range=[start_date, end_date])
    income = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'reports.html', {
        'income': income,
        'expenses': expenses,
        'balance': income - expenses,
        'transactions': transactions.order_by('-date')
    })


@login_required
def dashboard(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    transactions = Transaction.objects.filter(user=request.user)
    if start_date and end_date:
        transactions = transactions.filter(
            date__range=[start_date, end_date]
        )

    transactions = transactions.order_by('-date')

    income_total = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense_total = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0


    context = {
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'income_total': income_total,
        'expense_total': expense_total,
    }
    return render(request, 'dashboard.html', context)


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            
            code = random.randint(1000, 9999)

            if is_email(identifier):
                
                send_mail(
                    subject='Tasdiqlash kodi',
                    message=f"Sizning ro'yxatdan o‘tish kodingiz: {code}",
                    from_email='webmaster@localhost',
                    recipient_list=[identifier],
                    fail_silently=False,
                )
                verified = True

            elif is_phone(identifier):
                print(f"Telefon raqamga yuborilgan kod: {code}")
                verified = True

            else:
                form.add_error('identifier', 'Email yoki telefon noto‘g‘ri')
                return render(request, 'signup.html', {'form': form})

            
            if verified:
                user = User.objects.create_user(username=username, password=password)
                if is_email(identifier):
                    user.email = identifier
                else:
                    user.phone = identifier
                user.save()

                login(request, user)
                messages.success(request, 'Ro‘yxatdan muvaffaqiyatli o‘tdingiz!')
                return redirect('home')

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            code = random.randint(1000, 9999)

            if is_email(identifier):
                send_mail(
                    subject='Tasdiqlash kodi',
                    message=f"Sizning ro'yxatdan o‘tish kodingiz: {code}",
                    from_email='webmaster@localhost',
                    recipient_list=[identifier],
                    fail_silently=False,
                )
                verified = True

            elif is_phone(identifier):
                print(f"Telefon raqamga yuborilgan kod: {code}")
                verified = True

            else:
                form.add_error('identifier', 'Email yoki telefon noto‘g‘ri')
                return render(request, 'signup.html', {'form': form})

            if verified:
                user = User.objects.create_user(username=username, password=password)
                if is_email(identifier):
                    user.email = identifier
                else:
                    user.phone = identifier
                user.save()

                login(request, user)
                messages.success(request, 'Ro‘yxatdan muvaffaqiyatli o‘tdingiz!')
                return redirect('home')

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def verify_code_view(request):
    if request.method == 'POST':
        input_code = request.POST.get('code')
        actual_code = request.session.get('register_code')
        
        if input_code == actual_code:
            identifier = request.session.get('identifier')
            username = request.session.get('username')
            password = request.session.get('password')

            user = User.objects.create_user(username=username, password=password)
            if '@' in identifier:
                user.email = identifier
            user.save()
            messages.success(request, "Ro‘yxatdan o‘tish muvaffaqiyatli.")
            return redirect('login')
        else:
            messages.error(request, "Kod noto‘g‘ri.")
    return render(request, 'verify_code.html')


def logout_view(request):
    logout(request)
    return redirect('home')