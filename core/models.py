from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    SEMESTER_CHOICES = [
        ('S1', 'Semester 1'),
        ('S2', 'Semester 2'),
    ]

    student = models.OneToOneField(User, on_delete=models.CASCADE)
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES)

    def __str__(self):
        return self.student.username


class Syllabus(models.Model):
    SEMESTER_CHOICES = [
        ('S1', 'Semester 1'),
        ('S2', 'Semester 2'),
    ]

    name = models.CharField(max_length=255, unique=True)
    pdf = models.FileField(upload_to='syllabus/')
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class Module(models.Model):
    syllabus = models.ForeignKey(
        Syllabus,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    module_number = models.IntegerField()
    topics = models.JSONField(default=list)

    def __str__(self):
        return f"Module {self.module_number}"


class StudyPlan(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE)
    exam_date = models.DateField()
    daily_hours = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    schedule = models.JSONField(default=list)
    def __str__(self):
        return f"{self.student.username} - Study Plan"


class MCQ(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='mcqs'
    )
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return self.question


class ModuleProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    completed_topics = models.JSONField(default=list)

    def __str__(self):
        return f"{self.student.username} - Module {self.module.module_number}"
    