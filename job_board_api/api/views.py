from rest_framework import generics, permissions, viewsets, status, filters
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import User, JobListing, JobApplication, SavedJob
from .serializers import UserProfileSerializer, UserSerializer, JobListingSerializer, JobApplicationSerializer, SavedJobSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from .permissions import IsEmployerAndOwnerOrReadOnly, IsJobSeeker
from rest_framework.decorators import APIView
from django_filters.rest_framework import DjangoFilterBackend

class UserRegisterView(generics.CreateAPIView):
    """
    Handles user registration.

    This view accepts user data via POST, creates a new user, generates an authentication token,
    and returns the token along with serialized user information.

    Endpoint: POST /api/user-profile/
    Response: {
        "token": "<auth_token>",
        "user": { ...user_fields... }
    }
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data["email"])
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class UserUpdateView(generics.UpdateAPIView):
    """
    Handles updating the authenticated user's profile.

    Only authenticated users can access this endpoint. Users can only update their own profile,
    and not any other user's data.

    Endpoint: PUT /api/user-profile/<user_id>/
    Authentication: Token required
    Response: 200 OK with updated user data
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class CustomAuthToken(ObtainAuthToken):
    """
    Handles user login and returns an authentication token along with user details.

    Accepts email and password via POST request, verifies credentials, and returns a token.
    If authentication is successful, also returns the serialized user data.

    Endpoint: POST /api/login/
    Payload: {
        "username": "user@example.com",
        "password": "yourpassword"
    }
    Response: {
        "token": "<auth_token>",
        "user": { ...user_fields... }
    }
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])
        return Response({"token": token.key, "user": UserSerializer(token.user).data})


class JobListingViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for job listings.

    - Employers can create, update, and delete their own job listings.
    - Job seekers and employers can view job listings.
    - Supports filtering by location and company_name.
    - Supports searching by title, description, requirements, location, and company_name.

    Permissions:
    - Only authenticated users can access.
    - Only employers can create listings.
    - Only the employer who created the listing can modify or delete it.

    Filters:
    - Filter by 'location' and 'company_name'.
    - Search by 'title', 'description', 'requirements', 'location', and 'company_name'.
    """
    queryset = JobListing.objects.all().order_by("-created_at")
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated, IsEmployerAndOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["location", "company_name"]
    search_fields = ["title", "description", "requirements", "location", "company_name"]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)


class ApplyJobView(generics.CreateAPIView):
    """
    Allows a job seeker to apply for a specific job.

    - Only authenticated users with a 'job_seeker' role can apply.
    - Prevents duplicate applications for the same job by the same user.
    - Returns 404 if the job is inactive or does not exist.
    - Returns 400 if the user has already applied or if validation fails.

    Endpoint: POST /api/jobs/apply/<job_id>/
    Payload: {
        "resume": <uploaded_file>,
        "cover_letter": "Optional cover letter text"
    }
    Response: 201 CREATED with application data or relevant error message.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobSeeker]

    def post(self, request, job_id):
        try:
            job = JobListing.objects.get(pk=job_id, is_active=True)
        except JobListing.DoesNotExist:
            return Response({"detail": "Job not found or inactive."}, status=404)

        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            return Response(
                {"detail": "You have already applied to this job."}, status=400
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(applicant=request.user, job=job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)


class AppliedJobsListView(generics.ListAPIView):
    """
    Lists all jobs the authenticated job seeker has applied to.

    - Only authenticated users can access this endpoint.
    - Returns job applications made by the currently logged-in user.
    - Applications are ordered by most recent first.

    Endpoint: GET /api/jobs/applied/
    Response: 200 OK with a list of job applications.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(applicant=self.request.user).order_by(
            "-created_at"
        )


class SaveJobView(APIView):
    """
    Allows a job seeker to save a job listing for later reference.

    - Only authenticated users with a 'job_seeker' role can save jobs.
    - Prevents saving the same job multiple times.
    - Returns 404 if the job does not exist.
    - Returns 400 if the job has already been saved by the user.

    Endpoint: POST /api/jobs/save/<job_id>/
    Response: 201 CREATED with saved job data or relevant error message.
    """
    permission_classes = [permissions.IsAuthenticated, IsJobSeeker]

    def post(self, request, job_id):
        try:
            job = JobListing.objects.get(id=job_id)
        except JobListing.DoesNotExist:
            return Response({"detail": "Job not found."}, status=404)

        if SavedJob.objects.filter(job=job, user=request.user).exists():
            return Response({"detail": "Job already saved."}, status=400)

        saved_job = SavedJob.objects.create(job=job, user=request.user)
        serializer = SavedJobSerializer(saved_job)
        return Response(serializer.data, status=201)


class SavedJobListView(generics.ListAPIView):
    """
    Lists all jobs saved by the authenticated job seeker.

    - Only accessible by authenticated users with a 'job_seeker' role.
    - Returns saved job listings in reverse chronological order.

    Endpoint: GET /api/jobs/saved/
    Response: 200 OK with a list of saved jobs.
    """
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobSeeker]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).order_by("-saved_at")
