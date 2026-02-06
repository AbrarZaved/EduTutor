"""
Views for the academics app.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Course, UploadCourseDocuments, Class, QuizQuestion, Quiz, StudentQuizAttempt
from .serializers import (
    CourseSerializer,
    CourseListSerializer,
    UploadCourseDocumentsSerializer,
    ClassSerializer,
    ClassListSerializer,
    QuizQuestionSerializer,
    QuizQuestionCreateSerializer,
    QuizQuestionListSerializer,
    QuizSerializer,
    QuizCreateSerializer,
    QuizListSerializer,
    QuizUpdateSerializer,
    QuizSubmissionSerializer,
    QuizSubmissionResponseSerializer,
    StudentQuizAttemptSerializer,
    QuizPerformanceSerializer,
)


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


class ClassListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating classes.
    
    GET: List all classes
    POST: Create a new class
    """

    queryset = Class.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClassSerializer
        return ClassListSerializer

    @extend_schema(
        summary="List all classes",
        description="Retrieve a list of all available classes.",
        responses={
            200: ClassListSerializer(many=True),
        },
        tags=['Academics']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new class",
        description="Create a new class with associated courses.",
        request=ClassSerializer,
        responses={
            201: ClassSerializer,
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required"
        },
        tags=['Academics']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a class.
    
    GET: Retrieve class details
    PUT/PATCH: Update class
    DELETE: Delete class
    """

    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Get class details",
        description="Retrieve detailed information about a specific class.",
        responses={
            200: ClassSerializer,
            404: "Not Found - Class does not exist"
        },
        tags=['Academics']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update class",
        description="Update class information (full update).",
        request=ClassSerializer,
        responses={
            200: ClassSerializer,
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Class does not exist"
        },
        tags=['Academics']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update class",
        description="Partially update class information.",
        request=ClassSerializer,
        responses={
            200: ClassSerializer,
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Class does not exist"
        },
        tags=['Academics']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete class",
        description="Delete a class.",
        responses={
            204: "No Content - Class deleted successfully",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Class does not exist"
        },
        tags=['Academics']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# ============================================================================
# QuizQuestion Views
# ============================================================================


class QuizQuestionListView(generics.ListAPIView):
    """
    API view for listing quiz questions.
    
    GET: List all quiz questions
    """

    queryset = QuizQuestion.objects.all().select_related('course')
    serializer_class = QuizQuestionListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="List all quiz questions",
        description="Retrieve a list of all quiz questions.",
        responses={
            200: QuizQuestionListSerializer(many=True),
        },
        tags=['Quiz']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class QuizQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a quiz question.
    
    GET: Retrieve quiz question details
    PUT/PATCH: Update quiz question
    DELETE: Delete quiz question
    """

    queryset = QuizQuestion.objects.all().select_related('course')
    serializer_class = QuizQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Get quiz question details",
        description="Retrieve detailed information about a specific quiz question.",
        responses={
            200: QuizQuestionSerializer,
            404: "Not Found - Quiz question does not exist"
        },
        tags=['Quiz']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update quiz question",
        description="Update quiz question information (full update).",
        request=QuizQuestionSerializer,
        responses={
            200: QuizQuestionSerializer,
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Quiz question does not exist"
        },
        tags=['Quiz']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update quiz question",
        description="Partially update quiz question information.",
        request=QuizQuestionSerializer,
        responses={
            200: QuizQuestionSerializer,
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Quiz question does not exist"
        },
        tags=['Quiz']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete quiz question",
        description="Delete a quiz question.",
        responses={
            204: "No Content - Quiz question deleted successfully",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Quiz question does not exist"
        },
        tags=['Quiz']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class QuizQuestionCreateView(generics.CreateAPIView):
    """
    API view for creating quiz questions.
    
    POST: Create a new quiz question
    """

    serializer_class = QuizQuestionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Create quiz question",
        description="Create a new quiz question for a course.",
        request=QuizQuestionCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="Quiz question created successfully",
                response=QuizQuestionSerializer,
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required"
        },
        tags=['Quiz']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()
        
        return Response(
            {
                "message": "Quiz question created successfully.",
                "question": QuizQuestionSerializer(question).data,
            },
            status=status.HTTP_201_CREATED,
        )


