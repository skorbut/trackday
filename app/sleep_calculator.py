def car_in_pit(status):
    return any(status.pit)


def startlight_changing(status):
    return status.start > 1 and status.start != 9


def calculate_sleep_time(status):
    # if no status yet - sleep half a second
    if status is None:
        return 0.5
    # if someone in pit - sleep a tenth of a second
    if car_in_pit(status):
        return 0.1
    # if startlight changing - sleep a tenth of a second
    if startlight_changing(status):
        return 0.1
    # default
    return 0.1
