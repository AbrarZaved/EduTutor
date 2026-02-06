"""
URL configuration for ParentDashboard app.
"""

from django.urls import path
from .views import (
    SearchStudentView,
    LinkStudentView,
    MyChildrenListView,
    ChildProgressView,
    UnlinkStudentView,
)

app_name = "parent_dashboard"

urlpatterns = [
    # Search students
    path('students/search/', SearchStudentView.as_view(), name='search_student'),
    
    # Link/Unlink students
    path('students/link/', LinkStudentView.as_view(), name='link_student'),
    path('students/<int:student_id>/unlink/', UnlinkStudentView.as_view(), name='unlink_student'),
    
    # My children
    path('my-children/', MyChildrenListView.as_view(), name='my_children'),
    path('children/<int:student_id>/progress/', ChildProgressView.as_view(), name='child_progress'),
]
