import json
import requests
from apscheduler.schedulers.background import BackgroundScheduler


class Metadata:
    json = None

    def __init__(self):
        # Schedule metadata json for refresh once per 30 minutes
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=self.load, trigger="interval", minutes=30)
        scheduler.start()

    def load(self):
        self.json = json.loads(requests.get(f"https://hbb1.oscwii.org/metadata.json").text)
        print("Reloaded metadata JSON")

    def title_id_by_name(self, internal_name):
        try:
            return self.json[internal_name][5]
        except Exception:
            return None

    def title_version_by_name(self, internal_name):
        try:
            return self.json[internal_name][4]
        except Exception:
            return None
