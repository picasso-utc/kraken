from rest_framework.permissions import BasePermission, SAFE_METHODS
from core.models import UserRight

FULL_CONNEXION = 'full'
MENU_CONNEXION = 'menu'


class IsAdminUser(BasePermission):

    def has_permission(self, request, view):

        right = request.session.get('right')
        login = request.session.get('login')
        has_full_connexion = request.session.get('connexion') == FULL_CONNEXION
        return right =='A' and (UserRight.objects.filter(login=login, right=right).count()) and has_full_connexion


class IsMemberUser(BasePermission):

    def has_permission(self, request, view):

        right = request.session.get('right')
        login = request.session.get('login')
        has_full_connexion = request.session.get('connexion') == FULL_CONNEXION
        return (right =='A' or right == 'P') and (UserRight.objects.filter(login=login, right=right).count()) and has_full_connexion

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
