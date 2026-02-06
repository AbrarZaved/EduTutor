"""
Serializers for ParentDashboard app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ParentStudent
from academics.models import StudentQuizAttempt

User = get_user_model()


class StudentSearchSerializer(serializers.ModelSerializer):
    """Serializer for searching students."""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'phone_number']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        """Get student's full name."""
        return f"{obj.first_name} {obj.last_name}".strip() or "N/A"


class ParentStudentSerializer(serializers.ModelSerializer):
    """Serializer for parent-student relationship."""
    
    parent_email = serializers.EmailField(source='parent.email', read_only=True)
    parent_name = serializers.SerializerMethodField()
    student_email = serializers.EmailField(source='student.email', read_only=True)
    student_name = serializers.SerializerMethodField()
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    
    class Meta:
        model = ParentStudent
        fields = [
            'id',
            'parent',
            'parent_email',
            'parent_name',
            'student',
            'student_id',
            'student_email',
            'student_name',
            'relationship',
            'is_active',
            'linked_at'
        ]
        read_only_fields = ['id', 'linked_at']
    
    def get_parent_name(self, obj):
        """Get parent's full name."""
        return f"{obj.parent.first_name} {obj.parent.last_name}".strip() or obj.parent.email
    
    def get_student_name(self, obj):
        """Get student's full name."""
        return f"{obj.student.first_name} {obj.student.last_name}".strip() or obj.student.email


class LinkStudentSerializer(serializers.Serializer):
    """Serializer for linking a student to parent."""
    
    student_id = serializers.IntegerField(required=False)
    student_email = serializers.EmailField(required=False)
    relationship = serializers.ChoiceField(
        choices=[
            ('father', 'Father'),
            ('mother', 'Mother'),
            ('guardian', 'Guardian'),
            ('other', 'Other'),
        ],
        default='guardian'
    )
    
    def validate(self, attrs):
        """Validate that either student_id or student_email is provided."""
        if not attrs.get('student_id') and not attrs.get('student_email'):
            raise serializers.ValidationError(
                "Either student_id or student_email must be provided."
            )
        return attrs
    
    def validate_student_id(self, value):
        """Validate that student exists and has student role."""
        if value:
            try:
                student = User.objects.get(id=value, role='student')
            except User.DoesNotExist:
                raise serializers.ValidationError("Student with this ID does not exist.")
        return value
    
    def validate_student_email(self, value):
        """Validate that student exists and has student role."""
        if value:
            try:
                student = User.objects.get(email=value, role='student')
            except User.DoesNotExist:
                raise serializers.ValidationError("Student with this email does not exist.")
        return value


class ChildProgressSerializer(serializers.Serializer):
    """Serializer for child's progress overview."""
    
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    student_email = serializers.EmailField()
    
    # Course enrollment (dummy data for now)
    total_courses_enrolled = serializers.IntegerField()
    courses = serializers.ListField(child=serializers.DictField())
    
    # Quiz performance
    total_quizzes_attempted = serializers.IntegerField()
    quizzes_passed = serializers.IntegerField()
    quizzes_failed = serializers.IntegerField()
    average_score = serializers.FloatField()
    
    # Recent quiz attempts
    recent_quiz_attempts = serializers.ListField(child=serializers.DictField())
    
    # Overall progress (dummy for now)
    overall_completion_percentage = serializers.FloatField()


class ChildListSerializer(serializers.Serializer):
    """Serializer for listing parent's children with basic info."""
    
    relationship_id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    student_email = serializers.EmailField()
    relationship = serializers.CharField()
    linked_at = serializers.DateTimeField()
    
    # Quick stats
    total_courses = serializers.IntegerField()
    quizzes_attempted = serializers.IntegerField()
    average_score = serializers.FloatField()
