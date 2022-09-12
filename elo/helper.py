import math
from typing import List, Union

from elo.models import RankedMatches, EloRanking, SoloRankedMatches, DuoRankedMatches, SoloEloRanking, DuoEloRanking


def get_newbie_coef(elo, nb_game):
    if nb_game < 20:
        return 40
    if elo < 2400:
        return 20
    return 10


def get_new_elo(old_elo, score_coef, newbie_coef, proba_fide, win):
    win_coef = 1 if win else 0

    return old_elo + score_coef * newbie_coef * (win_coef - proba_fide)


def calculate_new_elo(winner_elo, looser_elo, winner_nb_game, looser_nb_game, looser_score=5):
    winner_newbie_coef = get_newbie_coef(winner_elo, winner_nb_game)
    looser_newbie_coef = get_newbie_coef(looser_elo, looser_nb_game)

    elo_difference = looser_elo - winner_elo

    looser_proba_fide = 1 / (1 + 10 ** (-elo_difference / 400))
    winner_proba_fide = 1 - looser_proba_fide

    score_coef = (10 - looser_score) / 5

    new_winner_elo = int(get_new_elo(
        old_elo=winner_elo,
        score_coef=score_coef,
        newbie_coef=winner_newbie_coef,
        proba_fide=winner_proba_fide,
        win=True,
    ))
    new_looser_elo = int(get_new_elo(
        old_elo=looser_elo,
        score_coef=score_coef,
        newbie_coef=looser_newbie_coef,
        proba_fide=looser_proba_fide,
        win=False,
    ))

    return max(new_winner_elo, 0), max(new_looser_elo, 0)


def evaluate_first_elo(player: EloRanking, game_list: List[Union[SoloRankedMatches, DuoRankedMatches]]):
    nb_game = len(game_list)
    opponents_elo_sum = 0
    nb_win = 0

    for game in game_list:
        win = player == game.winner
        player_elo = game.elo_winner if win else game.elo_looser
        score_difference = 10 - game.score_looser if game.support == 'B' else 10
        opponents_elo_sum += 1000 if player_elo is None else player_elo
        if win:
            nb_win += 0.5 + score_difference / 20
        else:
            nb_win += 0.5 - score_difference / 20

    win_proba = nb_win / nb_game
    elo_avg = opponents_elo_sum / nb_game

    if win_proba < 0.5:
        player_first_elo = int(elo_avg - 400 * math.log10((1 / win_proba) - 1)) if win_proba != 0 else elo_avg - 250
    elif win_proba > 0.5:
        player_first_elo = int(elo_avg + 20 * (2 * nb_win - nb_game))
    else:
        player_first_elo = int(elo_avg)

    return max(player_first_elo, 0)


def get_ranked_matches(RankedMatchesModel: RankedMatches, team: Union[SoloEloRanking, DuoEloRanking]):
    team_win_matches = list(RankedMatchesModel.objects.filter(winner=team))
    team_loose_matches = list(RankedMatchesModel.objects.filter(looser=team))

    return team_win_matches + team_loose_matches


def update_matches(player: EloRanking, game_list: List[Union[SoloRankedMatches, DuoRankedMatches]]):
    for game in game_list:
        win = player == game.winner

        if win:
            winner_elo = player.elo
            looser_elo = game.looser.elo
            game.elo_winner = winner_elo
        else:
            winner_elo = game.winner.elo
            looser_elo = player.elo
            game.elo_looser = looser_elo

        if winner_elo is not None and looser_elo is not None:
            new_winner_elo, new_looser_elo = calculate_new_elo(
                winner_elo=winner_elo,
                looser_elo=looser_elo,
                winner_nb_game=game.winner.nb_game,
                looser_nb_game=game.looser.nb_game,
                looser_score=game.score_looser if game.support == 'B' else 5
            )

            if win:
                opponent = game.looser
                opponent.elo = new_looser_elo
            else:
                opponent = game.looser
                opponent.elo = new_winner_elo

            opponent.save()

        game.save()

