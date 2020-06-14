from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login-view'),
    path('register/', views.RegisterView.as_view(), name='register-view'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard-view'),
    path('logout/', views.LogoutView.as_view(), name='logout-view'),

]
