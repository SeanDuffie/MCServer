""" @file scheduler.py
    @author Sean Duffie
    @brief Scheduler thread wrapper class that runs the backup function on every interval
"""
import datetime
import logging
import threading

### LOGGING SECTION ###
logger = logging.getLogger("BACKUP")

class Scheduler(threading.Timer):
    """ Manages the frequency and intervals of calls to the backup function.
    Construct one for each interval by passing in the amount of 

    Inherits from the threading.Timer class
    """
    def __init__(self, interval, function, args=None, kwargs=None):
        threading.Timer.__init__(self, interval, function, args, kwargs)

        self.start_time = datetime.datetime.now()
        self.tprev = self.start_time
        self.invl = datetime.timedelta(seconds=self.interval)
        self.tnext = self.next_time(self.start_time, self.invl)

        logger.warning(
            "Seconds until First %s Backup: %s",
            *self.args,
            (self.tnext - self.tprev).total_seconds()
        )

    def next_time(self, prev: datetime.datetime, interval: datetime.timedelta):
        """ Calculates the next timestamp that "run" will be active.

        Args:
            prev (datetime.datetime): Timestamp of last action.
            interval (datetime.timedelta): Seconds in between actions.

        Returns:
            datetime.datetime: Timestamp of the next run.
        """
        if interval > datetime.timedelta(seconds=86399):
            # If the program is started in the morning between 12AM and 6AM, round next time down
            if prev.hour < 6:
                day = prev.day
            # Otherwise, round next time up
            else:
                day = prev.day + interval.days

            # Always back up at the next 6AM occurrence.
            nxt = datetime.datetime(
                year=prev.year,
                month=prev.month,
                day=day,
                hour=6,
                minute=0,
                second=0,
                microsecond=0
            )
        else:
            # Always back up at the top of the next hour
            nxt = datetime.datetime(
                year=prev.year,
                month=prev.month,
                day=prev.day + interval.days,
                hour=(prev.hour + (interval.seconds // 3600)) % 24,
                minute=0,
                second=0,
                microsecond=0
            )
        logger.info(
            "Next %s Backup time is at %s (currently %s)",
            *self.args,
            nxt,
            datetime.datetime.now()
        )
        return nxt

    def get_remaining(self):
        """ Calculates and returns time remaining before next backup.

        Returns:
            datetime.timedelta: Amount of time remaining before next backup.
        """
        return self.tnext - datetime.datetime.now()

    def run(self):
        """ Function callback that is launched whenever the Scheduler thread is started. """
        while not self.finished.wait((self.tnext - self.tprev).total_seconds()):
            self.tprev = self.tnext
            self.tnext = self.next_time(self.tprev, self.invl)

            self.function(*self.args, **self.kwargs)
        logger.info("Scheduler finished.")
