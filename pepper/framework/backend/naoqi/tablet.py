from threading import Timer


class NaoqiTablet(object):
    def __init__(self, session):
        self._session = session
        self._service = self._session.service("ALTabletService")

    def show(self, url, timeout=None):
        self._service.showImage(url)
        if timeout:
            Timer(timeout, self.hide)

    def hide(self):
        self._service.hideImage()
