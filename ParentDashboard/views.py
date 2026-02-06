"""
Views for ParentDashboard app.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import ParentStudent
from .serializers import (
    StudentSearchSerializer,
    ParentStudentSerializer,
    LinkStudentSerializer,
    ChildProgressSerializer,
    ChildListSerializer,
)
from academics.models import StudentQuizAttempt, Quiz

User = get_user_model()


class SearchStudentView(generics.ListAPIView):
    """
    API view for searching students by ID or email.
    
    GET: Search for students (admin/parent access)
    """
    
    serializer_class = StudentSearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Search students",
        description="Search for students by ID or email. Accessible to parents and admins.",
        parameters=[
            OpenApiParameter(
                name='student_id',
                description='Student ID to search for',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='email',
                description='Student email to search for (partial match supported)',
                required=False,
                type=str
            ),
        ],
        responses={
            200: StudentSearchSerializer(many=True),
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Only parents and admins can search"
        },
        tags=['Parent Dashboard']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter students based on search criteria."""
        # Check permissions
        user = self.request.user
        if user.role not in ['parent', 'school_admin']:
            return User.objects.none()
        
        student_id = self.request.query_params.get('student_id')
        email = self.request.query_params.get('email')
        
        queryset = User.objects.filter(role='student')
        
        if student_id:
            queryset = queryset.filter(id=student_id)
        
        if email:
            queryset = queryset.filter(email__icontains=email)
        
        return queryset


