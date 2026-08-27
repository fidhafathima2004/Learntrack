import os
from sys import modules
import fitz
import re
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .models import Syllabus, Module
from .models import Syllabus, Module, StudyPlan,MCQ
from datetime import date, timedelta

def login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            auth_login(request, user)

            # Admin → Custom Admin Dashboard
            if user.is_staff:
                return redirect('admin_dashboard')

            # Student → Student Dashboard
            return redirect('dashboard')

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, 'Registration successful')
        return redirect('login')

    return render(request, 'register.html')


def dashboard(request):
    study_plan = StudyPlan.objects.filter(
        student=request.user
    ).order_by('-created_at').first()

    return render(
        request,
        'dashboard.html',
        {'study_plan': study_plan}
    )
def admin_dashboard(request):
    syllabus_count = Syllabus.objects.count()
    module_count = Module.objects.count()
    mcq_count = MCQ.objects.count()
    student_count = User.objects.filter(is_staff=False).count()

    return render(
        request,
        'admin_dashboard.html',
        {
            'syllabus_count': syllabus_count,
            'module_count': module_count,
            'mcq_count': mcq_count,
            'student_count': student_count,
        }
    )
def upload_syllabus(request):
    if request.method == 'POST':
        syllabus = request.FILES.get('syllabus')

        if syllabus and syllabus.name.lower().endswith('.pdf'):

            file_path = os.path.join(settings.MEDIA_ROOT, syllabus.name)

            with open(file_path, 'wb+') as destination:
                for chunk in syllabus.chunks():
                    destination.write(chunk)

            # Extract text from PDF using PyMuPDF
            doc = fitz.open(file_path)

            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()

            # Extract modules and topics
            modules = []
            current_module = None

            for raw_line in text.splitlines():

                line = " ".join(raw_line.split()).strip()

                match = re.match(
                    r'^[▶\s]*Module\s+(\d+)\s*[-–:]\s*(.*)$',
                    line,
                    re.IGNORECASE
                )

                if match:
                    if current_module:
                        modules.append(current_module)

                    current_module = {
                        'number': match.group(1),
                        'topics': []
                    }

                    topics_text = match.group(2)

                    topics = [
                        topic.strip()
                        for topic in topics_text.split(',')
                        if topic.strip()
                    ]

                    current_module['topics'].extend(topics)

                
                elif current_module and line:
                    if re.match(r'^\d+\s*/\s*\d+$', line):
                        continue

                    topics = [
                        topic.strip()
                        for topic in line.split(',')
                        if topic.strip()
                    ]

                    current_module['topics'].extend(topics)

            if current_module:
                modules.append(current_module)

            # Display modules and topics in terminal
            print("===== MODULES AND TOPICS =====")

            for module in modules:
                print(f"Module {module['number']}:")

                for topic in module['topics']:
                    print(f"  - {topic}")

            print("==============================")

            existing = Syllabus.objects.filter(name=syllabus.name).first()
            if existing:
                messages.warning(request, 'This syllabus is already uploaded.')
                return redirect('upload_syllabus')
            syllabus_obj = Syllabus.objects.create(
                name=syllabus.name,
                pdf=syllabus
            )
            for module in modules:
                Module.objects.create(
                    syllabus=syllabus_obj,
                    module_number=int(module['number']),
                    topics=module['topics']
            )

            messages.success(
                request,
                'Syllabus uploaded and modules extracted successfully!'
            )

            return redirect('upload_syllabus')

        messages.error(request, 'Please upload a PDF file.')

    return render(request, 'upload_syllabus.html')
def syllabus(request):
    syllabuses = Syllabus.objects.all()
    return render(request, 'syllabus.html', {'syllabuses': syllabuses})


def create_study_plan(request):
    if request.method == 'POST':
        exam_date = request.POST.get('exam_date')
        daily_hours = request.POST.get('daily_hours')

        if exam_date and daily_hours:
            syllabus = Syllabus.objects.first()
            modules = Module.objects.filter(
                syllabus=syllabus
            ).order_by('module_number')

            exam = date.fromisoformat(exam_date)
            today = date.today()
            remaining_days = (exam - today).days

            schedule = []

            if remaining_days > 0 and modules.exists():
                module_count = modules.count()
                days_per_module = max(
                    1,
                    remaining_days // module_count
                )

                current_date = today

                for module in modules:
                    for _ in range(days_per_module):
                        if current_date >= exam:
                            break

                        schedule.append({
                            'date': current_date.strftime('%Y-%m-%d'),
                            'module_number': module.module_number,
                            'hours': float(daily_hours),
                            'status': 'Pending'
                        })

                        current_date += timedelta(days=1)

            StudyPlan.objects.create(
                student=request.user,
                syllabus=syllabus,
                exam_date=exam_date,
                daily_hours=daily_hours,
                schedule=schedule
            )

            messages.success(
                request,
                'Personalized study plan generated successfully.'
            )

            return redirect('dashboard')

    return render(request, 'create_study_plan.html')
def question_bank(request):
    mcqs = MCQ.objects.select_related('module').all()

    return render(
        request,
        'question_bank.html',
        {'mcqs': mcqs}
    )
def module_detail(request, module_id):
    module = Module.objects.get(id=module_id)

    return render(
        request,
        'module_detail.html',
        {'module': module}
    )
def add_mcq(request):

    modules = Module.objects.all()

    if request.method == 'POST':

        module_id = request.POST.get('module')
        question = request.POST.get('question')
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        option4 = request.POST.get('option4')
        correct_answer = request.POST.get('correct_answer')

        module = Module.objects.get(id=module_id)

        MCQ.objects.create(
            module=module,
            question=question,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_answer=correct_answer
        )

        return redirect('question_bank')

    return render(
        request,
        'add_mcq.html',
        {'modules': modules}
    )