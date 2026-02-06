"""
Serializers for the academics app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Skills, Lesson, Units, Course, UploadCourseDocuments, Class, QuizQuestion, Quiz, StudentQuizAttempt

User = get_user_model()


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


class ClassSerializer(serializers.ModelSerializer):
    """
    Serializer for Class model.
    """

    course = CourseListSerializer(many=True, read_only=True)
    course_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Course.objects.all(),
        write_only=True,
        source='course'
    )

    class Meta:
        model = Class
        fields = [
            'id',
            'name',
            'learning_objectives',
            'course',
            'course_ids',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClassListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for Class listing.
    """

    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = [
            'id',
            'name',
            'learning_objectives',
            'course_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_course_count(self, obj):
        """Get the total number of courses in this class."""
        return obj.course.count()


class QuizQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for QuizQuestion model.
    """

    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = [
            'id',
            'question_point',
            'question_text',
            'course',
            'course_name',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_option',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class QuizQuestionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating quiz questions.
    """
    
    class Meta:
        model = QuizQuestion
        fields = [
            'question_point',
            'question_text',
            'course',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_option',
        ]

    def validate_correct_option(self, value):
        """Validate that correct_option is one of the valid choices."""
        valid_options = ['A', 'B', 'C', 'D']
        if value not in valid_options:
            raise serializers.ValidationError(
                f"Correct option must be one of {valid_options}"
            )
        return value


class QuizQuestionListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for quiz question listing (without correct answer).
    """

    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = [
            'id',
            'question_point',
            'question_text',
            'course_name',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
        ]
        read_only_fields = ['id']


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for Quiz model.
    """

    questions = QuizQuestionSerializer(many=True, read_only=True)
    question_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=QuizQuestion.objects.all(),
        write_only=True,
        source='questions'
    )
    course_name = serializers.CharField(source='course.name', read_only=True)
    class_name_display = serializers.CharField(source='class_name.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    total_points = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id',
            'name',
            'class_name',
            'class_name_display',
            'course',
            'course_name',
            'questions',
            'question_ids',
            'passing_score',
            'total_points',
            'question_count',
            'created_by',
            'created_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_total_points(self, obj):
        """Calculate total points for the quiz."""
        return sum(q.question_point for q in obj.questions.all())

    def get_question_count(self, obj):
        """Get the total number of questions in the quiz."""
        return obj.questions.count()


class QuizCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating quizzes.
    """

    question_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=QuizQuestion.objects.all(),
        write_only=True,
        source='questions',
        required=False
    )

    class Meta:
        model = Quiz
        fields = [
            'name',
            'class_name',
            'course',
            'question_ids',
            'passing_score',
        ]

    def validate(self, attrs):
        """Validate that quiz data is correct."""
        # Validate that all questions belong to the same course as the quiz
        if 'questions' in attrs:
            course = attrs.get('course')
            for question in attrs['questions']:
                if question.course != course:
                    raise serializers.ValidationError(
                        f"Question '{question.question_text[:50]}...' belongs to course '{question.course.name}', "
                        f"but quiz is for course '{course.name}'"
                    )
        
        # Validate passing score
        passing_score = attrs.get('passing_score', 70)
        if passing_score < 0 or passing_score > 100:
            raise serializers.ValidationError(
                "Passing score must be between 0 and 100."
            )
        
        return attrs

    def create(self, validated_data):
        """Create quiz with the current user as creator."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        questions = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        
        if questions:
            quiz.questions.set(questions)
        
        return quiz


class QuizListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for quiz listing.
    """

    course_name = serializers.CharField(source='course.name', read_only=True)
    class_name_display = serializers.CharField(source='class_name.name', read_only=True)
    question_count = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id',
            'name',
            'class_name_display',
            'course_name',
            'passing_score',
            'question_count',
            'total_points',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_question_count(self, obj):
        """Get the total number of questions in the quiz."""
        return obj.questions.count()

    def get_total_points(self, obj):
        """Calculate total points for the quiz."""
        return sum(q.question_point for q in obj.questions.all())


class QuizUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating quizzes.
    """

    question_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=QuizQuestion.objects.all(),
        write_only=True,
        source='questions',
        required=False
    )

    class Meta:
        model = Quiz
        fields = [
            'name',
            'passing_score',
            'question_ids',
        ]

    def validate(self, attrs):
        """Validate quiz update data."""
        # Validate that all questions belong to the same course as the quiz
        if 'questions' in attrs:
            quiz_course = self.instance.course
            for question in attrs['questions']:
                if question.course != quiz_course:
                    raise serializers.ValidationError({ 
                        f"Question '{question.question_text[:50]}...' belongs to course '{question.course.name}', "
                        f"but quiz is for course '{quiz_course.name}'"}
                    )
        
        # Validate passing score
        passing_score = attrs.get('passing_score')
        if passing_score is not None and (passing_score < 0 or passing_score > 100):
            raise serializers.ValidationError(
                "Passing score must be between 0 and 100."
            )
        
        return attrs

    def update(self, instance, validated_data):
        """Update quiz."""
        questions = validated_data.pop('questions', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if questions is not None:
            instance.questions.set(questions)
        
        return instance


class QuizAnswerSerializer(serializers.Serializer):
    """Serializer for individual quiz answer."""
    question_id = serializers.IntegerField()
    selected_option = serializers.ChoiceField(choices=['A', 'B', 'C', 'D'])


class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for submitting quiz answers."""
    quiz_id = serializers.IntegerField()
    answers = QuizAnswerSerializer(many=True)

    def validate_quiz_id(self, value):
        """Validate that the quiz exists."""
        try:
            Quiz.objects.get(id=value)
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz does not exist.")
        return value

    def validate_answers(self, value):
        """Validate that answers are provided."""
        if not value:
            raise serializers.ValidationError("At least one answer must be provided.")
        return value

    def validate(self, attrs):
        """Validate that all question IDs belong to the quiz."""
        quiz_id = attrs.get('quiz_id')
        answers = attrs.get('answers', [])
        
        try:
            quiz = Quiz.objects.prefetch_related('questions').get(id=quiz_id)
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz does not exist.")
        
        quiz_question_ids = set(quiz.questions.values_list('id', flat=True))
        submitted_question_ids = set(answer['question_id'] for answer in answers)
        
        # Check for invalid question IDs
        invalid_ids = submitted_question_ids - quiz_question_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"The following question IDs do not belong to this quiz: {invalid_ids}"
            )
        
        return attrs

    def create(self, validated_data):
        """Calculate score and create StudentQuizAttempt."""
        quiz_id = validated_data['quiz_id']
        answers = validated_data['answers']
        request = self.context.get('request')
        student = request.user
        
        # Get quiz and all questions
        quiz = Quiz.objects.prefetch_related('questions').get(id=quiz_id)
        
        # Calculate score
        score = 0
        total_points = 0
        results = []
        
        for answer in answers:
            try:
                question = QuizQuestion.objects.get(id=answer['question_id'])
                total_points += question.question_point
                
                is_correct = question.correct_option == answer['selected_option']
                if is_correct:
                    score += question.question_point
                
                results.append({
                    'question_id': question.id,
                    'question_text': question.question_text,
                    'selected_option': answer['selected_option'],
                    'correct_option': question.correct_option,
                    'is_correct': is_correct,
                    'points_earned': question.question_point if is_correct else 0,
                    'points_possible': question.question_point
                })
            except QuizQuestion.DoesNotExist:
                continue
        
        # Create quiz attempt (save method will calculate grade and progress_percentage)
        quiz_attempt = StudentQuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            score=score,
            progress_percentage=0  # Will be calculated in save method
        )
        
        return {
            'quiz_attempt': quiz_attempt,
            'results': results,
            'total_points': total_points
        }


class StudentQuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for StudentQuizAttempt model."""
    
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    quiz_name = serializers.CharField(source='quiz.name', read_only=True)
    course_name = serializers.CharField(source='quiz.course.name', read_only=True)
    
    class Meta:
        model = StudentQuizAttempt
        fields = [
            'id',
            'student',
            'student_name',
            'student_email',
            'quiz',
            'quiz_name',
            'course_name',
            'score',
            'grade',
            'progress_percentage',
            'attempted_at'
        ]
        read_only_fields = ['id', 'grade', 'progress_percentage', 'attempted_at']


class QuizSubmissionResponseSerializer(serializers.Serializer):
    """Serializer for quiz submission response."""
    
    attempt = StudentQuizAttemptSerializer()
    results = serializers.ListField(
        child=serializers.DictField()
    )
    total_points = serializers.IntegerField()
    message = serializers.CharField()


class QuizPerformanceSerializer(serializers.Serializer):
    """Serializer for student quiz performance overview."""
    user_name=serializers.CharField(source='student.full_name', read_only=True)
    user_email=serializers.CharField(source='student.email', read_only=True)
    quiz_id = serializers.IntegerField()
    quiz_name = serializers.CharField()
    course_name = serializers.CharField()
    class_name = serializers.CharField()
    total_points = serializers.IntegerField()
    passing_score = serializers.IntegerField()
    
    # Attempt statistics
    total_attempts = serializers.IntegerField()
    best_score = serializers.IntegerField(allow_null=True)
    best_grade = serializers.CharField(allow_null=True)
    best_percentage = serializers.FloatField(allow_null=True)
    latest_score = serializers.IntegerField(allow_null=True)
    latest_grade = serializers.CharField(allow_null=True)
    latest_percentage = serializers.FloatField(allow_null=True)
    latest_attempt_date = serializers.DateTimeField(allow_null=True)
    
    # Status
    has_passed = serializers.BooleanField()
    is_attempted = serializers.BooleanField()
    
    # All attempts
    attempts = StudentQuizAttemptSerializer(many=True, required=False)
