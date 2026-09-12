from django.apps import AppConfig


class LeaderboardConfig(AppConfig):
    name = 'LeaderBoard'

    def ready(self):
        import LeaderBoard.signals
