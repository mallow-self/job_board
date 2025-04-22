from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, user_type=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password):
        user = self.create_user(email, full_name, password, user_type='employer')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
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
    job = models.ForeignKey(
        JobListing, on_delete=models.CASCADE, related_name="saved_by"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_jobs")
    saved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ["job", "user"]  # Prevent duplicate saves

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
