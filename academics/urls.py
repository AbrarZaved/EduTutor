"""
URL configuration for the academics app.
"""

from django.urls import path
from .views import CourseListCreateView, CourseDetailView, UploadCourseDocumentView

app_name = "academics"

urlpatterns = [
    # Course endpoints
    path('courses/', CourseListCreateView.as_view(), name='course_list_create'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    # Document upload endpoint
    path('documents/upload/', UploadCourseDocumentView.as_view(), name='document_upload'),
]