class QuizQuestionByCourseView(generics.ListAPIView):
    """
    API view for listing quiz questions by course.
    
    GET: List all quiz questions for a specific course
    """

    serializer_class = QuizQuestionListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="List quiz questions by course",
        description="Retrieve a list of all quiz questions for a specific course.",
        responses={
            200: QuizQuestionListSerializer(many=True),
            404: "Not Found - Course does not exist"
        },
        tags=['Quiz']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Filter questions by course ID from URL."""
        course_id = self.kwargs.get('course_id')
        return QuizQuestion.objects.filter(course_id=course_id).select_related('course')


# ============================================================================
# Quiz Views
# ============================================================================


class QuizListView(generics.ListAPIView):
    """
    API view for listing quizzes.
    
    GET: List all quizzes
    """

    queryset = Quiz.objects.all().select_related('course', 'class_name', 'created_by').prefetch_related('questions')
    serializer_class = QuizListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="List all quizzes",
        description="Retrieve a list of all available quizzes.",
        responses={
            200: QuizListSerializer(many=True),
        },
        tags=['Quiz']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class QuizDetailView(generics.RetrieveAPIView):
    """
    API view for retrieving quiz details.
    
    GET: Retrieve quiz details with all questions
    """

    queryset = Quiz.objects.all().select_related('course', 'class_name', 'created_by').prefetch_related('questions')
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Get quiz details",
        description="Retrieve detailed information about a specific quiz including all questions.",
        responses={
            200: QuizSerializer,
            404: "Not Found - Quiz does not exist"
        },
        tags=['Quiz']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class QuizCreateView(generics.CreateAPIView):
    """
    API view for creating quizzes.
    
    POST: Create a new quiz
    """

    serializer_class = QuizCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Create quiz",
        description="Create a new quiz for a class and course. Optionally add questions.",
        request=QuizCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="Quiz created successfully",
                response=QuizSerializer,
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required"
        },
        tags=['Quiz']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save()
        
        return Response(
            {
                "message": "Quiz created successfully.",
                "quiz": QuizSerializer(quiz).data,
            },
            status=status.HTTP_201_CREATED,
        )


class QuizUpdateView(generics.UpdateAPIView):
    """
    API view for updating quizzes.
    
    PUT/PATCH: Update quiz
    """

    queryset = Quiz.objects.all()
    serializer_class = QuizUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Update quiz",
        description="Update quiz information (name, passing score, questions).",
        request=QuizUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="Quiz updated successfully",
                response=QuizSerializer,
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Quiz does not exist"
        },
        tags=['Quiz']
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "message": "Quiz updated successfully.",
                "quiz": QuizSerializer(instance).data,
            }
        )

    @extend_schema(
        summary="Partially update quiz",
        description="Partially update quiz information.",
        request=QuizUpdateSerializer,
        responses={
            200: OpenApiResponse(
                description="Quiz updated successfully",
                response=QuizSerializer,
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Quiz does not exist"
        },
        tags=['Quiz']
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class QuizDeleteView(generics.DestroyAPIView):
    """
    API view for deleting quizzes.
    
    DELETE: Delete quiz
    """

    queryset = Quiz.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Delete quiz",
        description="Delete a quiz.",
        responses={
            204: "No Content - Quiz deleted successfully",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Quiz does not exist"
        },
        tags=['Quiz']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class QuizByCourseView(generics.ListAPIView):
    """
    API view for listing quizzes by course.
    
    GET: List all quizzes for a specific course
    """

    serializer_class = QuizListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="List quizzes by course",
        description="Retrieve a list of all quizzes for a specific course.",
        responses={
            200: QuizListSerializer(many=True),
            404: "Not Found - Course does not exist"
        },
        tags=['Quiz']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Filter quizzes by course ID from URL."""
        course_id = self.kwargs.get('course_id')
        return Quiz.objects.filter(course_id=course_id).select_related(
            'course', 'class_name', 'created_by'
        ).prefetch_related('questions')


