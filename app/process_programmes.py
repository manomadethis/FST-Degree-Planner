from app.models import Programmes


def process_programmes(programme_name):
    # Fetch the programme
    programme = Programmes.query.get(programme_name)