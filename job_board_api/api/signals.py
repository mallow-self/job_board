from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import JobApplication
from typing import Type
from django.db.models import Model


@receiver(post_save, sender=JobApplication)
def send_application_notifications(sender: Type[Model], instance: JobApplication, created: bool, **kwargs) -> None:
    """
    Signal handler that sends email notifications when a new JobApplication is created.

    Sends:
    - An email to the employer notifying them of the new application.
    - A confirmation email to the applicant confirming the successful submission.

    Args:
        sender (Type[Model]): The model class (JobApplication).
        instance (JobApplication): The actual instance being saved.
        created (bool): Whether this is a new instance (True) or an update (False).
        **kwargs: Additional keyword arguments passed by the signal.
    """
    if created:
        job = instance.job
        applicant = instance.applicant
        employer = job.employer

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