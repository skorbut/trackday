from app import app
from app import track_listener
from app.observers import EmittingRaceStatusObserver, EmittingRaceTimeObserver, EmittingQuickRaceStatusObserver, EmittingQuickRaceTimeObserver


def start(race):
    # set status to started
    if race is not None and race.status == 'created':
        race.start()
    # register observers and start track listener
    return track_listener.start_track_listener(EmittingRaceStatusObserver(race), EmittingRaceTimeObserver(race))


def attach(race):
    if not track_listener.track_listener_running():
        track_listener.start_track_listener(EmittingRaceStatusObserver(race), EmittingRaceTimeObserver(race))

    return track_listener.track_listener_running()


def attach_quick_race():
    if not track_listener.track_listener_running():
        track_listener.start_track_listener(EmittingQuickRaceStatusObserver(), EmittingQuickRaceTimeObserver())
    return track_listener.track_listener_running()


def finish(race):
    # set race to stopped
    app.logger.info("Race is " + repr(race))
    if race is not None and (race.status == 'started' or race.status == 'created'):
        race.stop()
    # stop track listener
    track_listener.stop_track_listener()
