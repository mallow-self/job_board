from rest_framework import permissions


class IsEmployerAndOwnerOrReadOnly(permissions.BasePermission):
    """
    Only the employer who created the job can edit/delete.
    All authenticated users can view.
    """

    def has_permission(self, request, view):
        # Allow listing and retrieve to all authenticated users
        if view.action in ["list", "retrieve"]:
            return request.user.is_authenticated
        # Allow create/update/delete only to employer users
        return request.user.is_authenticated and request.user.user_type == "employer"

    def has_object_permission(self, request, view, obj):
        # Allow safe methods for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only employer who created the listing can edit/delete
        return obj.employer == request.user and request.user.user_type == "employer"


class IsJobSeeker(permissions.BasePermission):
    """
    Only job seekers are allowed to perform this action.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "job_seeker"
