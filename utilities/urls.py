from django.urls import path
from .views import PrivacyPolicyView, TermsAndConditionsView

app_name = "utilities"

urlpatterns = [
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', TermsAndConditionsView.as_view(), name='terms_of_service'),
]
