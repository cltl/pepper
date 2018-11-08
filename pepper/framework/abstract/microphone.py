from pepper import logger

import numpy as np

from threading import Thread
from Queue import Queue
from time import time

from collections import deque


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

        self._dt_threshold_multiplier = 1.5
        self._dt_buffer = deque([], maxlen=32)
        self._true_rate = rate
        self._t0 = time()

        self._queue = Queue()
        self._processor_thread = Thread(name="MicrophoneThread", target=self._processor)
        self._processor_thread.daemon = True
        self._processor_thread.start()

        self._log = logger.getChild(self.__class__.__name__)

        self._running = False

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
    def true_rate(self):
        """
        Returns
        -------
        true_rate:
            Actual Audio bit rate
        """
        return self._true_rate

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

    @property
    def running(self):
        """
        Returns
        -------
        running: bool
        """
        return self._running

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
        self._running = True

    def stop(self):
        """Stop Microphone Stream"""
        self._running = False

    def _processor(self):
        """
        Audio Processor

        Calls each callback for each audio frame, threaded, for higher audio throughput
        """
        while True:
            audio = self._queue.get()
            if self._running:
                for callback in self.callbacks:
                    callback(audio)
            self._update_dt(len(audio))

    def _update_dt(self, n_bytes):
        t1 = time()
        self._dt_buffer.append((t1 - self._t0))
        self._t0 = t1
        self._true_rate = n_bytes / np.mean(self._dt_buffer)
