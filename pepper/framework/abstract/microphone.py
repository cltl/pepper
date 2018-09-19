import numpy as np

from threading import Thread
from Queue import Queue
from time import time

from collections import deque

import logging


class AbstractMicrophone(object):
    def __init__(self, rate, channels, callbacks):
        """
        Abstract Microphone

        Parameters
        ----------
        rate: int
        channels: int
        callbacks: list of callable
        """
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
        self._blocks = 0

    @property
    def rate(self):
        """
        Returns
        -------
        rate: int
            Audio bit rate
        """
        return self._rate

    @property
    def channels(self):
        """
        Returns
        -------
        channels: int
            Audio channels
        """
        return self._channels

    @property
    def callbacks(self):
        """
        Returns
        -------
        callbacks: list of callable
        """
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value):
        """
        Parameters
        ----------
        value: list of callable
        """
        self._callbacks = value

    def on_audio(self, audio):
        """
        On Audio Event

        Parameters
        ----------
        audio: np.ndarray
        """
        self._queue.put(audio)

    def start(self):
        """Start Microphone Stream"""

        self._blocks = max(0, self._blocks - 1)
        if self._blocks == 0:
            self._running = True
            self._t0 = time()

    def stop(self):
        """Stop Microphone Stream"""

        self._blocks += 1
        self._running = False

    def _processor(self):
        """
        Audio Processor

        Calls each callback for each audio frame, threaded, for higher audio throughput
        """
        while True:
            audio = self._queue.get()

            t1 = time()
            dt = (t1 - self._t0)
            self._dt_buffer.append(dt)

            if len(self._dt_buffer) == self._dt_buffer.maxlen and \
                    np.mean(self._dt_buffer) > self._dt_threshold_multiplier * (len(audio) / float(self.rate)):
                self._log.warning("<< Frames were skipped, Check Host/Pepper Network Connection/Load >>")
                self._dt_buffer.clear()

            self._t0 = t1

            if self._running:
                for callback in self.callbacks:
                    callback(audio)