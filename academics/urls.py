"""
URL configuration for the academics app.
"""

from django.urls import path
from .views import CourseListView, CourseDetailView, UploadCourseDocumentView

app_name = "academics"

urlpatterns = [
    # Course endpoints
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    # Document upload endpoint
    path('course/documents/upload/', UploadCourseDocumentView.as_view(), name='document_upload'),
]
