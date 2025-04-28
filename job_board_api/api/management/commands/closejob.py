from django.core.management.base import BaseCommand, CommandError
from api.models import JobListing


class Command(BaseCommand):
    """
    Custom Django management command to deactivate (close) a specific job posting.

    This command sets the 'is_active' field of a JobListing instance to False,
    preventing any further applications for that job.

    Usage:
        python manage.py close_job <job_id>
    """

    help = "Deactivate a job posting by setting its 'is_active' field to False."

    def add_arguments(self, parser):
        parser.add_argument("job_id", type=int)

    def handle(self, *args, **options):
        id: int = options["job_id"]
        try:
            job = JobListing.objects.get(pk=id)
            job.is_active = False
            job.save()
            self.stdout.write(f"Job with {id} closed successfully")
        except JobListing.DoesNotExist:
            raise CommandError(f"job id:{id} doesn't exist")
