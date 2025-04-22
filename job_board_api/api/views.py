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
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data["email"])
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])
        return Response({"token": token.key, "user": UserSerializer(token.user).data})


class JobListingViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.all().order_by("-created_at")
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated, IsEmployerAndOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["location", "company_name"]
    search_fields = ["title", "description", "requirements", "location", "company_name"]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)


class ApplyJobView(generics.CreateAPIView):
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
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(applicant=self.request.user).order_by(
            "-created_at"
        )


class SaveJobView(APIView):
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
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobSeeker]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).order_by("-saved_at")
