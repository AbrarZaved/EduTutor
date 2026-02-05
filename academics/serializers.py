"""
Serializers for the academics app.
"""

from rest_framework import serializers
from .models import Skills, Lesson, Units, Course, UploadCourseDocuments


class SkillsSerializer(serializers.ModelSerializer):
    """
    Serializer for Skills model.
    """

    class Meta:
        model = Skills
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer for Lesson model.
    """

    skills = SkillsSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skills.objects.all(),
        write_only=True,
        source='skills'
    )

    class Meta:
        model = Lesson
        fields = [
            'id',
            'title',
            'description',
            'skills',
            'skill_ids',
            'duration',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UnitsSerializer(serializers.ModelSerializer):
    """
    Serializer for Units model.
    """

    lessons = LessonSerializer(many=True, read_only=True)
    lesson_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Lesson.objects.all(),
        write_only=True,
        source='lessons'
    )

    class Meta:
        model = Units
        fields = [
            'id',
            'name',
            'description',
            'lessons',
            'lesson_ids',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for Course model.
    """

    units = UnitsSerializer(many=True, read_only=True)
    unit_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Units.objects.all(),
        write_only=True,
        source='units'
    )

    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'description',
            'units',
            'unit_ids',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for Course listing.
    """

    units_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'description',
            'units_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_units_count(self, obj):
        """Get the total number of units in this course."""
        return obj.units.count()


class UploadCourseDocumentsSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading course documents.
    Creates course if it doesn't exist.
    """

    course_name = serializers.CharField(write_only=True, required=True)
    course_description = serializers.CharField(write_only=True, required=False, allow_blank=True)
    course_details = CourseListSerializer(source='course', read_only=True)

    class Meta:
        model = UploadCourseDocuments
        fields = [
            'id',
            'course_name',
            'course_description',
            'course_details',
            'document',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']

    def create(self, validated_data):
        """Create or get course and upload document."""
        course_name = validated_data.pop('course_name')
        course_description = validated_data.pop('course_description', '')

        # Get or create course by name
        course, created = Course.objects.get_or_create(
            name=course_name,
            defaults={'description': course_description}
        )

        # Create document upload
        validated_data['course'] = course
        return super().create(validated_data)
