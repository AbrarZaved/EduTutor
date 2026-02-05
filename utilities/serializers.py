from rest_framework import serializers
from .models import PrivacyPolicy, TermsAndConditions


class PrivacyPolicySerializer(serializers.ModelSerializer):
    """
    Serializer for the PrivacyPolicy model.
    """

    class Meta:
        model = PrivacyPolicy
        fields = ['id', 'content', 'effective_date']
        read_only_fields = ['id', 'effective_date']


class TermsAndConditionsSerializer(serializers.ModelSerializer):
    """
    Serializer for the TermsAndConditions model.
    """

    class Meta:
        model = TermsAndConditions
        fields = ['id', 'content', 'effective_date']
        read_only_fields = ['id', 'effective_date']