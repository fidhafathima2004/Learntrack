from django.db import models
from django.contrib.auth.models import User


class Syllabus(models.Model):
    name = models.CharField(max_length=255)
    pdf = models.FileField(upload_to='syllabus/')
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
