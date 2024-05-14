def process_minors(minor_name):
    # Fetch the minor
    minor = Minors.query.get(minor_name)