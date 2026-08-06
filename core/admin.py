from django.contrib import admin
from .models import Syllabus, Module, StudyPlan, MCQ, ModuleProgress

admin.site.register(Syllabus)
admin.site.register(Module)
admin.site.register(StudyPlan)
admin.site.register(MCQ)
admin.site.register(ModuleProgress)