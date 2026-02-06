"""
URL configuration for the academics app.
"""

from django.urls import path
from .views import (
    CourseListView,
    CourseDetailView,
    UploadCourseDocumentView,
    ClassListCreateView,
    ClassDetailView,
    QuizQuestionListView,
    QuizQuestionDetailView,
    QuizQuestionCreateView,
    QuizQuestionByCourseView,
    QuizListView,
    QuizDetailView,
    QuizCreateView,
    QuizUpdateView,
    QuizDeleteView,
    QuizByCourseView,
    QuizByClassView,
    QuizSubmitView,
    StudentQuizResultView,
    StudentQuizPerformanceView,
)

app_name = "academics"

urlpatterns = [
    # Course endpoints
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    # Document upload endpoint
    path('course/documents/upload/', UploadCourseDocumentView.as_view(), name='document_upload'),
    # Class endpoints
    path('classes/', ClassListCreateView.as_view(), name='class_list_create'),
    path('classes/<int:pk>/', ClassDetailView.as_view(), name='class_detail'),
    
    # Quiz Question endpoints
    path('quiz-questions/', QuizQuestionListView.as_view(), name='quiz_question_list'),
    path('quiz-questions/create/', QuizQuestionCreateView.as_view(), name='quiz_question_create'),
    path('quiz-questions/<int:pk>/', QuizQuestionDetailView.as_view(), name='quiz_question_detail'),
    path('quiz-questions/course/<int:course_id>/', QuizQuestionByCourseView.as_view(), name='quiz_questions_by_course'),
    
    # Quiz endpoints
    path('quizzes/', QuizListView.as_view(), name='quiz_list'),
    path('quizzes/create/', QuizCreateView.as_view(), name='quiz_create'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz_detail'),
    path('quizzes/<int:pk>/update/', QuizUpdateView.as_view(), name='quiz_update'),
    path('quizzes/<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz_delete'),
    path('quizzes/course/<int:course_id>/', QuizByCourseView.as_view(), name='quizzes_by_course'),
    path('quizzes/class/<int:class_id>/', QuizByClassView.as_view(), name='quizzes_by_class'),
    
    # Quiz submission endpoints
    path('quizzes/submit/', QuizSubmitView.as_view(), name='quiz_submit'),
    path('quiz-attempts/', StudentQuizResultView.as_view(), name='student_quiz_attempts'),
    path('quiz-performance/', StudentQuizPerformanceView.as_view(), name='student_quiz_performance'),
]

