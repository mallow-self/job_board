from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import User, JobListing, JobApplication
from .serializers import RegisterSerializer, UserSerializer, JobListingSerializer, JobApplicationSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from .permissions import IsEmployerAndOwnerOrReadOnly, IsJobSeeker


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data["email"])
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])
        return Response({"token": token.key, "user": UserSerializer(token.user).data})


class JobListingViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.all().order_by("-created_at")
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated, IsEmployerAndOwnerOrReadOnly]

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
