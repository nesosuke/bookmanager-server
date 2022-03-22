import multiprocessing


bind = "localhost:8000"

# worker processes
workers = 2

# logging 
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "debug"
logconfig = None
