from app import app
from app.models import Timing, PitStop
from app.socket_connection import emit_status, emit_lap, emit_race_finished, emit_pit_stops


class EmittingRaceStatusObserver:
    def __init__(self, race):
        self.race = race
        self.pit_stops = [PitStop(num) for num in range(0, 8)]

    def notify_status(self, status):
        if self.update_pit_stops(status):
            emit_pit_stops(self.pit_stops)
        emit_status(status)

    def update_pit_stops(self, status):
        # identify pit status change
        changed = False
        for controller in range(0, 8):
            fuel = status.fuel[controller]
            pit_stop = self.pit_stops[controller]
            if status.pit[controller]:
                pit_stop.pit(fuel)
            else:
                changed = changed or pit_stop.track(fuel)
        return changed


class EmittingQuickRaceStatusObserver:
    def __init__(self):
        self.pit_stops = [PitStop(num) for num in range(0, 8)]

    def notify_status(self, status):
        if self.update_pit_stops(status):
            emit_pit_stops(self.pit_stops)
        emit_status(status)

    def update_pit_stops(self, status):
        # identify pit status change
        changed = False
        for controller in range(0, 8):
            fuel = status.fuel[controller]
            pit_stop = self.pit_stops[controller]
            if status.pit[controller]:
                pit_stop.pit(fuel)
            else:
                changed = changed or pit_stop.track(fuel)
        return changed


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

    def notify_time_past(self):
        return None


class LoggingDebugObserver:
    def notify_timer(self, time):
        app.logger.info("received a new time {}".format(time))

    def notify_status(self, status):
        app.logger.info("received a new status {}".format(status))
