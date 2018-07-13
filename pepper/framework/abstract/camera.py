from Queue import Queue
from threading import Thread


class AbstractCamera(object):
    def __init__(self, resolution, rate, callbacks):
        self._resolution = resolution
        self._rate = rate
        self._callbacks = callbacks

        self._queue = Queue()
        self._processor_thread = Thread(target=self._processor)
        self._processor_thread.daemon = True
        self._processor_thread.start()

        self._running = False

    @property
    def resolution(self):
        return self._resolution

    @property
    def width(self):
        return self._resolution.value[1]

    @property
    def height(self):
        return self._resolution.value[0]

    @property
    def channels(self):
        return 3

    @property
    def rate(self):
        return self._rate

    @property
    def callbacks(self):
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value):
        self._callbacks = value

    def on_image(self, image):
        self._queue.put(image)

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def _processor(self):
        while True:
            image = self._queue.get()
            for callback in self.callbacks:
                callback(image)