# chatGPT
from django.core.management.base import BaseCommand
from movies.utils import sync_genres  # the function we wrote before

class Command(BaseCommand):
    help = "Sync genres from TMDB API into the database"

    def handle(self, *args, **kwargs):
        sync_genres()
        self.stdout.write(self.style.SUCCESS("Genres synced successfully"))
