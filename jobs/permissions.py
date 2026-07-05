from rest_framework import permissions


class IsEmployer(permissions.BasePermission):
    message = "Only employer accounts can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_employer)


class IsCandidate(permissions.BasePermission):
    message = "Only candidate accounts can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_candidate)


class IsJobOwnerOrReadOnly(permissions.BasePermission):
    """Only the employer who owns a job listing may edit or delete it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and obj.employer.user_id == request.user.id
