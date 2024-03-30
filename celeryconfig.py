from celery import Celery

app = Celery('my_tasks', broker='redis://redis:6379/0')

import tasks