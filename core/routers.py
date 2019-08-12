from rest_framework import routers
from treso import views as treso_views
from core import views as core_views
from perm import views as perm_views

router = routers.DefaultRouter()

router.register('perms', perm_views.PermViewSet, 'perm')
router.register('creneau', perm_views.CreneauViewSet)
router.register('signatures', perm_views.SignatureViewSet, 'signature')
router.register('facture/categories', treso_views.CategorieFactureRecueViewSet)
router.register('semestres', core_views.SemestreView)
router.register('facture/recue', treso_views.FactureRecueViewSet)
router.register('facture/cheque', treso_views.ChequeViewSet)
router.register('facture/emise', treso_views.FactureEmiseViewSet)
router.register('facture/emiserow', treso_views.FactureEmiseRowViewSet)
router.register('facture/reversements', treso_views.ReversementEffectueViewSet)
router.register('perm/articles', perm_views.ArticleViewSet)