class LinkStudentView(APIView):
    """
    API view for linking a student to parent.
    
    POST: Link a student to the authenticated parent
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Link student to parent",
        description="Link a student to the authenticated parent by student ID or email.",
        request=LinkStudentSerializer,
        responses={
            201: ParentStudentSerializer,
            400: "Bad Request - Invalid data",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Only parents can link students"
        },
        tags=['Parent Dashboard']
    )
    def post(self, request):
        # Check if user is a parent
        if request.user.role != 'parent':
            return Response(
                {'error': 'Only parents can link students.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = LinkStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Find student
        student_id = serializer.validated_data.get('student_id')
        student_email = serializer.validated_data.get('student_email')
        relationship = serializer.validated_data.get('relationship', 'guardian')
        
        try:
            if student_id:
                student = User.objects.get(id=student_id, role='student')
            else:
                student = User.objects.get(email=student_email, role='student')
        except User.DoesNotExist:
            return Response(
                {'error': 'Student not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already linked
        existing = ParentStudent.objects.filter(
            parent=request.user,
            student=student
        ).first()
        
        if existing:
            if existing.is_active:
                return Response(
                    {'error': 'Student is already linked to your account.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Reactivate the link
                existing.is_active = True
                existing.relationship = relationship
                existing.save()
                response_serializer = ParentStudentSerializer(existing)
                return Response(
                    {
                        'message': 'Student link reactivated successfully.',
                        'data': response_serializer.data
                    },
                    status=status.HTTP_200_OK
                )
        
        # Create new link
        parent_student = ParentStudent.objects.create(
            parent=request.user,
            student=student,
            relationship=relationship
        )
        
        response_serializer = ParentStudentSerializer(parent_student)
        return Response(
            {
                'message': 'Student linked successfully.',
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class MyChildrenListView(generics.ListAPIView):
    """
    API view for listing parent's children.
    
    GET: List all children linked to the authenticated parent
    """
    
    serializer_class = ChildListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List my children",
        description="Get a list of all children linked to the authenticated parent with quick stats.",
        responses={
            200: ChildListSerializer(many=True),
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Only parents can access"
        },
        tags=['Parent Dashboard']
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def get_queryset(self):
        """Return children with basic stats."""
        # Check if user is a parent
        if self.request.user.role != 'parent':
            return []
        
        relationships = ParentStudent.objects.filter(
            parent=self.request.user,
            is_active=True
        ).select_related('student')
        
        children_data = []
        
        for rel in relationships:
            student = rel.student
            
            # Get quiz stats (dummy data for courses)
            quiz_attempts = StudentQuizAttempt.objects.filter(student=student)
            total_attempts = quiz_attempts.count()
            avg_score = quiz_attempts.aggregate(Avg('progress_percentage'))['progress_percentage__avg'] or 0
            
            children_data.append({
                'relationship_id': rel.id,
                'student_id': student.id,
                'student_name': f"{student.first_name} {student.last_name}".strip() or student.email,
                'student_email': student.email,
                'relationship': rel.get_relationship_display(),
                'linked_at': rel.linked_at,
                'total_courses': 5,  # Dummy data
                'quizzes_attempted': total_attempts,
                'average_score': round(avg_score, 2)
            })
        
        return children_data
    
    def list(self, request, *args, **kwargs):
        """Return children data."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ChildProgressView(APIView):
    """
    API view for viewing a child's detailed progress.
    
    GET: Get detailed progress for a specific child
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get child's progress",
        description="Get detailed progress information for a specific child including course enrollment, quiz performance, and overall progression.",
        parameters=[
            OpenApiParameter(
                name='student_id',
                description='Student ID',
                required=True,
                type=int,
                location=OpenApiParameter.PATH
            ),
        ],
        responses={
            200: ChildProgressSerializer,
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Can only view your own children's progress",
            404: "Not Found - Student not found or not linked"
        },
        tags=['Parent Dashboard']
    )
    def get(self, request, student_id):
        # Check if user is a parent
        if request.user.role != 'parent':
            return Response(
                {'error': 'Only parents can view child progress.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify the student is linked to this parent
        try:
            relationship = ParentStudent.objects.get(
                parent=request.user,
                student_id=student_id,
                is_active=True
            )
            student = relationship.student
        except ParentStudent.DoesNotExist:
            return Response(
                {'error': 'Student not found or not linked to your account.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get quiz performance
        quiz_attempts = StudentQuizAttempt.objects.filter(
            student=student
        ).select_related('quiz', 'quiz__course')
        
        total_quizzes = quiz_attempts.count()
        
        # Calculate pass/fail
        passed = 0
        failed = 0
        for attempt in quiz_attempts:
            if attempt.progress_percentage >= attempt.quiz.passing_score:
                passed += 1
            else:
                failed += 1
        
        # Average score
        avg_score = quiz_attempts.aggregate(
            Avg('progress_percentage')
        )['progress_percentage__avg'] or 0
        
        # Recent quiz attempts
        recent_attempts = quiz_attempts.order_by('-attempted_at')[:5]
        recent_data = [
            {
                'quiz_name': attempt.quiz.name,
                'course_name': attempt.quiz.course.name,
                'score': attempt.score,
                'grade': attempt.grade,
                'percentage': attempt.progress_percentage,
                'attempted_at': attempt.attempted_at,
                'passed': attempt.progress_percentage >= attempt.quiz.passing_score
            }
            for attempt in recent_attempts
        ]
        
        # Dummy course data (to be replaced with actual enrollment model later)
        dummy_courses = [
            {
                'course_id': 1,
                'course_name': 'Mathematics Grade 8',
                'enrollment_date': '2026-01-15',
                'completion_percentage': 65.5,
                'lessons_completed': 15,
                'total_lessons': 23
            },
            {
                'course_id': 2,
                'course_name': 'English Language Arts',
                'enrollment_date': '2026-01-15',
                'completion_percentage': 78.0,
                'lessons_completed': 20,
                'total_lessons': 26
            },
            {
                'course_id': 3,
                'course_name': 'General Science',
                'enrollment_date': '2026-01-20',
                'completion_percentage': 45.0,
                'lessons_completed': 9,
                'total_lessons': 20
            },
        ]
        
        # Prepare response
        progress_data = {
            'student_id': student.id,
            'student_name': f"{student.first_name} {student.last_name}".strip() or student.email,
            'student_email': student.email,
            'total_courses_enrolled': len(dummy_courses),
            'courses': dummy_courses,
            'total_quizzes_attempted': total_quizzes,
            'quizzes_passed': passed,
            'quizzes_failed': failed,
            'average_score': round(avg_score, 2),
            'recent_quiz_attempts': recent_data,
            'overall_completion_percentage': 62.8  # Dummy data
        }
        
        serializer = ChildProgressSerializer(progress_data)
        return Response(serializer.data)


class UnlinkStudentView(APIView):
    """
    API view for unlinking a student from parent.
    
    DELETE: Unlink a student from the authenticated parent
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Unlink student from parent",
        description="Deactivate the link between a student and the authenticated parent.",
        parameters=[
            OpenApiParameter(
                name='student_id',
                description='Student ID to unlink',
                required=True,
                type=int,
                location=OpenApiParameter.PATH
            ),
        ],
        responses={
            200: "Student unlinked successfully",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Only parents can unlink students",
            404: "Not Found - Student link not found"
        },
        tags=['Parent Dashboard']
    )
    def delete(self, request, student_id):
        # Check if user is a parent
        if request.user.role != 'parent':
            return Response(
                {'error': 'Only parents can unlink students.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Find the relationship
        try:
            relationship = ParentStudent.objects.get(
                parent=request.user,
                student_id=student_id,
                is_active=True
            )
        except ParentStudent.DoesNotExist:
            return Response(
                {'error': 'Student link not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Deactivate instead of delete
        relationship.is_active = False
        relationship.save()
        
        return Response(
            {'message': 'Student unlinked successfully.'},
            status=status.HTTP_200_OK
        )

