import os
from sys import modules
import fitz
import re
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .models import StudentProfile, Syllabus, Module
from .models import Syllabus, Module, StudyPlan,MCQ,ModuleProgress
from datetime import date, timedelta
from django.contrib.auth import logout


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
        semester = request.POST['semester']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        StudentProfile.objects.create(
            student=user,
            semester=semester
        )

        messages.success(request, 'Registration successful')
        return redirect('login')

    return render(request, 'register.html')
def dashboard(request):

    study_plan = StudyPlan.objects.filter(
        student=request.user
    ).order_by('-created_at').first()

    # Automatic rescheduling of missed topics
    if study_plan:
        schedule = study_plan.schedule
        exam_date = study_plan.exam_date
        today = date.today()

        pending_topics = [
            item for item in schedule
            if item['status'] != 'Completed'
            and date.fromisoformat(item['date']) < today
        ]

        current_date = today

        for item in pending_topics:

            if current_date >= exam_date:
                break

            item['date'] = current_date.strftime('%Y-%m-%d')
            item['status'] = 'Pending'

            current_date += timedelta(days=1)

        study_plan.schedule = schedule
        study_plan.save()

    completed_modules = ModuleProgress.objects.filter(
        student=request.user,
        completed=True
    ).count()

    total_modules = Module.objects.count()

    overall_progress = 0

    if total_modules > 0:
        overall_progress = round(
            (completed_modules / total_modules) * 100
        )

    return render(
        request,
        'dashboard.html',
        {
            'study_plan': study_plan,
            'completed_modules': completed_modules,
            'overall_progress': overall_progress
        }
    )
def logout_view(request):
    logout(request)
    return redirect('login')
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
def admin_modules(request):
    syllabuses = Syllabus.objects.all()

    return render(
        request,
        'syllabus.html',
        {
            'syllabuses': syllabuses,
            'is_admin_page': True
        }
    )
def edit_module(request, module_id):
    module = Module.objects.get(id=module_id)

    if request.method == 'POST':
        module.module_number = request.POST.get('module_number')

        topics = request.POST.get('topics')
        module.topics = [t.strip() for t in topics.split('\n') if t.strip()]

        module.save()

        return redirect('admin_modules')

    return render(
        request,
        'edit_module.html',
        {'module': module}
    )
def delete_module(request, module_id):
    module = Module.objects.get(id=module_id)
    module.delete()

    return redirect('admin_modules')

