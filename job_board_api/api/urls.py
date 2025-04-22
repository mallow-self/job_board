from django.urls import path, include
from .views import RegisterView, CustomAuthToken, JobListingViewSet, ApplyJobView, AppliedJobsListView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"job-listings", JobListingViewSet, basename="job-listings")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomAuthToken.as_view(), name="login"),
    path("jobs/apply/<int:job_id>/", ApplyJobView.as_view(), name="apply-job"),
    path("jobs/applied/", AppliedJobsListView.as_view(), name="applied-jobs"),
]
