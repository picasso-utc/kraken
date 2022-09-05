from django.urls import path

from elo.views import (
    BabyfootSoloEloRankingViewSet,
    EightPoolSoloEloRankingViewSet,
    BabyfootDuoEloRankingViewSet,
    EightPoolDuoEloRankingViewSet,
    BabyfootSoloRankedMatchesViewSet,
    EightPoolSoloRankedMatchesViewSet,
    BabyfootDuoRankedMatchesViewSet,
    EightPoolDuoRankedMatchesViewSet
)

urlpatterns = [
    path('solo/baby/ranking', BabyfootSoloEloRankingViewSet.as_view(), name='Classement ELO solo babyfoot'),
    path('solo/baby/matches', BabyfootSoloRankedMatchesViewSet.as_view(), name='Matchs solo babyfoot'),
    path('solo/8pool/ranking', EightPoolSoloEloRankingViewSet.as_view(), name='Classement ELO solo billard'),
    path('solo/8pool/matches', EightPoolSoloRankedMatchesViewSet.as_view(), name='Matchs solo billard'),
    path('duo/baby/ranking', BabyfootDuoEloRankingViewSet.as_view(), name='Classement ELO duo babyfoot'),
    path('duo/baby/matches', BabyfootDuoRankedMatchesViewSet.as_view(), name='Matchs duo babyfoot'),
    path('duo/8pool/ranking', EightPoolDuoEloRankingViewSet.as_view(), name='Classement ELO duo billard'),
    path('duo/8pool/matches', EightPoolDuoRankedMatchesViewSet.as_view(), name='Matchs duo billard')
]