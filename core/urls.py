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
    path('question-bank/module/<int:module_id>/', views.module_questions, name='module_questions'),

    path('add-mcq/', views.add_mcq, name='add_mcq'),
    path('edit-mcq/<int:mcq_id>/', views.edit_mcq, name='edit_mcq'),
    path('delete-mcq/<int:mcq_id>/', views.delete_mcq, name='delete_mcq'),

    path('mock-test/<int:module_id>/', views.mock_test, name='mock_test'),
    path('take-test/', views.take_test, name='take_test'),
    path('complete-topic/<int:module_id>/<str:topic>/', views.complete_topic, name='complete_topic'),
    path('edit-study-plan/',views.edit_study_plan,name='edit_study_plan'),
    path('reschedule-topic/', views.reschedule_topic, name='reschedule_topic'),
    path('admin-modules/', views.admin_modules, name='admin_modules'),
    path('edit-module/<int:module_id>/', views.edit_module, name='edit_module'),
    path('delete-module/<int:module_id>/', views.delete_module, name='delete_module'),
    path('new-study-plan/',views.new_study_plan,name='new_study_plan'),
    path('manage-students/', views.manage_students, name='manage_students'),
    path('logout/', views.logout_view, name='logout'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('progress/', views.progress, name='progress'),
    path('profile/', views.profile, name='profile'),
    path('admin-progress/', views.admin_progress, name='admin_progress'),
    path('reports/', views.reports, name='reports'),
]