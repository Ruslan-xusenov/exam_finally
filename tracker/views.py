from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils.timezone import make_aware
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm, UserForm, UserProfileForm, SignupForm
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import date, datetime
import random
from django.core.mail import send_mail
from django.conf import settings


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


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
def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def statistics(request):
    today = date.today()
    start_date = today.replace(day=1)  # Oy boshidan boshlab
    end_date = today  # Bugungi sana

    # Foydalanuvchi uchun oylik kirim va chiqimlar
    transactions = Transaction.objects.filter(user=request.user, date__range=[start_date, end_date])
    income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income - expenses

    context = {
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'transactions': transactions.order_by('-date')
    }

    return render(request, 'statistics.html', context)


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
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'dashboard.html', {'transactions': transactions})


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            code = str(random.randint(1000, 9999))

            request.session['register_code'] = code
            request.session['identifier'] = identifier
            request.session['password'] = password

            if form.is_email():
                send_mail(
                    subject='Tasdiqlash kodi',
                    message=f"Sizning ro'yxatdan o‘tish kodingiz: {code}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[identifier],
                )
                messages.info(request, "Tasdiqlash kodi emailingizga yuborildi.")
            else:
                print(f"Ro'yxatdan o'tish kodingiz: {code}")
                messages.info(request, "Tasdiqlash kodi terminalga chiqarildi.")

            return redirect('verify_code')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def verify_code_view(request):
    if request.method == 'POST':
        input_code = request.POST.get('code')
        actual_code = request.session.get('register_code')
        
        if input_code == actual_code:
            identifier = request.session.get('identifier')
            password = request.session.get('password')
            username = identifier.split('@')[0] if '@' in identifier else identifier[-6:]
            
            count = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{count}"
                count += 1
            
            user = User.objects.create_user(username=username, password=password)
            if '@' in identifier:
                user.email = identifier
            else:
                user.username = identifier
            user.save()
            
            messages.success(request, "Ro‘yxatdan o‘tish muvaffaqiyatli.")
            return redirect('login')
        else:
            messages.error(request, "Kod noto‘g‘ri.")
    return render(request, 'verify_code.html')


def logout_view(request):
    logout(request)
    return redirect('home')
