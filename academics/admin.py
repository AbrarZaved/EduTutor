from django.contrib import admin

# Register your models here.

from .models import Skills, Lesson, Units, Course, UploadCourseDocuments

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
