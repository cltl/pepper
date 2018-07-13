import numpy as np

from threading import Thread
from Queue import Queue
from time import time

from collections import deque

import logging


class AbstractMicrophone(object):
    def __init__(self, rate, channels, callbacks):
        self._rate = rate
        self._channels = channels
        self._callbacks = callbacks

        self._queue = Queue()
        self._processor_thread = Thread(target=self._processor)
        self._processor_thread.daemon = True
        self._processor_thread.start()

        self._log = logging.getLogger(self.__class__.__name__)

        self._dt_threshold_multiplier = 1.5
        self._dt_buffer = deque([], maxlen=100)
        self._t0 = time()

        self._running = False

    @property
    def rate(self):
        return self._rate

    @property
    def channels(self):
        return self._channels

    @property
    def callbacks(self):
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value):
        self._callbacks = value

    def on_audio(self, audio):
        self._queue.put(audio)

    def start(self):
        self._running = True
        self._t0 = time()

    def stop(self):
        self._running = False

    def _processor(self):
        while True:
            audio = self._queue.get()

            t1 = time()
            dt = (t1 - self._t0)
            self._dt_buffer.append(dt)

            if np.mean(self._dt_buffer) > self._dt_threshold_multiplier * (len(audio) / float(self.rate)):
                self._log.warning("<< Frames were skipped, Check Host/Pepper Network Connection/Load >>")
                self._dt_buffer.clear()

            self._t0 = t1

            for callback in self.callbacks:
                callback(audio)