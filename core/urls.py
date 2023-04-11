from . import settings
from core import views as core_views
from core.routers import router
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
                  # Authentication
                  path( 'api/auth/login', core_views.login, name='auth.login' ),
                  path( 'api/auth/login_callback', core_views.login_callback, name='auth.login_callback' ),
                  path( 'api/auth/badge', core_views.login_badge, name="auth.badge" ),
                  path( 'api/auth/username', core_views.login_username, name="auth.username" ),
                  path( 'api/auth/me', core_views.me, name='auth.me' ),
                  path( 'api/auth/logout', core_views.logout, name='auth.logout' ),


                  # Application Core
                  path('api/core/user', core_views.user_information),
                  path('api/core/semester/state', core_views.semestre_state),
                  path('api/core/semester/credit', core_views.semester_beginning_credit),
                  path('api/current/semester', core_views.current_semester),
                  path('api/core/team', core_views.get_team),
                  path('api/core/badge_scan', core_views.badge_scan),
                  path('api/core/covid_stat', core_views.covid_stat),
                  # path('api/core/export', core_views.get_export),

                  # Inclusion URL application Perm
                  path( 'api/perms/', include( 'perm.urls' ) ),

                  # Inclusion URL application Treso
                  path( 'api/treso/', include( 'treso.urls' ) ),

                  # Inclusion URL application Treso
                  path( 'api/treso2/', include( 'treso2.urls' ) ),

                  # Inclusion URL application Payutc
                  path( 'api/payutc/', include( 'payutc.urls' ) ),

                  # Inclusion URL application Survey
                  path( 'api/surveys/', include( 'survey.urls' ) ),

                  # Inclusion URL application TV
                  path( 'api/tv/', include( 'tv.urls' ) ),

                  # Inclusion URL covid
                  path( 'api/covid/', include( 'covid.urls' ) ),

                  # Inclusion URL mobile app related (Chopin)
                  path( 'api/chopin/', include( 'chopin.urls' ) ),

                  # include shotgun lib
                  path( 'api/shotgun/', include( 'shotgun.urls' ) ),

                  # include elo system lib
                  path( 'api/elo/', include( 'elo.urls' ) ),


                  # include stock system lib
                  path('api/stock/', include('stock.urls')),

                  # Inclusion fichier Router
                  # Ce dernier contient les Viewset, 1 URL = 1 CRUD
                  # CRUD = Create, Read, Update, Delete
                  path('api/', include(router.urls)),


              ] + static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
# Route pour ajouter les médias
