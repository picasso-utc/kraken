import math


def get_newbie_coef(elo, nb_game):
    if nb_game < 20:
        return 40
    if elo < 2400:
        return 20
    return 10


def get_new_elo(old_elo, score_coef, newbie_coef, win, proba_fide):
    win_coef = 1 if win else 0

    return old_elo + score_coef * newbie_coef * (win_coef - proba_fide)


def calculate_new_elo(winner_elo, looser_elo, winner_nb_game, looser_nb_game, winner_score=5, looser_score=0):
    winner_newbie_coef = get_newbie_coef(winner_elo, winner_nb_game)
    looser_newbie_coef = get_newbie_coef(looser_elo, looser_nb_game)

    elo_difference = looser_elo - winner_elo

    looser_proba_fide = 1 / (1 + 10 ** (-elo_difference / 400))
    winner_proba_fide = 1 - looser_proba_fide

    score_coef = (winner_score - looser_score) / 5

    new_winner_elo = int(get_new_elo(
        old_elo=winner_elo,
        score_coef=score_coef,
        newbie_coef=winner_newbie_coef,
        win=True,
        proba_fide=winner_proba_fide
    ))
    new_looser_elo = int(get_new_elo(
        old_elo=looser_elo,
        score_coef=score_coef,
        newbie_coef=looser_newbie_coef,
        win=False,
        proba_fide=looser_proba_fide
    ))

    return new_winner_elo, new_looser_elo


def evaluate_first_elo(game_list):
    nb_game = len(game_list)
    elo_sum = 0
    nb_win = 0

    for [elo, score_difference, win] in game_list:
        elo_sum += 1000 if elo is None else elo
        nb_win += 0.5 if win else 0
        nb_win += 0.5 - score_difference / 20

    win_proba = nb_win / nb_game
    elo_avg = elo_sum / nb_game

    if win_proba < 0.5:
        return int(elo_avg - 400 * math.log10((1 / win_proba) - 1))
    if win_proba > 0.5:
        return int(elo_avg + 20 * (2 * nb_win - nb_game))

    return int(elo_avg)


def get_ranked_matches(RankedMatchesModel, support, team, opponent_elo, score_difference, win):
    team_win_matches_queryset = list(RankedMatchesModel.objects.filter(winner__id=team.id))
    team_loose_matches_queryset = list(RankedMatchesModel.objects.filter(looser__id=team.id))

    if support == 'E':
        win_matches = [
            [game.elo_looser, 5, True] for game in team_win_matches_queryset
        ]
        loose_matches = [
            [game.elo_winner, 5, False] for game in team_loose_matches_queryset
        ]
    else:
        win_matches = [
            [game.elo_looser, game.score_winner - game.score_looser, True] for game in team_win_matches_queryset
        ]
        loose_matches = [
            [game.elo_winner, game.score_winner - game.score_looser, False] for game in team_loose_matches_queryset
        ]

    actual_game = [[opponent_elo, score_difference, win]]

    return win_matches + loose_matches + actual_game
