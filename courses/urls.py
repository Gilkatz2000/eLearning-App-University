from django.urls import path
from . import views

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("create/", views.create_course, name="create_course"),
    path("<int:course_id>/", views.course_detail, name="course_detail"),
    path("<int:course_id>/enroll/", views.enroll_course, name="enroll_course"),
    path("<int:course_id>/upload/", views.upload_material, name="upload_material"),

    path("<int:course_id>/feedback/", views.submit_feedback, name="submit_feedback"),
    path("teacher/courses/<int:course_id>/feedback/", views.teacher_course_feedback, name="teacher_course_feedback"),
    
    path("<int:course_id>/enrollments/", views.manage_enrollments, name="manage_enrollments"),
    path("<int:course_id>/enrollments/<int:enrollment_id>/block/", views.block_student, name="block_student"),
    path("<int:course_id>/enrollments/<int:enrollment_id>/unblock/", views.unblock_student, name="unblock_student"),
    path("<int:course_id>/enrollments/<int:enrollment_id>/remove/", views.remove_student, name="remove_student"),
    
    path("<int:course_id>/materials/<int:material_id>/download/", views.download_material, name="download_material"),
]
