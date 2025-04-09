import logging
import threading
from time import time
from typing import List
from logging.handlers import RotatingFileHandler

class AsyncRotatingFileHandler(RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        self.buffer_size = kwargs.pop('buffer_size', 100)
        self.flush_interval = kwargs.pop('flush_interval', 1.0)
        super().__init__(*args, **kwargs)
        
        self._buffer = []
        self._last_flush = time()
        self._lock = threading.RLock()
        self._stopping = False
        self._start_worker()

    def _start_worker(self):
        def _worker():
            while not self._stopping:
                try:
                    if self._should_flush():
                        self._flush()
                except Exception:
                    pass
                threading.Event().wait(0.1)

        self._thread = threading.Thread(target=_worker)
        self._thread.daemon = True
        self._thread.start()

    def _should_flush(self):
        with self._lock:
            if not self._buffer:
                return False
            return (len(self._buffer) >= self.buffer_size or
                   time() - self._last_flush >= self.flush_interval)

    def _flush(self):
        with self._lock:
            if not self._buffer:
                return
                
            try:
                if self.maxBytes > 0:
                    current_size = self.stream.tell()
                    buffer_size = sum(len(msg) for msg in self._buffer)
                    if current_size + buffer_size > self.maxBytes:
                        self.doRollover()
                
                for msg in self._buffer:
                    self.stream.write(msg)
                self.stream.flush()
                self._buffer = []
                self._last_flush = time()
            except Exception:
                pass

    def emit(self, record):
        try:
            msg = self.format(record) + self.terminator
            with self._lock:
                self._buffer.append(msg)
        except Exception:
            self.handleError(record)

    def close(self):
        self._stopping = True
        if hasattr(self, '_thread'):
            self._flush()
        super().close()