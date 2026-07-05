from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User, EmployerProfile, CandidateProfile


class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = [
            "id", "company_name", "industry", "company_website",
            "company_size", "location", "about", "logo", "is_verified", "created_at",
        ]
        read_only_fields = ["is_verified", "created_at"]


class CandidateProfileSerializer(serializers.ModelSerializer):
    skills_list = serializers.ReadOnlyField()

    class Meta:
        model = CandidateProfile
        fields = [
            "id", "full_name", "headline", "phone", "location", "skills",
            "skills_list", "experience_years", "about", "profile_picture", "created_at",
        ]
        read_only_fields = ["created_at"]


class UserSerializer(serializers.ModelSerializer):
    employer_profile = EmployerProfileSerializer(read_only=True)
    candidate_profile = CandidateProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "employer_profile", "candidate_profile", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "company_name", "full_name"]

    def validate(self, attrs):
        role = attrs.get("role")
        if role == User.Role.EMPLOYER and not attrs.get("company_name"):
            raise serializers.ValidationError({"company_name": "Company name is required for employer accounts."})
        if role == User.Role.CANDIDATE and not attrs.get("full_name"):
            raise serializers.ValidationError({"full_name": "Full name is required for candidate accounts."})
        return attrs

    def create(self, validated_data):
        company_name = validated_data.pop("company_name", "")
        full_name = validated_data.pop("full_name", "")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user.role == User.Role.EMPLOYER:
            EmployerProfile.objects.create(user=user, company_name=company_name)
        else:
            CandidateProfile.objects.create(user=user, full_name=full_name)

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        attrs["user"] = user
        return attrs
