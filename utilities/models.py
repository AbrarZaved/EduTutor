from django.db import models

# Create your models here.

class PrivacyPolicy(models.Model):
    content = models.TextField()
    effective_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"PrivacyPolicy effective from {self.effective_date}"
    

class TermsAndConditions(models.Model):
    content = models.TextField()
    effective_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"TermsAndConditions effective from {self.effective_date}"