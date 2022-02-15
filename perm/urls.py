from django.urls import path

from perm import views as perm_views

urlpatterns = [
    path('payutc/article/<int:id>', perm_views.create_payutc_article),
    path('sales/article/<int:id>', perm_views.get_article_sales),
    path('sales/<int:id>', perm_views.get_creneau_sales),
    path('current/creneau', perm_views.get_current_creneau),
    path('current/public/creneau', perm_views.get_current_public_creneau),
    path('menu/orders/<int:id>', perm_views.get_order_lines),
    path('menu/served/<int:id>', perm_views.set_ordeline_served),
    path('menu/staff/<int:id>', perm_views.set_ordeline_staff),
    path('menu/closed/<int:id>', perm_views.set_menu_closed),
    path('mail', perm_views.send_mail),
    path('user/astreintes', perm_views.get_user_astreintes),
    path('week/astreintes', perm_views.get_week_astreintes),
    path('reminder', perm_views.send_creneau_reminder),
    path('calendar', perm_views.get_week_calendar),
    path('count/halloween', perm_views.get_halloween_article_count),
    path('signature/<int:creneau_id>', perm_views.get_creaneau_signature),
    path('notation/all', perm_views.get_perms_for_notation),
    path('notation/<int:perm_id>', perm_views.get_perm_for_notation),
    path('public/may/request', perm_views.perm_may_be_requested),
    path('update/may/request', perm_views.update_perm_may_be_requested_setting),
    path('requested/pdf', perm_views.get_pdf_requested_perms),
    path('assos', perm_views.get_portal_assos)
]
