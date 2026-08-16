import os
import fitz
import re
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .models import Syllabus, Module

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
            if user.is_staff:
                return redirect('admin_dashboard')
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


def upload_syllabus(request):
    if request.method == 'POST':
        syllabus = request.FILES.get('syllabus')

        if syllabus and syllabus.name.lower().endswith('.pdf'):
            file_path = os.path.join(settings.MEDIA_ROOT, syllabus.name)

            with open(file_path, 'wb+') as destination:
                for chunk in syllabus.chunks():
                    destination.write(chunk)

            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            modules = []
            current_module = None

            for raw_line in text.splitlines():
                line = " ".join(raw_line.split()).strip()
                match = re.match(r'^[▶\s]*Module\s+(\d+)\s*[-–:]\s*(.*)$', line, re.IGNORECASE)

                if match:
                    if current_module:
                        modules.append(current_module)
                    current_module = {'number': match.group(1), 'topics': []}
                    topics_text = match.group(2)
                    topics = [t.strip() for t in topics_text.split(',') if t.strip()]
                    current_module['topics'].extend(topics)
                elif current_module and line:
                    if re.match(r'^\d+\s*/\s*\d+$', line):
                        continue
                    topics = [t.strip() for t in line.split(',') if t.strip()]
                    current_module['topics'].extend(topics)

            if current_module:
                modules.append(current_module)

            existing = Syllabus.objects.filter(name=syllabus.name).first()
            if existing:
                messages.warning(request, 'This syllabus is already uploaded.')
                return redirect('upload_syllabus')

            syllabus_obj = Syllabus.objects.create(name=syllabus.name, pdf=syllabus)
            for module in modules:
                Module.objects.create(
                    syllabus=syllabus_obj,
                    module_number=int(module['number']),
                    topics=module['topics']
                )

            messages.success(request, 'Syllabus uploaded and modules extracted successfully!')
            return redirect('upload_syllabus')

        messages.error(request, 'Please upload a PDF file.')

    return render(request, 'upload_syllabus.html')


def syllabus(request):
    syllabuses = Syllabus.objects.all()
    return render(request, 'syllabus.html', {'syllabuses': syllabuses})


def admin_dashboard(request):
    syllabus_count = Syllabus.objects.count()
    module_count = Module.objects.count()
    student_count = User.objects.filter(is_staff=False).count()

    return render(
        request,
        'admin_dashboard.html',
        {
            'syllabus_count': syllabus_count,
            'module_count': module_count,
            'mcq_count': 0,
            'student_count': student_count,
        }
    )
