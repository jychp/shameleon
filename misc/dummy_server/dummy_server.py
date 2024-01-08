import errno
import os
import time

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class FileLockException(Exception):
    pass


class FileLock:
    """ A file locking mechanism that has context-manager support so
        you can use it in a with statement. This should be relatively cross
        compatible as it doesn't rely on msvcrt or fcntl for the locking.
    """

    def __init__(self, file_name, timeout=10, delay=.05):
        """ Prepare the file locker. Specify the file to lock and optionally
            the maximum timeout and the delay between each attempt to lock.
        """
        if timeout is not None and delay is None:
            raise ValueError("If timeout is not None, then delay must not be None.")
        self.is_locked = False
        self.lockfile = os.path.join(os.getcwd(), "%s.lock" % file_name)
        self.file_name = file_name
        self.timeout = timeout
        self.delay = delay

    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again
            every `wait` seconds. It does this until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it throws
            an exception.
        """
        start_time = time.time()
        while True:
            try:
                self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                self.is_locked = True  # moved to ensure tag only when locked
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if self.timeout is None:
                    raise FileLockException(f"Could not acquire lock on {self.file_name}")
                if (time.time() - start_time) >= self.timeout:
                    raise FileLockException("Timeout occured.")
                time.sleep(self.delay)

    def release(self):
        """ Get rid of the lock by deleting the lockfile.
            When working in a `with` statement, this gets automatically
            called at the end.
        """
        if self.is_locked:
            os.close(self.fd)
            os.unlink(self.lockfile)
            self.is_locked = False

    def __enter__(self):
        """ Activated when used in the with statement.
            Should automatically acquire a lock to be used in the with block.
        """
        if not self.is_locked:
            self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
        """
        if self.is_locked:
            self.release()

    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a lockfile
            lying around.
        """
        self.release()


class Elements(BaseModel):
    elements: list[str]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/in")
def get_input():
    try:
        orders = []
        with FileLock('in.txt'):
            with open('in.txt') as f:
                for order in f:
                    order = order.strip()
                    if len(order) == 0:
                        continue
                    orders.append(order)
            with open('in.txt', 'w') as f:
                f.write('')
        return {"elements": orders}
    except FileNotFoundError:
        return {"elements": []}


@app.post("/in")
def post_input(payload: Elements):
    with FileLock('in.txt'):
        with open('in.txt', 'a') as f:
            for element in payload.elements:
                f.write(f'{element}\n')
    return {}


@app.post("/out")
def post_output(payload: Elements):
    with FileLock('out.txt'):
        with open('out.txt', 'a') as f:
            for element in payload.elements:
                f.write(f'{element}\n')
    return {}


@app.get("/out")
def get_result():
    try:
        results = []
        with FileLock('out.txt'):
            with open('out.txt') as f:
                for order in f:
                    order = order.strip()
                    if len(order) == 0:
                        continue
                    results.append(order)
            with open('out.txt', 'w') as f:
                f.write('')
        return {"elements": results}
    except FileNotFoundError:
        return {"elements": []}
