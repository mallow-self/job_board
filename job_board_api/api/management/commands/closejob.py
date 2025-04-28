from django.core.management.base import BaseCommand, CommandError
from api.models import JobListing


class Command(BaseCommand):
    help = "Changes the title of the snippet for the given id"

    def add_arguments(self, parser):
        parser.add_argument("job_id", type=int)

    def handle(self, *args, **options):
        id = options["job_id"]
        try:
            job = JobListing.objects.get(pk=id)
            job.is_active = False
            job.save()
            self.stdout.write(f"Job with {id} closed successfully")
        except JobListing.DoesNotExist:
            raise CommandError(f"job id:{id} doesn't exist")
