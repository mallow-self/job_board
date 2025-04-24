from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter


class CustomAPIRootView(APIView):
    api_root_dict = {}
    def get(self, request, *args, **kwargs):
        return Response(
            {
                "job-listings": request.build_absolute_uri("job-listings/"),
                "create-user-profile": request.build_absolute_uri("user-profile/"),
                "update-user-profile": request.build_absolute_uri(
                    "user-profile/1/"
                ),  # sample ID
                "login": request.build_absolute_uri("login/"),
                "apply-job": request.build_absolute_uri(
                    "jobs/apply/1/"
                ),  # sample job ID
                "applied-jobs": request.build_absolute_uri("jobs/applied/"),
                "save-job": request.build_absolute_uri("jobs/save/1/"),  # sample job ID
                "saved-jobs": request.build_absolute_uri("jobs/saved/"),
            }
        )


class CustomRouter(DefaultRouter):
    APIRootView = CustomAPIRootView
