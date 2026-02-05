from django.contrib import admin

# Register your models here.
from .models import PrivacyPolicy, TermsAndConditions

@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ('id', 'effective_date')
    search_fields = ('effective_date',)
    ordering = ('-effective_date',)


@admin.register(TermsAndConditions)
class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'effective_date')
    search_fields = ('effective_date',)
    ordering = ('-effective_date',)