def check_macro_announcement():
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    keys = ['interest_rate_announcement_date', 'cpi_announcement_date', 'ppi_announcement_date']

    for key in keys:
        announcement_date = read_latest_data(key, datetime)
        if announcement_date is not None:
            diff = announcement_date - now
            if diff.total_seconds() >= 0 and diff <= timedelta(days=3):
                return True

    return False
