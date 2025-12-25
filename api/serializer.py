from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from api.models import *
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
import logging

logger = logging.getLogger(__name__)

# This serializer is used for user registration, allowing users to create an account.
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    # Don't validate the password here to ensure that if a password mismatch, it shows first.
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password', 'first_name', 'last_name')


    def validate_email(self, value):
        if User.objects.filter(username=value.lower()).exists():
            raise serializers.ValidationError("Oops, something is wrong with this email. Contact admin.")

        if "@flyflair.com" not in value.lower():
            raise serializers.ValidationError("Oops, something is wrong with this email. Contact admin.")

        return value

    # Validate the password.
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match."})


        # Raise the error in a list.
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise DRFValidationError({"password": " ".join(e.messages)})

        return attrs


    # Use the email as the username.
    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']

        user = User.objects.create_user(
            username=email.lower(),
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        user.groups.add(Group.objects.get(name='Basic'))
        user.save()

        return user


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]


# Serializer to login a user.
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Log the email to monitor login attempts.
        if email:
            logger.info(f"Login attempt for {email} at {datetime.now()}")

        try:
            user_obj = User.objects.get(email=email.lower())
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            # Dummy auth to prevent timing attacks
            authenticate(username="dummy_email", password="dummy_password")
            user = None

        if not user:
            raise serializers.ValidationError("Invalid login credentials.")

        attrs['user'] = user
        return attrs


class HandoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Handover
        fields = '__all__'

    def create(self, validated_data):
        date = validated_data['date']
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        shift = validated_data['shift']
        region = validated_data['region']

        handover_id = f"{date.strftime('%Y-%m-%d')}-{shift}-{region}"
        validated_data['handover_id'] = handover_id

        # This returns a Handover instance
        handover, _ = Handover.objects.update_or_create(
            handover_id=handover_id,
            defaults=validated_data
        )

        return handover



class CDDUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CDD_Users
        fields = ['full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"




class PDFEmailSerializer(serializers.Serializer):
    to = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False
    )
    cc = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        allow_empty=True,
        default=[]
    )

    subject = serializers.CharField()
    message = serializers.CharField()
    pdf = serializers.FileField()

    def validate(self, attrs):
        pdf = attrs.get('pdf')
        if pdf is None or pdf.content_type != 'application/pdf':
            raise serializers.ValidationError("Only PDF Files are supported.")

        return attrs



class DispatchHandoverListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Handover
        fields = ['handover_id', 'date', 'dispatcher_name', 'shift', 'region', 'modified_at']
