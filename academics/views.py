"""
Views for the academics app.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Course, UploadCourseDocuments
from .serializers import CourseSerializer, CourseListSerializer, UploadCourseDocumentsSerializer


class CourseListView(generics.ListAPIView):
    """
    API view for listing courses.
    
    GET: List all courses
    """

    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="List all courses",
        description="Retrieve a list of all available courses.",
        responses={
            200: CourseListSerializer(many=True),
        },
        tags=['Academics']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a course.
    
    GET: Retrieve course details
    PUT/PATCH: Update course
    DELETE: Delete course
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Get course details",
        description="Retrieve detailed information about a specific course.",
        responses={
            200: CourseSerializer,
            404: "Not Found - Course does not exist"
        },
        tags=['Academics']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update course",
        description="Update course information (full update).",
        request=CourseSerializer,
        responses={
            200: CourseSerializer,
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Course does not exist"
        },
        tags=['Academics']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update course",
        description="Partially update course information.",
        request=CourseSerializer,
        responses={
            200: CourseSerializer,
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Course does not exist"
        },
        tags=['Academics']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete course",
        description="Delete a course.",
        responses={
            204: "No Content - Course deleted successfully",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Course does not exist"
        },
        tags=['Academics']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class UploadCourseDocumentView(generics.CreateAPIView):
    """
    API view for uploading course documents.
    
    POST: Upload a document for a course (creates course if it doesn't exist)
    """

    queryset = UploadCourseDocuments.objects.all()
    serializer_class = UploadCourseDocumentsSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Upload course document",
        description="Upload a document for a course. Automatically creates the course if it doesn't exist based on course_name.",
        request=UploadCourseDocumentsSerializer,
        responses={
            201: UploadCourseDocumentsSerializer,
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required"
        },
        tags=['Academics']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
