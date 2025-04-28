# jobs/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import JobApplication


@receiver(post_save, sender=JobApplication)
def send_application_notifications(sender, instance, created, **kwargs):
    if created:
        job = instance.job
        applicant = instance.applicant
        employer = (
            job.employer
        )

        # Email to Employer
        send_mail(
            subject=f"New Application for {job.title}",
            message=f"{applicant.full_name} has applied for your job posting: {job.title}.",
            from_email="no-reply@example.com",
            recipient_list=[employer.email],
            fail_silently=False,
        )

        # Email to Applicant
        send_mail(
            subject=f"Application Received: {job.title}",
            message=f"Your application for {job.title} has been submitted successfully.",
            from_email="no-reply@example.com",
            recipient_list=[applicant.email],
            fail_silently=False,
        )
