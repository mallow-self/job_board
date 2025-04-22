from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    """
    Custom manager for the User model.

    Provides helper methods for creating regular users and superusers
    with email as the unique identifier instead of a username.

    Methods:
        - create_user: Creates and returns a new user with the given email, full name, password, and user type.
        - create_superuser: Creates and returns a new superuser with staff and superuser permissions.
    """
    def create_user(self, email, full_name, password=None, user_type=None, **extra_fields):
        """
        Creates and returns a standard user.

        Args:
            email (str): The user's email address.
            full_name (str): The full name of the user.
            password (str, optional): The user's password.
            user_type (str, optional): The type of user (e.g., 'job_seeker' or 'employer').
            **extra_fields: Additional fields for the user model.

        Raises:
            ValueError: If email is not provided.

        Returns:
            User: The created user instance.
        """
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password):
        """
        Creates and returns a superuser with admin permissions.

        Args:
            email (str): The superuser's email address.
            full_name (str): The full name of the superuser.
            password (str): The superuser's password.

        Returns:
            User: The created superuser instance.
        """
        user = self.create_user(email, full_name, password, user_type='employer')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that supports using email as the unique identifier
    instead of a username. Includes support for two user types: job seekers
    and employers.

    Fields:
        - email (EmailField): Unique email address used as the username field.
        - full_name (CharField): Full name of the user.
        - user_type (CharField): Indicates whether the user is a 'job_seeker' or 'employer'.
        - phone_number (CharField): Contact number of the user.
        - skills (TextField): List or description of user skills (relevant for job seekers).
        - company (CharField): Company name (relevant for employers).
        - is_active (BooleanField): Designates whether this user should be treated as active.
        - is_staff (BooleanField): Designates whether the user can access the admin site.

    Manager:
        - objects: Uses a custom UserManager to handle user and superuser creation.

    Authentication:
        - USERNAME_FIELD: Uses 'email' as the unique identifier.
        - REQUIRED_FIELDS: Requires 'full_name' when creating a superuser via CLI.

    Methods:
        - __str__(): Returns the user's email address.
    """
    USER_TYPES = [
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(max_length=20)
    skills = models.TextField(blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email


class JobListing(models.Model):
    """
    Model representing a job listing posted by an employer.

    Fields:
        - title (CharField): Title of the job position.
        - description (TextField): Detailed description of the job role.
        - requirements (TextField): Skills or qualifications required for the role.
        - location (CharField): Physical or remote location of the job.
        - salary (CharField): Salary or compensation details.
        - company_name (CharField): Name of the employer's company (auto-filled, not editable).
        - employer (ForeignKey): Reference to the user who posted the job (must be an employer).
        - is_active (BooleanField): Indicates whether the listing is currently active.
        - created_at (DateTimeField): Timestamp of job listing creation.
        - updated_at (DateTimeField): Timestamp of the most recent update.

    Behavior:
        - The `company_name` field is automatically populated from the associated employer's profile
          on save to ensure consistency and prevent manual edits.

    Methods:
        - save(): Overrides the default save method to populate the `company_name` field before saving.
        - __str__(): Returns a human-readable representation of the job listing.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=255)
    salary = models.CharField(max_length=100)
    company_name = models.CharField(max_length=255, editable=False)
    employer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="job_listings"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.company_name = self.employer.company
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} at {self.company_name}"


class JobApplication(models.Model):
    """
    Model representing a job application submitted by a user for a specific job listing.

    Fields:
        - job (ForeignKey): Reference to the job listing being applied for.
        - applicant (ForeignKey): Reference to the user submitting the application.
        - resume (FileField): Uploaded resume document.
        - cover_letter (TextField): Optional cover letter text.
        - status (CharField): Status of the application; defaults to 'PENDING'.
        - created_at (DateTimeField): Timestamp when the application was created.
        - updated_at (DateTimeField): Timestamp when the application was last updated.

    Choices:
        - STATUS_CHOICES:
            - PENDING: Application has been submitted but not yet reviewed.
            - REVIEWED: Application has been seen by the employer.
            - SHORTLISTED: Applicant has been shortlisted.
            - REJECTED: Application was not successful.
            - HIRED: Applicant was hired for the position.

    Meta:
        - unique_together: Ensures a user cannot apply to the same job multiple times.

    Methods:
        - __str__(): Returns a readable string representation of the application.
    """
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("REVIEWED", "Reviewed"),
        ("SHORTLISTED", "Shortlisted"),
        ("REJECTED", "Rejected"),
        ("HIRED", "Hired"),
    )
    job = models.ForeignKey(
        JobListing, on_delete=models.CASCADE, related_name="applications"
    )
    applicant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )
    resume = models.FileField(upload_to="resumes/")
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["job", "applicant"]  # Prevent duplicate applications

    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"


class SavedJob(models.Model):
    """
    Model representing a job that has been saved/bookmarked by a user.

    Fields:
        - job (ForeignKey): Reference to the job listing that was saved.
        - user (ForeignKey): The user who saved the job.
        - saved_at (DateTimeField): Timestamp of when the job was saved (defaults to current time).

    Meta:
        - unique_together: Ensures that the same user cannot save the same job more than once.

    Methods:
        - __str__(): Returns a readable representation showing who saved which job.
    """
    job = models.ForeignKey(
        JobListing, on_delete=models.CASCADE, related_name="saved_by"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_jobs")
    saved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ["job", "user"]  # Prevent duplicate saves

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
