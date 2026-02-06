"""
Models for ParentDashboard app.

This module defines models to manage parent-student relationships and tracking.
"""

from django.db import models
from django.conf import settings


class ParentStudent(models.Model):
    """
    Model to link parents with their children (students).
    
    A parent can have multiple children, and a student can have multiple parents.
    """
    
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='children',
        limit_choices_to={'role': 'parent'}
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parents',
        limit_choices_to={'role': 'student'}
    )
    relationship = models.CharField(
        max_length=50,
        choices=[
            ('father', 'Father'),
            ('mother', 'Mother'),
            ('guardian', 'Guardian'),
            ('other', 'Other'),
        ],
        default='guardian'
    )
    
    is_active = models.BooleanField(default=True)
    linked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Parent-Student Relationship"
        verbose_name_plural = "Parent-Student Relationships"
        unique_together = ['parent', 'student']
        ordering = ['-linked_at']

    def __str__(self):
        return f"{self.parent.email} - {self.student.email} ({self.relationship})"

