from django.contrib import admin
from .models import StudentProfile, TeacherProfile, ParentProfile, ParentPreference
# Register your models here.

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'get_full_name')
    search_fields = ('student_id', 'user__email', 'user__first_name', 'user__last_name')


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'user', 'get_full_name', 'department', 'experience')
    search_fields = ('teacher_id', 'user__email', 'user__first_name', 'user__last_name', 'department')


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('parent_id', 'user', 'get_full_name')
    search_fields = ('parent_id', 'user__email', 'user__first_name', 'user__last_name')

@admin.register(ParentPreference)
class ParentPreferenceAdmin(admin.ModelAdmin):
    list_display = ('parent',)