class QuizByClassView(generics.ListAPIView):
    """
    API view for listing quizzes by class.
    
    GET: List all quizzes for a specific class
    """

    serializer_class = QuizListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="List quizzes by class",
        description="Retrieve a list of all quizzes for a specific class.",
        responses={
            200: QuizListSerializer(many=True),
            404: "Not Found - Class does not exist"
        },
        tags=['Quiz']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Filter quizzes by class ID from URL."""
        class_id = self.kwargs.get('class_id')
        return Quiz.objects.filter(class_name_id=class_id).select_related(
            'course', 'class_name', 'created_by'
        ).prefetch_related('questions')


class QuizSubmitView(generics.CreateAPIView):
    """
    API view for submitting quiz responses.
    
    POST: Submit quiz answers and receive calculated grade
    """

    serializer_class = QuizSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Submit quiz answers",
        description="Submit answers for a quiz and receive calculated score, grade, and detailed results.",
        request=QuizSubmissionSerializer,
        responses={
            201: QuizSubmissionResponseSerializer,
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Quiz does not exist"
        },
        tags=['Quiz']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create quiz attempt and calculate score
        result = serializer.save()
        
        quiz_attempt = result['quiz_attempt']
        results = result['results']
        total_points = result['total_points']
        
        # Prepare success message
        passed = quiz_attempt.progress_percentage >= quiz_attempt.quiz.passing_score
        message = f"Quiz submitted successfully! You scored {quiz_attempt.score} out of {total_points} points ({quiz_attempt.progress_percentage:.2f}%). Grade: {quiz_attempt.grade}. "
        message += "You passed!" if passed else "You did not pass. Keep trying!"
        
        # Prepare response
        response_data = {
            'attempt': StudentQuizAttemptSerializer(quiz_attempt).data,
            'results': results,
            'total_points': total_points,
            'message': message
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class StudentQuizResultView(generics.ListAPIView):
    """
    API view for listing student quiz results.
    
    GET: List all quiz results for the authenticated student
    """

    serializer_class = StudentQuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="List student quiz results",
        description="Retrieve a list of all quiz results for the authenticated student.",
        responses={
            200: StudentQuizAttemptSerializer(many=True),
            401: "Unauthorized - Authentication required"
        },
        tags=['Quiz']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Filter quiz attempts by the authenticated student."""
        return StudentQuizAttempt.objects.filter(
            student=self.request.user
        ).select_related('student', 'quiz', 'quiz__course').order_by('-attempted_at')


class StudentQuizPerformanceView(generics.ListAPIView):
    """
    API view for viewing student's performance across all quizzes.
    
    GET: Get performance overview for all quizzes (attempted and not attempted)
    """

    serializer_class = QuizPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get student quiz performance overview",
        description="Retrieve comprehensive performance data for all quizzes, including best scores, grades, and attempt history.",
        responses={
            200: QuizPerformanceSerializer(many=True),
            401: "Unauthorized - Authentication required"
        },
        tags=['Quiz']
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        """Return performance data for all quizzes."""
        student = self.request.user
        
        # Get all quizzes
        quizzes = Quiz.objects.select_related('course', 'class_name').prefetch_related('questions')
        
        performance_data = []
        
        for quiz in quizzes:
            # Get all attempts for this quiz by the student
            attempts = StudentQuizAttempt.objects.filter(
                student=student,
                quiz=quiz
            ).order_by('-attempted_at')
            
            # Calculate statistics
            total_attempts = attempts.count()
            is_attempted = total_attempts > 0
            
            if is_attempted:
                best_attempt = attempts.order_by('-score').first()
                latest_attempt = attempts.first()
                
                best_score = best_attempt.score
                best_grade = best_attempt.grade
                best_percentage = best_attempt.progress_percentage
                
                latest_score = latest_attempt.score
                latest_grade = latest_attempt.grade
                latest_percentage = latest_attempt.progress_percentage
                latest_attempt_date = latest_attempt.attempted_at
                
                has_passed = best_percentage >= quiz.passing_score
            else:
                best_score = best_grade = best_percentage = None
                latest_score = latest_grade = latest_percentage = latest_attempt_date = None
                has_passed = False
            
            # Calculate total points
            total_points = sum(q.question_point for q in quiz.questions.all())
            
            performance_data.append({
                'quiz_id': quiz.id,
                'quiz_name': quiz.name,
                'course_name': quiz.course.name,
                'class_name': quiz.class_name.name,
                'total_points': total_points,
                'passing_score': quiz.passing_score,
                'total_attempts': total_attempts,
                'best_score': best_score,
                'best_grade': best_grade,
                'best_percentage': best_percentage,
                'latest_score': latest_score,
                'latest_grade': latest_grade,
                'latest_percentage': latest_percentage,
                'latest_attempt_date': latest_attempt_date,
                'has_passed': has_passed,
                'is_attempted': is_attempted,
                'attempts': list(attempts)
            })
        
        return performance_data
    
    def list(self, request, *args, **kwargs):
        """Return the performance data."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
