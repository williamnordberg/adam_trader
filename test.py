



def compare_google_search_trends(last_hour: int, two_hours_before: int) -> Tuple[float, float]:
    """
    Compare the search trends between the last hour and two hours before.

    Args:
        last_hour (int): The search volume of the last hour.
        two_hours_before (int): The search volume of two hours before the last hour.

    Returns:
        tuple: bullish and bearish probabilities based on the search trends.
    """
    if last_hour >= two_hours_before:
        if last_hour >= (two_hours_before * 1.25):
            return 1, 0
        elif last_hour >= (two_hours_before * 1.20):
            return 0.85, 0.15
        elif last_hour >= (two_hours_before * 1.15):
            return 0.75, 0.25
        elif last_hour >= (two_hours_before * 1.1):
            return 0.6, 0.4
        return 0, 0

    elif last_hour <= two_hours_before:
        if two_hours_before >= (last_hour * 1.25):
            return 0, 1
        elif two_hours_before >= (last_hour * 1.2):
            return 0.15, 0.85
        elif two_hours_before >= (last_hour * 1.15):
            return 0.25, 0.75
        elif two_hours_before >= (last_hour * 1.1):
            return 0.4, 0.6
        return 0, 0

    return 0, 0


def compare_reddit(current_activity: float, previous_activity: float) -> Tuple[float, float]:

    activity_percentage = (current_activity - previous_activity) / previous_activity * 100
    if activity_percentage > 0:
        if activity_percentage >= 30:
            return 1, 0
        elif activity_percentage >= 20:
            return 0.9, 0.1
        elif activity_percentage >= 15:
            return 0.8, 0.2
        elif activity_percentage >= 10:
            return 0.7, 0.3
        elif activity_percentage >= 5:
            return 0.6, 0.4

    elif activity_percentage <= 0:
        if activity_percentage <= -30:
            return 0, 1
        elif activity_percentage <= -20:
            return 0.1, 0.9
        elif activity_percentage <= -15:
            return 0.2, 0.8
        elif activity_percentage <= -10:
            return 0.3, 0.7
        elif activity_percentage <= -5:
            return 0.4, 0.6

    return 0, 0
