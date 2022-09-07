from rest_framework.generics import ListCreateAPIView

from core.permissions import IsAdminUser
from elo.models import SoloEloRanking, DuoEloRanking, SoloRankedMatches, DuoRankedMatches
from elo.serializers import (
    SoloEloRankingSerializer,
    DuoEloRankingSerializer, SoloRankedMatchesSerializer, DuoRankedMatchesSerializer,
)


class EloSystemViewSet(ListCreateAPIView):
    def get_permissions(self):
        permission_classes = []

        #if self.request.method == 'POST':
        #    permission_classes = [IsAdminUser()]

        return permission_classes

# Elo Ranking ViewSets #

class BabyfootSoloEloRankingViewSet(EloSystemViewSet):
    queryset = SoloEloRanking.objects.filter(support='B', is_active=True)
    serializer_class = SoloEloRankingSerializer


class EightPoolSoloEloRankingViewSet(EloSystemViewSet):
    queryset = SoloEloRanking.objects.filter(support='E', is_active=True)
    serializer_class = SoloEloRankingSerializer


class BabyfootDuoEloRankingViewSet(EloSystemViewSet):
    queryset = DuoEloRanking.objects.filter(support='B', is_active=True)
    serializer_class = DuoEloRankingSerializer


class EightPoolDuoEloRankingViewSet(EloSystemViewSet):
    queryset = DuoEloRanking.objects.filter(support='E', is_active=True)
    serializer_class = DuoEloRankingSerializer


# Matches ViewSets #

class BabyfootSoloRankedMatchesViewSet(EloSystemViewSet):
    queryset = SoloRankedMatches.objects.filter(support='B')
    serializer_class = SoloRankedMatchesSerializer


class EightPoolSoloRankedMatchesViewSet(EloSystemViewSet):
    queryset = SoloRankedMatches.objects.filter(support='E')
    serializer_class = SoloRankedMatchesSerializer


class BabyfootDuoRankedMatchesViewSet(EloSystemViewSet):
    queryset = DuoRankedMatches.objects.filter(support='B')
    serializer_class = DuoRankedMatchesSerializer


class EightPoolDuoRankedMatchesViewSet(EloSystemViewSet):
    queryset = DuoRankedMatches.objects.filter(support='E')
    serializer_class = DuoRankedMatchesSerializer