def upload_syllabus(request):
    if request.method == 'POST':
        syllabus = request.FILES.get('syllabus')
        semester = request.POST.get('semester')

        if syllabus and syllabus.name.lower().endswith('.pdf'):

            file_path = os.path.join(
                settings.MEDIA_ROOT,
                syllabus.name
            )

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

            existing = Syllabus.objects.filter(
                name=syllabus.name
            ).first()

            if existing:
                messages.warning(
                    request,
                    'This syllabus is already uploaded.'
                )
                return redirect('upload_syllabus')

            syllabus_obj = Syllabus.objects.create(
                name=syllabus.name,
                pdf=syllabus,
                semester=semester
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

        messages.error(
            request,
            'Please upload a PDF file.'
        )

    return render(request, 'upload_syllabus.html')

def syllabus(request):
    student_profile = StudentProfile.objects.get(student=request.user)

    syllabuses = Syllabus.objects.filter(
        semester=student_profile.semester
    )

    return render(request, 'syllabus.html', {
        'syllabuses': syllabuses
    })


def create_study_plan(request):

    existing_plan = StudyPlan.objects.filter(
        student=request.user
    ).last()

    if request.method == 'GET' and existing_plan:
        return render(
            request,
            'study_plan_result.html',
            {
                'schedule': existing_plan.schedule,
                'exam_date': existing_plan.exam_date,
                'daily_hours': existing_plan.daily_hours
            }
        )

    student_profile = StudentProfile.objects.get(
        student=request.user
    )

    syllabus = Syllabus.objects.filter(
        semester=student_profile.semester
    ).first()

    modules = Module.objects.filter(
        syllabus=syllabus
    )

    topic_count = sum(
        len(module.topics)
        for module in modules
    )

    suggested_hours = 2

    if topic_count > 10:
        suggested_hours = 3

    if topic_count > 20:
        suggested_hours = 4

    if request.method == 'POST':

        exam_date = request.POST.get('exam_date')
        daily_hours = request.POST.get('daily_hours')

        if exam_date and daily_hours:

            exam = date.fromisoformat(exam_date)
            today = date.today()
            remaining_days = (exam - today).days

            schedule = []

            if remaining_days > 0 and modules.exists():

                current_date = today

                for module in modules:

                    for topic in module.topics:

                        if current_date >= exam:
                            break

                        schedule.append({
                            'date': current_date.strftime('%Y-%m-%d'),
                            'module_id': module.id,
                            'module_number': module.module_number,
                            'topic': topic,
                            'hours': float(daily_hours),
                            'status': 'Pending'
                        })

                        current_date += timedelta(days=1)

            study_plan = StudyPlan.objects.create(
                student=request.user,
                syllabus=syllabus,
                exam_date=exam_date,
                daily_hours=float(daily_hours),
                schedule=schedule
            )

            return render(
                request,
                'study_plan_result.html',
                {
                    'schedule': study_plan.schedule,
                    'exam_date': study_plan.exam_date,
                    'daily_hours': study_plan.daily_hours
                }
            )

    return render(
        request,
        'create_study_plan.html',
        {
            'suggested_hours': suggested_hours
        }
    )
def new_study_plan(request):
    syllabus = Syllabus.objects.first()
    modules = Module.objects.filter(syllabus=syllabus)

    topic_count = sum(len(module.topics) for module in modules)

    suggested_hours = 2

    if topic_count > 10:
        suggested_hours = 3

    if topic_count > 20:
        suggested_hours = 4

    return render(
        request,
        'create_study_plan.html',
        {'suggested_hours': suggested_hours}
    )      
def question_bank(request):

    if request.user.is_staff:
        modules = Module.objects.all().order_by('module_number')
    else:
        student_profile = StudentProfile.objects.get(
            student=request.user
        )

        modules = Module.objects.filter(
            syllabus__semester=student_profile.semester
        ).order_by('module_number')

    return render(
        request,
        'question_bank.html',
        {'modules': modules}
    )
def module_questions(request, module_id):
    module = Module.objects.get(id=module_id)
    mcqs = MCQ.objects.filter(module=module)

    return render(
        request,
        'module_questions.html',
        {
            'module': module,
            'mcqs': mcqs
        }
    )
def module_detail(request, module_id):
    module = Module.objects.get(id=module_id)

    return render(
        request,
        'module_detail.html',
        {'module': module}
    )
def mock_test(request, module_id):
    module = Module.objects.get(id=module_id)

    # Check whether module is unlocked
    if module.module_number > 1:
        previous_module = Module.objects.get(
            module_number=module.module_number - 1
        )

        previous_progress = ModuleProgress.objects.filter(
            student=request.user,
            module=previous_module
        ).first()

        if not previous_progress or not previous_progress.passed:
            return redirect('take_test')

    mcqs = MCQ.objects.filter(module=module)

    if request.method == 'POST':
        score = 0

        for mcq in mcqs:
            selected_answer = request.POST.get(
                f'question_{mcq.id}'
            )

            if selected_answer == mcq.correct_answer:
                score += 1

        progress, created = ModuleProgress.objects.get_or_create(
            student=request.user,
            module=module
        )

        progress.score = score

        percentage = (score / mcqs.count()) * 100
        passed = percentage >= 75

        progress.passed = passed
        progress.completed = True
        progress.save()

        return render(
            request,
            'mock_test_result.html',
            {
                'module': module,
                'score': score,
                'total': mcqs.count(),
                'percentage': percentage,
                'passed': passed
            }
        )

    return render(
        request,
        'mock_test.html',
        {
            'module': module,
            'mcqs': mcqs
        }
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
def edit_mcq(request, mcq_id):
    mcq = MCQ.objects.get(id=mcq_id)
    modules = Module.objects.all()

    if request.method == 'POST':
        mcq.module_id = request.POST.get('module')
        mcq.question = request.POST.get('question')
        mcq.option1 = request.POST.get('option1')
        mcq.option2 = request.POST.get('option2')
        mcq.option3 = request.POST.get('option3')
        mcq.option4 = request.POST.get('option4')
        mcq.correct_answer = request.POST.get('correct_answer')

        mcq.save()

        return redirect('module_questions', module_id=mcq.module.id)

    return render(
        request,
        'edit_mcq.html',
        {
            'mcq': mcq,
            'modules': modules
        }
    )
def delete_mcq(request, mcq_id):
    mcq = MCQ.objects.get(id=mcq_id)
    module_id = mcq.module.id

    mcq.delete()

    return redirect('module_questions', module_id=module_id)

def take_test(request):
    student_profile = StudentProfile.objects.get(student=request.user)

    modules = Module.objects.filter(
        syllabus__semester=student_profile.semester
    ).order_by('module_number')

    unlocked_modules = []

    for module in modules:

        progress = ModuleProgress.objects.filter(
            student=request.user,
            module=module
        ).first()

        if module.module_number == 1:
            if progress and progress.completed:
                unlocked_modules.append(module)

        else:
            previous_module = Module.objects.get(
                syllabus=module.syllabus,
                module_number=module.module_number - 1
            )

            previous_progress = ModuleProgress.objects.filter(
                student=request.user,
                module=previous_module
            ).first()

            if previous_progress and previous_progress.passed:
                unlocked_modules.append(module)

    return render(
        request,
        'take_test.html',
        {
            'modules': modules,
            'unlocked_modules': unlocked_modules
        }
    )
def admin_progress(request):
    students = User.objects.filter(is_staff=False)

    progress_data = []

    for student in students:
        progress = ModuleProgress.objects.filter(student=student)

        total_modules = progress.count()
        completed_modules = progress.filter(completed=True).count()

        if total_modules:
            percentage = round((completed_modules / total_modules) * 100)
        else:
            percentage = 0

        progress_data.append({
            'student': student,
            'total_modules': total_modules,
            'completed_modules': completed_modules,
            'percentage': percentage,
        })

    return render(request, 'admin_progress.html', {
        'progress_data': progress_data
    })
def progress(request):
    student_profile = StudentProfile.objects.get(student=request.user)

    modules = Module.objects.filter(
        syllabus__semester=student_profile.semester
    ).order_by('module_number')

    progress_data = []

    for module in modules:
        item = ModuleProgress.objects.filter(
            student=request.user,
            module=module
        ).first()

        if item:
            total = module.mcqs.count()
            item.percentage = round(
                (item.score / total) * 100
            ) if total else 0
        else:
            item = ModuleProgress(
                module=module,
                score=0,
                completed=False,
                passed=False
            )
            item.percentage = 0

        progress_data.append(item)

    return render(
        request,
        'progress.html',
        {'progress_data': progress_data}
    )
def complete_topic(request, module_id, topic):

    module = Module.objects.get(id=module_id)

    progress, created = ModuleProgress.objects.get_or_create(
        student=request.user,
        module=module
    )

    completed_topics = list(progress.completed_topics)

    if topic not in completed_topics:
        completed_topics.append(topic)

    progress.completed_topics = completed_topics

    progress.completed = all(
        t in completed_topics
        for t in module.topics
    )

    progress.save()

    study_plan = StudyPlan.objects.filter(
        student=request.user
    ).last()

    if study_plan:

        schedule = study_plan.schedule

        progresses = ModuleProgress.objects.filter(
            student=request.user
        )

        completed_map = {
            p.module_id: set(p.completed_topics)
            for p in progresses
        }

        for item in schedule:

            if item['topic'] in completed_map.get(
                item['module_id'], set()
            ):
                item['status'] = 'Completed'
            else:
                item['status'] = 'Pending'

        study_plan.schedule = schedule
        study_plan.save()

    return redirect('create_study_plan')
def edit_study_plan(request):
    study_plan = StudyPlan.objects.filter(
        student=request.user
    ).last()

    if request.method == 'POST':
        exam_date = request.POST.get('exam_date')
        daily_hours = request.POST.get('daily_hours')

        study_plan.exam_date = exam_date
        study_plan.daily_hours = daily_hours

        syllabus = study_plan.syllabus
        modules = Module.objects.filter(
            syllabus=syllabus
        ).order_by('module_number')

        exam = date.fromisoformat(exam_date)
        today = date.today()

        old_schedule = study_plan.schedule
        schedule = []
        current_date = today

        for module in modules:

            progress = ModuleProgress.objects.filter(
                student=request.user,
                module=module
            ).first()

            completed_topics = []

            if progress:
                completed_topics = progress.completed_topics

            for topic in module.topics:

                if current_date >= exam:
                    break

                status = (
                    'Completed'
                    if topic in completed_topics
                    else 'Pending'
                )

                schedule.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'module_id': module.id,
                    'module_number': module.module_number,
                    'topic': topic,
                    'hours': float(daily_hours),
                    'status': status
                })

                current_date += timedelta(days=1)

        study_plan.schedule = schedule
        study_plan.save()

        return redirect('create_study_plan')

    return render(
        request,
        'edit_study_plan.html',
        {
            'study_plan': study_plan
        }
    )
