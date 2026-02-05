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
    
