from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import logout_view

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('categories/', views.categories, name='categories'),
    path('statistics/', views.statistics, name='statistics'),
    path('categories/add/', views.add_category, name='add_category'),
    path('reports/', views.reports, name='reports'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('verify/', views.verify_code_view, name='verify_code'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
]