from django.contrib import admin
from .models import Course, Enrollment, CourseMaterial, Feedback

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(CourseMaterial)
admin.site.register(Feedback)
