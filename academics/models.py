from django.db import models

class Skills(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Create your models here.
class Lesson(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    skills=models.ManyToManyField(Skills, related_name='lessons')
    duration=models.IntegerField(help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Units(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    lessons = models.ManyToManyField(Lesson, related_name='units')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    units = models.ManyToManyField(Units, related_name='courses', )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    


class UploadCourseDocuments(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='course_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.course.name} uploaded at {self.uploaded_at}"
    


class Class(models.Model):
    name = models.CharField(max_length=100)
    learning_objectives = models.TextField(blank=True, null=True)
    course = models.ManyToManyField(Course, related_name='classes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Classes"


class QuizQuestion(models.Model):
    options=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    question_point=models.IntegerField(default=1)
    question_text = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quiz_questions')
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=options)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question for {self.course.name}"
    

class Quiz(models.Model):
    name = models.CharField(max_length=100)
    class_name=models.ForeignKey(Class, on_delete=models.CASCADE, related_name='quizzes')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    questions = models.ManyToManyField(QuizQuestion, related_name='quizzes')
    passing_score = models.IntegerField(help_text="Minimum score required to pass the quiz", default=70)
    created_by=models.ForeignKey('core_auth.User', on_delete=models.SET_NULL, null=True, related_name='created_quizzes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz: {self.name} for {self.course.name}"
    

class StudentQuizAttempt(models.Model):

    student = models.ForeignKey('core_auth.User', on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.IntegerField()
    grade = models.CharField(max_length=10, blank=True, null=True)
    progress_percentage = models.FloatField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.email} - {self.quiz.name} Attempted at {self.attempted_at}"
    

    def save(self, *args, **kwargs):
        """Override save method to calculate pass/fail and progress percentage."""
        total_points = sum(q.question_point for q in self.quiz.questions.all())
        self.progress_percentage = (self.score / total_points) * 100 if total_points > 0 else 0
        self.grade = self.calculate_grade()

        super().save(*args, **kwargs)

    def calculate_grade(self):
        percentage = self.progress_percentage
        if percentage >= 97:
            return 'A+'
        elif percentage >= 93:
            return 'A'
        elif percentage >= 90:
            return 'A-'
        elif percentage >= 87:
            return 'B+'
        elif percentage >= 83:
            return 'B'
        elif percentage >= 80:
            return 'B-'
        elif percentage >= 77:
            return 'C+'
        elif percentage >= 73:
            return 'C'
        elif percentage >= 70:
            return 'C-'
        elif percentage >= 67:
            return 'D+'
        elif percentage >= 63:
            return 'D'
        elif percentage >= 60:
            return 'D-'
        else:
            return 'F'