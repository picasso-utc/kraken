from rest_framework.permissions import BasePermission, SAFE_METHODS
from core.models import UserRight


class IsAdminUser(BasePermission):

    def has_permission(self, request, view):

        right = request.session.get('right')
        login = request.session.get('login')
        return right =='A' and (UserRight.objects.filter(login=login, right=right).count())


class IsMemberUser(BasePermission):

    def has_permission(self, request, view):

        right = request.session.get('right')
        login = request.session.get('login')
        return (right =='A' or right == 'P') and (UserRight.objects.filter(login=login, right=right).count())

class IsAuthenticatedUser(BasePermission):

    def has_permission(self, request, view):

        login = request.session.get('login')
        return (login is not None)

class IsMemberUserOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        right = request.session.get('right')
        login = request.session.get('login')
        isMemberUser = (right =='A' or right == 'P') and (UserRight.objects.filter(login=login, right=right).count())
        return isMemberUser or request.method in SAFE_METHODS
