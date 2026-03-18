# movies/tasks.py
from celery import shared_task
import time

@shared_task
def sync_tmdb_movies():
    # Logic to fetch from TMDB and update your Cache/DB
    print("Syncing with TMDB...")
    return "Sync Complete"