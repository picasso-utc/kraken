from django.db import models

SUPPORT_CHOICES = [
    ('B', 'Babyfoot'),
    ('E', 'Billard')
]


class EloRanking(models.Model):
    id = models.BigAutoField(primary_key=True)
    elo = models.IntegerField(null=True)
    nb_game = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, null=False)

    class Meta:
        ordering = ['-elo']


class SoloEloRanking(EloRanking):
    login = models.CharField(max_length=8, null=False)
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    support = models.CharField(max_length=1, choices=SUPPORT_CHOICES)

    def __str__(self):
        return f"{self.support} - {self.first_name} {self.last_name}"

    class Meta:
        unique_together = (('login', 'support'),)


class DuoEloRanking(EloRanking):
    team_name = models.CharField(max_length=30, blank=True)
    login_a = models.CharField(max_length=8, null=False)
    first_name_a = models.CharField(max_length=20, blank=True)
    last_name_a = models.CharField(max_length=20, blank=True)
    login_b = models.CharField(max_length=8, null=False)
    first_name_b = models.CharField(max_length=20, blank=True)
    last_name_b = models.CharField(max_length=20, blank=True)
    support = models.CharField(max_length=1, choices=SUPPORT_CHOICES)

    def __str__(self):
        return f"{self.support} - {self.first_name_a} {self.last_name_a} & {self.first_name_b} {self.last_name_b}"

    class Meta:
        unique_together = (('login_a', 'login_b', 'support'),)


class RankedMatches(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    elo_winner = models.IntegerField(null=True, blank=True)
    elo_looser = models.IntegerField(null=True, blank=True)
    score_looser = models.IntegerField(null=True)
    support = models.CharField(max_length=1, choices=SUPPORT_CHOICES)

    class Meta:
        ordering = ['-date']


class SoloRankedMatches(RankedMatches):
    winner = models.ForeignKey(SoloEloRanking, related_name='winner', on_delete=models.SET_NULL, null=True)
    looser = models.ForeignKey(SoloEloRanking, related_name='looser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if self.support == 'B':
            return f"{self.date} | {self.winner} vs {self.looser} | 10 - {self.score_looser}"
        return f"{self.date} | {self.winner} vs {self.looser}"


class DuoRankedMatches(RankedMatches):
    winner = models.ForeignKey(DuoEloRanking, related_name='winner_team', on_delete=models.SET_NULL, null=True)
    looser = models.ForeignKey(DuoEloRanking, related_name='looser_team', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if self.support == 'B':
            return f"{self.date} | {self.winner} vs {self.looser} | 10 - {self.score_looser}"
        return f"{self.date} | {self.winner} vs {self.looser}"
