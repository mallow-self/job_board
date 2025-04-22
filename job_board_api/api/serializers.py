from rest_framework import serializers
from .models import User, JobListing, JobApplication, SavedJob
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "user_type",
            "phone_number",
            "skills",
            "company",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "full_name",
            "email",
            "password",
            "user_type",
            "phone_number",
            "skills",
            "company",
        ]

    def validate(self, attrs):
        user_type = attrs.get("user_type")
        if user_type == "job_seeker" and not attrs.get("skills"):
            raise serializers.ValidationError("Job Seekers must have skills.")
        if user_type == "employer" and not attrs.get("company"):
            raise serializers.ValidationError("Employers must provide a company.")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class JobListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobListing
        read_only_fields = ["employer", "company_name"]
        fields = "__all__"


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.ReadOnlyField(source='job.title')

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_title', 'resume', 'cover_letter', 'status', 'created_at']
        read_only_fields = ['status', 'created_at', 'job_title']


class SavedJobSerializer(serializers.ModelSerializer):
    job_title = serializers.ReadOnlyField(source="job.title")
    job_id = serializers.ReadOnlyField(source="job.id")

    class Meta:
        model = SavedJob
        fields = ["id", "job_id", "job_title", "saved_at"]
