def car_in_pit(status):
    return any(status.pit)


def startlight_changing(status):
    return status.start > 1 and status.start != 9


def calculate_sleep_time(race, status):
    # if no race sleep a minute
    if race is None:
        return 60
    # if no status yet - sleep half a second
    if status is None:
        return 0.5
    # if someone in pit - sleep a fifth of a second
    if car_in_pit(status):
        return 0.2
    # if startlight changing - sleep a fifth of a second
    if startlight_changing(status):
        return 0.2
    return 0.5
