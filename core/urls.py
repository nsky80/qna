from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index-view'),
    path('login/', views.LoginView.as_view(), name='login-view'),
    path('register/', views.RegisterView.as_view(), name='register-view'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard-view'),
    path('logout/', views.LogoutView.as_view(), name='logout-view'),
    path('ask_question/', views.AskQuestionView.as_view(), name='ask_question-view'),
    path('questions/<int:question_id>/<str:question_slug>', views.WriteAnswerView.as_view(), name="write_answer-view"),
    path('tag/<str:slug>', views.tagged, name="tagged-view"),
]
