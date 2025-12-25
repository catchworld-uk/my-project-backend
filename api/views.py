from django.core.exceptions import PermissionDenied
from django.core.mail.message import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.template.context_processors import request
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import *
from api.custom_permissions import HasMinimumTierPermission
from api.serializer import (RegisterSerializer, LoginSerializer, CurrentUserSerializer, CDDUserSerializer,
                            PDFEmailSerializer, HandoverSerializer, DispatchHandoverListSerializer)


class RegisterView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'User registered successfully'},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = RefreshToken.for_user(user)

            # Return token in the response
            response = Response({
                "message": "Login Successful",
            })

            # Set the token in the response headers
            # Set as HttpOnly to prevent XSS attacks
            response.set_cookie(
                key='access_token',
                value=str(tokens.access_token),
                httponly=True,  # HttpOnly to prevent JavaScript access
                secure=True,  # Secure to ensure it's only sent over HTTPS
                samesite='Lax',  # Lax to allow sending cookies with top-level navigations and same-site requests
                max_age=300  # 5 minutes
            )

            response.set_cookie(
                key='refresh_token',
                value=str(tokens),
                httponly=True,  # HttpOnly to prevent JavaScript access
                secure=True,  # Secure to ensure it's only sent over HTTPS
                samesite='Lax',  # Lax to allow sending cookies with top-level navigations and same-site requests
                max_age=86400  # 1 day
            )

            return response
        else:
            return Response({
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)



class RefreshTokenView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                # Decode the fresh token to get a new access token.
                tokens = RefreshToken(refresh_token)

                # Set the new access token in the response headers.
                # Set as HttpOnly to prevent XSS attacks
                response = Response({
                    'message': 'Refresh Successful',
                })

                response.set_cookie(
                    key='access_token',
                    value=str(tokens.access_token),
                    httponly=True,  # HttpOnly to prevent JavaScript access
                    secure=True,  # Secure to ensure it's only sent over HTTPS
                    samesite='Lax',  # Lax to allow sending cookies with top-level navigations and same-site requests
                    max_age=300 # Set cookie expiration time (5 minutes)
                )

                response.set_cookie(
                    key='refresh_token',
                    value=str(tokens),
                    httponly=True,  # HttpOnly to prevent JavaScript access
                    secure=True,  # Secure to ensure it's only sent over HTTPS
                    samesite='Lax',  # Lax to allow sending cookies with top-level navigations and same-site requests
                    max_age=86400  # Set cookie expiration time (1 day)
                )

                return response

            except Exception as e:
                # Return an error if the refresh token is invalid
                return Response({
                    'message': 'Invalid refresh token',
                    'error': str(e)
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'message': 'Refresh token not provided'
            }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

class CurrentUser(APIView):

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)



class HomeView(APIView):
    def get(self, request):
        # If the user is authenticated, return a success message
        return Response({
            'message': 'Welcome to the dashboard!',
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        }, status=status.HTTP_200_OK)


class GetCDDUsers(APIView):
    def get(self, request):
        cdd_users = CDD_Users.objects.all()
        serializer = CDDUserSerializer(cdd_users, many=True)
        return Response(serializer.data)


class SendPDFEmail(APIView):
    def post(self, request):
        serializer = PDFEmailSerializer(data=request.data)
        if serializer.is_valid():
            to = serializer.validated_data['to']
            cc = serializer.validated_data['cc']
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']
            pdf = serializer.validated_data['pdf']

            email = EmailMessage(
                subject=subject,
                body=message,
                to=to,
                cc=cc if cc else []
            )

            email.attach(pdf.name, pdf.read(), 'application/pdf')
            email.send()

            return Response({"message": "Email sent successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SaveHandover(APIView):
    def post(self, request):
        serializer = HandoverSerializer(data=request.data)
        if serializer.is_valid():

            handover = serializer.save()
            print(request.data)

            return Response({"handover_id": handover.handover_id}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HandoverList(APIView):
    def get(self, request):
        handovers = Handover.objects.all()
        serializer = DispatchHandoverListSerializer(handovers, many=True)
        return Response(serializer.data)




# class HomeView(APIView):
#     permission_classes = [HasMinimumTierPermission]
#     required_tier_level = 2
#
#     def get(self, request):
#         return Response({
#             'message': 'Welcome to the dashboard!',
#             'email': request.user.email,
#             'first_name': request.user.first_name,
#             'last_name': request.user.last_name
#         }, status=status.HTTP_200_OK)
#
#     def permission_denied(self, request, message=None, code=None):
#         raise PermissionDenied(detail="You do not have permission to view this page.")
#
