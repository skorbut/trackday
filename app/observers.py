from app import app
from app.models import Timing
from app.socket_connection import emit_status, emit_lap, emit_race_finished


class EmittingRaceStatusObserver:
    def __init__(self, race):
        self.race = race

    def notify_status(self, status):
        app.logger.info("Processing a new status")
        emit_status(status)


class EmittingQuickRaceStatusObserver:
    def notify_status(self, status):
        app.logger.info("Processing a new status")
        emit_status(status)



class EmittingRaceTimeObserver:
    def __init__(self, race):
        self.race = race
        self.timings = [Timing(num) for num in range(0, 8)]

    def notify_timer(self, time):
        app.logger.info("Processing a new time")
        controller = int(time.address)
        timing = self.timings[controller]
        timing.newlap(time)
        self.race.add_lap(controller, timing.lap_time)
        if timing.lap_time is not None and timing.laps > 0:
            emit_lap(time, timing)
        self.check_duration()

    def notify_time_past(self):
        self.check_duration()

    def check_duration(self):
        if self.race.has_reached_duration():
            self.race.stop()
            emit_race_finished(self.race.id)


class EmittingQuickRaceTimeObserver:
    def __init__(self):
        self.timings = [Timing(num) for num in range(0, 8)]

    def notify_timer(self, time):
        app.logger.info("Processing a new time")
        controller = int(time.address)
        timing = self.timings[controller]
        timing.newlap(time)
        if timing.lap_time is not None and timing.laps > 0:
            emit_lap(time, timing)


class LoggingDebugObserver:
    def notify_timer(self, time):
        app.logger.info("received a new time {}".format(time))

    def notify_status(self, status):
        app.logger.info("received a new status {}".format(status))