def reschedule_topic(request):

    study_plan = StudyPlan.objects.filter(
        student=request.user
    ).last()

    if not study_plan:
        return redirect('create_study_plan')

    schedule = study_plan.schedule
    exam_date = study_plan.exam_date

    module_id = int(request.GET.get('module_id'))
    topic = request.GET.get('topic')

    for item in schedule:

        if (
            item['module_id'] == module_id
            and item['topic'] == topic
        ):

            original_date = date.fromisoformat(
                item['date']
            )

            new_date = original_date + timedelta(days=1)

            if new_date < exam_date:
                item['date'] = new_date.strftime('%Y-%m-%d')
                item['status'] = 'Pending'

            break

    study_plan.schedule = schedule
    study_plan.save()

    return redirect('create_study_plan')
def admin_modules(request):
    syllabuses = Syllabus.objects.all()
    return render(request, 'syllabus.html', {
        'syllabuses': syllabuses,
        'is_admin_page': True
    })
def manage_students(request):
    students = User.objects.filter(
        is_staff=False
    ).order_by('username')

    return render(
        request,
        'manage_students.html',
        {'students': students}
    )
def delete_student(request, student_id):
    student = User.objects.get(id=student_id)
    student.delete()
    return redirect('manage_students')
def profile(request):
    if request.method == 'POST':
        request.user.email = request.POST.get('email')
        request.user.save()

    return render(request, 'profile.html', {'user': request.user})
def reports(request):
    study_plan = StudyPlan.objects.filter(
        student=request.user
    ).last()

    if study_plan:
        modules = Module.objects.filter(
            syllabus=study_plan.syllabus
        ).order_by('module_number')
    else:
        modules = Module.objects.all().order_by('module_number')

    progress = []

    for module in modules:
        item, created = ModuleProgress.objects.get_or_create(
            student=request.user,
            module=module
        )
        progress.append(item)

    if progress:
        overall_percentage = round(
            sum(item.score for item in progress) / len(progress)
        )
    else:
        overall_percentage = 0

    if overall_percentage >= 90:
        overall_status = "Very Good"
    elif overall_percentage >= 85:
        overall_status = "Good"
    elif overall_percentage >= 80:
        overall_status = "Above Average"
    elif overall_percentage >= 75:
        overall_status = "Bad"
    else:
        overall_status = "Very Bad"

    return render(
        request,
        'reports.html',
        {
            'progress': progress,
            'overall_percentage': overall_percentage,
            'overall_status': overall_status
        }
    )