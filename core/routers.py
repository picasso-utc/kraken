from rest_framework import routers
from treso import views as treso_views
from core import views as core_views
from perm import views as perm_views
from payutc import views as payutc_views
from tv import views as tv_views

router = routers.DefaultRouter()

router.register('perms', perm_views.PermViewSet, 'perm')
router.register('users', core_views.UserViewSet, 'user')
router.register('creneau', perm_views.CreneauViewSet)
router.register('perm/menus', perm_views.MenuViewSet)
router.register('signatures', perm_views.SignatureViewSet, 'signature')
router.register('facture/categories', treso_views.CategorieFactureRecueViewSet)
router.register('semesters', core_views.SemestreViewSet)
router.register('periodetva', core_views.PeriodeTVAViewSet)
router.register('facture/recue', treso_views.FactureRecueViewSet)
router.register('facture/cheque', treso_views.ChequeViewSet)
router.register('facture/emise', treso_views.FactureEmiseViewSet)
router.register('facture/emiserow', treso_views.FactureEmiseRowViewSet)
router.register('facture/reversements', treso_views.ReversementEffectueViewSet)
router.register('perm/articles', perm_views.ArticleViewSet)
router.register('payutc/goodies', payutc_views.GoodiesWinnerViewSet, 'goodies')


# WebTV
router.register('tvs', tv_views.WebTVViewSet)
# router.register('tv/config', tv_views.WebTVConfigurationViewSet)
router.register('config/tv', tv_views.WebTVConfigurationViewSet)
router.register('tv/media', tv_views.TVMediaViewSet)