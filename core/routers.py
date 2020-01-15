from rest_framework import routers
from treso import views as treso_views
from core import views as core_views
from perm import views as perm_views
from payutc import views as payutc_views
from survey import views as survey_views
from tv import views as tv_views

router = routers.DefaultRouter()

router.register('perms', perm_views.PermViewSet, 'perm')
router.register('users', core_views.UserViewSet, 'user')
router.register('blocked/users', core_views.BlockedUserViewSet, 'blocked_user')
router.register('userrights', core_views.UserRightViewSet, 'user')
router.register('creneau', perm_views.CreneauViewSet, 'creneau')
router.register('perm/menus', perm_views.MenuViewSet)
router.register('signatures', perm_views.SignatureViewSet, 'signature')
router.register('facture/categories', treso_views.CategorieFactureRecueViewSet)
router.register('semesters', core_views.SemestreViewSet)
router.register('periodetva', core_views.PeriodeTVAViewSet)
router.register('facture/recue', treso_views.FactureRecueViewSet, 'facture_recue')
router.register('facture/cheque', treso_views.ChequeViewSet)
router.register('facture/emise', treso_views.FactureEmiseViewSet, 'facture_emise')
router.register('facture/emiserow', treso_views.FactureEmiseRowViewSet)
router.register('facture/reversements', treso_views.ReversementEffectueViewSet, 'facture_reversement')
router.register('perm/articles', perm_views.ArticleViewSet, 'articles')
router.register('payutc/goodies', payutc_views.GoodiesWinnerViewSet, 'goodies')
router.register('surveys', survey_views.SurveyViewSet, 'surveys')
router.register('survey/items', survey_views.SurveyItemViewSet, 'survey_tems')
router.register('survey/item/votes', survey_views.SurveyItemVoteViewSet, 'survey_item_votes')
router.register('admin/postes', core_views.PosteViewSet, 'postes')
router.register('admin/members', core_views.MemberViewSet, 'members')
router.register('perm/astreintes', perm_views.AstreinteViewSet, 'astreintes')
router.register('perm/creneaux', perm_views.CreneauViewSet, 'creneaux')
router.register('perm/halloween', perm_views.PermHalloweenViewSet, 'halloween')
router.register('request/perm', perm_views.RequestedPermViewSet, 'request_perm')

# WebTV
router.register('tvs', tv_views.WebTVViewSet)
router.register('tv/links', tv_views.WebTVLinkViewSet)
router.register('tv/media', tv_views.WebTVMediaViewSet)