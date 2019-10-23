from rest_framework.permissions import BasePermission, SAFE_METHODS
from core.models import UserRight
from core.settings import MAIL_REMINDER_APP_KEY

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
        return (right =='A' or right == 'M') and (UserRight.objects.filter(login=login, right=right).count()) and has_full_connexion

class IsAuthenticatedUser(BasePermission):

    def has_permission(self, request, view):

        login = request.session.get('login')
        return (login is not None)


class IsMemberUserOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        right = request.session.get('right')
        login = request.session.get('login')
        isMemberUser = (right =='A' or right == 'M') and (UserRight.objects.filter(login=login, right=right).count())
        return isMemberUser or request.method in SAFE_METHODS


class CanAccessMenuFunctionnalities(BasePermission):

    def has_permission(self, request, view):

        right = request.session.get('right')
        login = request.session.get('login')
        connexion = request.session.get('connexion')
        has_full_connexion = connexion == FULL_CONNEXION
        isMemberUser = (right =='A' or right == 'M') and (UserRight.objects.filter(login=login, right=right).count()) and has_full_connexion
        return isMemberUser or connexion == MENU_CONNEXION


class HasApplicationRight(BasePermission):

    def has_permission(self, request, view):

        app_key = request.GET.get('app_key')
        return app_key == MAIL_REMINDER_APP_KEY
