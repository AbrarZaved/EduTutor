from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PrivacyPolicy, TermsAndConditions
from .serializers import PrivacyPolicySerializer, TermsAndConditionsSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view



@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Privacy Policy",
        description="Get the latest Privacy Policy.",
        responses={
            200: PrivacyPolicySerializer,
            404: OpenApiResponse(description="Privacy Policy not found.")
        },
        tags=['Utilities']
    ),
    post=extend_schema(
        summary="Create Privacy Policy",
        description="Create a new Privacy Policy.",
        request=PrivacyPolicySerializer,
        responses={
            201: PrivacyPolicySerializer,
            400: OpenApiResponse(description="Bad Request")
        },
        tags=['Utilities']
    ),
    patch=extend_schema(
        summary="Update Privacy Policy",
        description="Update the latest Privacy Policy.",
        request=PrivacyPolicySerializer,
        responses={
            200: PrivacyPolicySerializer,
            400: OpenApiResponse(description="Bad Request"),
            404: OpenApiResponse(description="Privacy Policy not found.")
        },
        tags=['Utilities']
    ),
)
class PrivacyPolicyView(APIView):
    """
    View to retrieve the latest Privacy Policy.
    """

    def get(self, request, *args, **kwargs):
        try:
            policy = PrivacyPolicy.objects.latest('effective_date')
            serializer = PrivacyPolicySerializer(policy)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PrivacyPolicy.DoesNotExist:
            return Response(
                {"detail": "Privacy Policy not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request, *args, **kwargs):
        serializer = PrivacyPolicySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        try:
            policy = PrivacyPolicy.objects.latest('effective_date')
            serializer = PrivacyPolicySerializer(policy, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PrivacyPolicy.DoesNotExist:
            return Response(
                {"detail": "Privacy Policy not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
 
@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Terms and Conditions",
        description="Get the latest Terms and Conditions.",
        responses={
            200: TermsAndConditionsSerializer,
            404: OpenApiResponse(description="Terms and Conditions not found.")
        },
        tags=['Utilities']
    ),
    post=extend_schema(
        summary="Create Terms and Conditions",
        description="Create new Terms and Conditions.",
        request=TermsAndConditionsSerializer,
        responses={
            201: TermsAndConditionsSerializer,
            400: OpenApiResponse(description="Bad Request")
        },
        tags=['Utilities']
    ),
    patch=extend_schema(
        summary="Update Terms and Conditions",
        description="Update the latest Terms and Conditions.",
        request=TermsAndConditionsSerializer,
        responses={
            200: TermsAndConditionsSerializer,
            400: OpenApiResponse(description="Bad Request"),
            404: OpenApiResponse(description="Terms and Conditions not found.")
        },
        tags=['Utilities']
    ),
)   
class TermsAndConditionsView(APIView):

    """
    View to retrieve the latest Terms and Conditions.
    """


    def get(self, request, *args, **kwargs):
        try:
            terms = TermsAndConditions.objects.latest('effective_date')
            serializer = TermsAndConditionsSerializer(terms)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TermsAndConditions.DoesNotExist:
            return Response(
                {"detail": "Terms and Conditions not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    
    def post(self, request, *args, **kwargs):
        serializer = TermsAndConditionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        try:
            terms = TermsAndConditions.objects.latest('effective_date')
            serializer = TermsAndConditionsSerializer(terms, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TermsAndConditions.DoesNotExist:
            return Response(
                {"detail": "Terms and Conditions not found."},
                status=status.HTTP_404_NOT_FOUND,
            )