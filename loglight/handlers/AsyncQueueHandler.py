import threading
import queue
import time
from typing import Callable

from loglight.handlers.BaseHandler import BaseHandler


class AsyncQueueHandler(BaseHandler):
    def __init__(self, underlying_handler, queue_size=1000, flush_interval=1.0, enable_internal_logging=True):
        super().__init__(enable_internal_logging)
        self.underlying_handler = underlying_handler
        self.queue = queue.Queue(maxsize=queue_size)
        self.flush_interval = flush_interval
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def emit(self, log_str: str):
        try:
            self.queue.put(log_str, block=False)
        except queue.Full:
            # Drop log if queue is full
            pass

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                log_str = self.queue.get(timeout=self.flush_interval)
                self.underlying_handler.emit(log_str)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.log_internal_error("async_handler_emit_failed", e)

    def flush(self):
        # Wait for all items in queue to be processed
        self.queue.join()

    def stop(self):
        self._stop_event.set()
        self._worker_thread.join()
        self.flush()
