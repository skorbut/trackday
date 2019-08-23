bind = 'localhost:8000'

worker_class = 'eventlet'
workers = 1

timeout = 60
accesslog = 'logs/gunicorn-access.log'
errorlog = 'logs/gunicorn-error.log'
capture_output = True
