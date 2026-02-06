from django.db import models

# Create your models here.

class StudentProfile(models.Model):
    student_id = models.CharField(("Student ID"), max_length=50, primary_key=True)
    user = models.OneToOneField(
        "core_auth.User",
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/students/",
        blank=True,
        null=True,
    )
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"StudentProfile: {self.user.email}"
    
    def get_full_name(self):
        """Return the full name of the student."""
        return self.user.full_name
    
    def save(self, *args, **kwargs):
        """Override save method to auto-generate student_id if not provided."""
        if not self.student_id:
            self.student_id = f"STU-{self.user.id:06d}"
        super().save(*args, **kwargs)


class TeacherProfile(models.Model):
    teacher_id=models.CharField(("Teacher ID"), max_length=50, primary_key=True)
    user=models.OneToOneField(
        "core_auth.User",
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )
    profile_picture=models.ImageField(
        upload_to="profile_pictures/teachers/",
        blank=True,
        null=True,
    )
    department=models.CharField(max_length=100, blank=True, null=True)
    experience=models.IntegerField(blank=True, null=True)  # in years


    def __str__(self):
        return f"TeacherProfile: {self.user.email}"
    
    def get_full_name(self):
        """Return the full name of the teacher."""
        return self.user.full_name
    
    def save(self, *args, **kwargs):
        """Override save method to auto-generate teacher_id if not provided."""
        if not self.teacher_id:
            self.teacher_id = f"TEA-{self.user.id:06d}"
        super().save(*args, **kwargs)


class ParentProfile(models.Model):
    parent_id=models.CharField(max_length=50, blank=False, primary_key=True)
    user=models.OneToOneField(
        "core_auth.User",
        on_delete=models.CASCADE,
        related_name="parent_profile",
    )
    profile_picture=models.ImageField(
        upload_to="profile_pictures/parents/",
        blank=True,
        null=True,
    )
    relation=models.CharField(max_length=100, blank=True, null=True)  # e.g., Father, Mother


    def __str__(self):
        return f"ParentProfile: {self.user.email}"
    
    def get_full_name(self):
        """Return the full name of the parent."""
        return self.user.full_name
    
    def save(self, *args, **kwargs):
        """Override save method to auto-generate parent_id if not provided."""
        if not self.parent_id:
            self.parent_id = f"PAR-{self.user.id:06d}"
        super().save(*args, **kwargs)



class ParentPreference(models.Model):
    parent=models.OneToOneField(
        ParentProfile,
        on_delete=models.CASCADE,
        related_name="preferences",
    )
    childs=models.ManyToManyField(StudentProfile, related_name="parents")
    notifications_enabled=models.BooleanField(default=True)


    def __str__(self):
        return f"ParentPreference: {self.parent.user.email}"
    
    

class AdminProfile(models.Model):
    admin_id=models.CharField(max_length=50, blank=False, primary_key=True)
    user=models.OneToOneField(
        "core_auth.User",
        on_delete=models.CASCADE,
        related_name="admin_profile",
    )
    profile_picture=models.ImageField(
        upload_to="profile_pictures/admins/",
        blank=True,
        null=True,
    )
    address=models.CharField(max_length=255, blank=True, null=True)
    location=models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"AdminProfile: {self.user.email}"
    
    def get_full_name(self):
        """Return the full name of the admin."""
        return self.user.full_name
    
    def save(self, *args, **kwargs):
        """Override save method to auto-generate admin_id if not provided."""
        if not self.admin_id:
            self.admin_id = f"ADM-{self.user.id:06d}"
        super().save(*args, **kwargs)