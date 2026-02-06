from django.contrib import admin

# Register your models here.

from .models import Skills, Lesson, Units, Course, UploadCourseDocuments, Class, Quiz, QuizQuestion, StudentQuizAttempt

@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'duration', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

@admin.register(Units)
class UnitsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(UploadCourseDocuments)
class UploadCourseDocumentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'document', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('course__name',)
    ordering = ('-uploaded_at',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'course', 'created_at')
    search_fields = ('question_text', 'course__name')
    ordering = ('-created_at',)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'passing_score', 'created_at')
    search_fields = ('course__name',)
    ordering = ('-created_at',)

@admin.register(StudentQuizAttempt)
class StudentQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'quiz', 'score', 'grade', 'progress_percentage', 'attempted_at')
    list_filter = ('grade', 'attempted_at')
    search_fields = ('student__email', 'quiz__name')
    ordering = ('-attempted_at',)
    readonly_fields = ('grade', 'progress_percentage', 'attempted_at')