from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('upload-syllabus/', views.upload_syllabus, name='upload_syllabus'),
    path('syllabus/', views.syllabus, name='syllabus'),
    path('create-study-plan/', views.create_study_plan, name='create_study_plan'),
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('question-bank/', views.question_bank, name='question_bank'),
    path('add-mcq/', views.add_mcq, name='add_mcq'),
]