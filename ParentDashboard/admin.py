from django.contrib import admin
from .models import ParentStudent


@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent', 'student', 'relationship', 'is_active', 'linked_at')
    list_filter = ('relationship', 'is_active', 'linked_at')
    search_fields = ('parent__email', 'student__email', 'parent__first_name', 'student__first_name')
    readonly_fields = ('linked_at', 'updated_at')
    ordering = ('-linked_at',)
    
    fieldsets = (
        ('Relationship', {
            'fields': ('parent', 'student', 'relationship')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('linked_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

