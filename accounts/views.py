from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

class RegisterAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Send registration email
            try:
                # send_mail(
                #     subject="Registration Successful",
                #     message=f"Welcome to Public Notes API, {user.username}!\n\nYour account has been created successfully.\nYou can now login with your credentials.",
                #     from_email=None,
                #     recipient_list=[user.email],
                # )
                send_mail(
                    subject="Registration Successful",
                    message="Your account has been created successfully.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,  # 🔥 VERY IMPORTANT
                )
            except Exception as e:
                print(f"Email error: {e}")
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "User registered successfully",
                    "user": UserSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Send login email
            try:
                send_mail(
                    subject="Login Successful",
                    message=f"You have successfully logged in to your Public Notes API account.",
                    from_email=None,
                    recipient_list=[user.email],
                )
            except Exception as e:
                print(f"Email error: {e}")
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "You logged in successfully",
                    "user": UserSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Send logout email
            send_mail(
                subject="Logout Successful",
                message=f"You have successfully logged out from your Public Notes API account.",
                from_email=None,
                recipient_list=[request.user.email],
            )
        except Exception as e:
            print(f"Email error: {e}")
        
        return Response(
            {
                "message": "You logged out successfully",
                "detail": "Token has been invalidated. Please clear your local token."
            },
            status=status.HTTP_200_OK
        )


