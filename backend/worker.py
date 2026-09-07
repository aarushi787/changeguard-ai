"""Run with RUN_WORKER=0 on API and python -m backend.worker in a separate process."""
from backend.main import worker
if __name__=='__main__': worker()
