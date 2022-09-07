from rest_framework import serializers

from core.services.ginger import GingerClient
from elo.helper import evaluate_first_elo, calculate_new_elo, get_ranked_matches, update_matches
from elo.models import SoloRankedMatches, DuoRankedMatches, SoloEloRanking, DuoEloRanking


class SoloEloRankingSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data.pop('elo', None)
        validated_data.pop('nb_game', None)
        validated_data.pop('is_active', None)
        return SoloEloRanking.objects.create(**validated_data)

    def validate(self, data):
        g = GingerClient()

        try:
            user = g.get_user_info(data['login'])

            data['first_name'] = user['data']['prenom']
            data['last_name'] = user['data']['nom']

        except Exception:
            raise serializers.ValidationError("Login not found")

        return data

    class Meta:
        model = SoloEloRanking
        exclude = list()


class DuoEloRankingSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data.pop('elo', None)
        validated_data.pop('nb_game', None)
        validated_data.pop('is_active', None)
        return DuoEloRanking.objects.create(**validated_data)

    def validate(self, data):
        login_a = data['login_a']
        login_b = data['login_b']
        support = data['support']

        g = GingerClient()

        try:
            user_a = g.get_user_info(login_a)

            data['first_name_a'] = user_a['data']['prenom']
            data['last_name_a'] = user_a['data']['nom']

        except Exception:
            raise serializers.ValidationError("Login a not found")

        try:
            user_b = g.get_user_info(login_b)

            data['first_name_b'] = user_b['data']['prenom']
            data['last_name_b'] = user_b['data']['nom']

        except Exception:
            raise serializers.ValidationError("Login b not found")

        if DuoEloRanking.objects.filter(login_a=login_b, login_b=login_a, support=support).count() == 1:
            raise serializers.ValidationError("Team already exist")

        return data

    class Meta:
        model = DuoEloRanking
        exclude = list()


class RankedMatchesSerializer(serializers.ModelSerializer):
    @staticmethod
    def process_validated_data(RankedMatchesModel, validated_data):
        support = validated_data['support']

        winner = validated_data['winner']
        looser = validated_data['looser']

        winner_elo = winner.elo
        looser_elo = looser.elo

        winner.nb_game += 1
        looser.nb_game += 1

        validated_data['elo_winner'] = winner_elo
        validated_data['elo_looser'] = looser_elo

        if support == 'E':
            validated_data.pop('winner_score', None)
            validated_data.pop('looser_score', None)

        looser_score = validated_data.get('looser_score', 5)

        if winner.nb_game > 5 and looser.nb_game > 5:
            winner.elo, looser.elo = calculate_new_elo(
                winner_elo=winner.elo,
                looser_elo=looser.elo,
                winner_nb_game=winner.nb_game,
                looser_nb_game=looser.nb_game,
                looser_score=looser_score
            )

        if winner.nb_game == 5:
            ranked_matches = get_ranked_matches(RankedMatchesModel=RankedMatchesModel, team=winner)
            ranked_matches.append(RankedMatchesModel(**validated_data))

            winner.elo = evaluate_first_elo(winner, ranked_matches)
            update_matches(winner, ranked_matches)

        if looser.nb_game == 5:
            ranked_matches = get_ranked_matches(RankedMatchesModel=RankedMatchesModel, team=looser)
            ranked_matches.append(RankedMatchesModel(**validated_data))

            looser.elo = evaluate_first_elo(looser, ranked_matches)
            update_matches(looser, ranked_matches)

        winner.save()
        looser.save()

        return RankedMatchesModel.objects.create(**validated_data)

    def validate(self, data):
        winner = data.get('winner')
        looser = data.get('looser')
        score_looser = data.get('score_looser')
        support = data.get('support')

        if winner.support != support or looser.support != support:
            raise serializers.ValidationError("Players must have the appropriate support")

        if winner is None or looser is None:
            raise serializers.ValidationError("Both players are required")

        if winner == looser:
            raise serializers.ValidationError("Players must be different")

        if support == 'B' and score_looser is None:
            raise serializers.ValidationError("Babyfoot matches must have score")

        if support == 'B' and (score_looser < 0 or score_looser > 10):
            raise serializers.ValidationError("Scores must be between 0 and 10")

        return data


class SoloRankedMatchesSerializer(RankedMatchesSerializer):
    def create(self, validated_data):
        return super().process_validated_data(SoloRankedMatches, validated_data)

    class Meta:
        model = SoloRankedMatches
        exclude = list()


class DuoRankedMatchesSerializer(RankedMatchesSerializer):
    def create(self, validated_data):
        return super().process_validated_data(DuoRankedMatches, validated_data)

    def validate(self, data):
        super().validate(data)

        winner_team = data.get('winner')
        looser_team = data.get('looser')

        if winner_team.login_a in [looser_team.login_a, looser_team.login_b] or \
                winner_team.login_b in [looser_team.login_a, looser_team.login_b]:
            raise serializers.ValidationError("A player can't be in both team")

        return data

    class Meta:
        model = DuoRankedMatches
        exclude = list()
