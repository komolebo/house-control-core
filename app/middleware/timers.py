from apscheduler.schedulers.background import BackgroundScheduler

class ScheduleItems:
    CONN_POLL = 'conn_poll'


class Scheduler:
    scheduler = BackgroundScheduler()

    @classmethod
    def register_job(cls, _cb, _id, _period_sec):
        if cls.scheduler.get_job(_id) is not None:
            raise Exception("Job {} is already running".format(_id))
        cls.scheduler.add_job(_cb, 'interval', seconds=_period_sec, id=_id)
        cls.scheduler.start()

    @classmethod
    def remove_job(cls, _id):
        cls.scheduler.remove_job(_id)


class TimerHandler:
    sched = BackgroundScheduler()

    job_id_list = []

    def __init__(self, callback, period_sec):
        self.job_id = self._get_free_job_id()
        if self.job_id is None:
            raise Exception("Job ID cannot be calculated")

        self.set_period_callback(callback, period_sec, self.job_id)
        self.job_id_list.append(self.job_id)

    @classmethod
    def _get_free_job_id(cls):
        # find free id
        for i in range(len(cls.job_id_list) + 1):
            if not i in cls.job_id_list:
                return i
        return None

    @classmethod
    def set_period_callback(cls, callback, period_sec, job_id):
        if not cls.sched.state:
            cls.sched.start()
        cls.sched.add_job(callback, 'interval', seconds=period_sec, id=str(job_id))

    @classmethod
    def unset_callback(cls, job_id):
        cls.sched.remove_job(job_id)
        if not cls.sched.get_jobs():  # TODO: check when need this part
            cls.sched.pause()

