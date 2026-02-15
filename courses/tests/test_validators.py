from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from courses.models import Course, CourseMaterial
from tests.helpers import make_teacher

class CourseMaterialValidatorTests(TestCase):
    def setUp(self):
        self.teacher = make_teacher("alice", "pass")
        self.course = Course.objects.create(teacher=self.teacher, title="Validators", description="x")

    def test_rejects_disallowed_file_extension(self):
        bad_file = SimpleUploadedFile("malware.exe", b"1234", content_type="application/octet-stream")
        material = CourseMaterial(course=self.course, uploaded_by=self.teacher, title="Bad", file=bad_file)

        with self.assertRaises(ValidationError):
            material.full_clean()

    def test_allows_pdf_upload(self):
        good_file = SimpleUploadedFile("notes.pdf", b"%PDF-1.4 fake", content_type="application/pdf")
        material = CourseMaterial(course=self.course, uploaded_by=self.teacher, title="Good", file=good_file)

        # should not raise
        material.full_clean()
