from django.core.exceptions import PermissionDenied

def teacher_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_teacher():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped


def student_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_student():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped
