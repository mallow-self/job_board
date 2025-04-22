from rest_framework import serializers
from .models import User, JobListing, JobApplication, SavedJob
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for representing user profile data.

    Includes fields:
    - id
    - full_name
    - email
    - user_type (job_seeker or employer)
    - phone_number
    - skills (optional, shown if user_type is job_seeker)
    - company (optional, shown if user_type is employer)
    """
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


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data. Handles validation, creation, and updating
    of user instances with custom logic for different user types.

    Fields:
        - full_name (str): Full name of the user.
        - email (str): Email address of the user.
        - password (str): Password for the user (write-only).
        - user_type (str): Type of user, e.g., 'job_seeker' or 'employer'.
        - phone_number (str): User's phone number.
        - skills (str or list): Skills (required if user_type is 'job_seeker').
        - company (str): Company name (required if user_type is 'employer').

    Validation Rules:
        - Job seekers must provide at least one skill.
        - Employers must provide a company name.

    Methods:
        - validate(): Ensures that 'skills' and 'company' are provided
                      based on the user's type.
        - create(): Creates a user using the custom create_user method.
        - update(): Updates user fields and handles password hashing
                    if the password is updated.
    """
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

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data.pop("password"))
        return super().update(instance, validated_data)


class JobListingSerializer(serializers.ModelSerializer):
    """
    Serializer for the JobListing model.

    Handles serialization and deserialization of job listing data,
    including automatic assignment of read-only fields.

    Meta Configuration:
        - model: JobListing
        - fields: Includes all model fields.
        - read_only_fields:
            - employer: The user who posted the job (typically set automatically).
            - company_name: The company associated with the employer.

    This serializer can be used for creating, retrieving, updating, and deleting job listings,
    while ensuring that certain fields are not editable by clients.
    """
    class Meta:
        model = JobListing
        read_only_fields = ["employer", "company_name"]
        fields = "__all__"


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the JobApplication model.

    Includes fields for submitting and viewing job applications,
    with support for read-only fields to prevent client-side manipulation
    of certain values.

    Fields:
        - id (int): Unique identifier of the job application.
        - job (ForeignKey): Reference to the associated job listing.
        - job_title (str): Title of the associated job (read-only, sourced from job.title).
        - resume (File): Uploaded resume for the application.
        - cover_letter (Text): Optional cover letter content.
        - status (str): Status of the application (read-only).
        - created_at (datetime): Timestamp when the application was created (read-only).

    Meta Configuration:
        - model: JobApplication
        - fields: All relevant fields related to job applications.
        - read_only_fields:
            - status: Managed by the system or employer.
            - created_at: Set automatically when the application is submitted.
            - job_title: Derived from the related Job model.
    """
    job_title = serializers.ReadOnlyField(source='job.title')

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_title', 'resume', 'cover_letter', 'status', 'created_at']
        read_only_fields = ['status', 'created_at', 'job_title']


class SavedJobSerializer(serializers.ModelSerializer):
    """
    Serializer for the SavedJob model.

    Used to represent saved jobs for a user, including basic job details
    like title and ID, as well as the timestamp when the job was saved.

    Fields:
        - id (int): Unique identifier of the saved job entry.
        - job_id (int): ID of the associated job (read-only, from job.id).
        - job_title (str): Title of the associated job (read-only, from job.title).
        - saved_at (datetime): Timestamp when the job was saved.

    Meta Configuration:
        - model: SavedJob
        - fields: Fields included in the serialized representation.
    """
    job_title = serializers.ReadOnlyField(source="job.title")
    job_id = serializers.ReadOnlyField(source="job.id")

    class Meta:
        model = SavedJob
        fields = ["id", "job_id", "job_title", "saved_at"]
