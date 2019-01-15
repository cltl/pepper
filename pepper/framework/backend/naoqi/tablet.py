import re


class NaoqiTablet(object):

    IMAGE_FORMATS = re.compile("\.(jpeg|jpg|png|gif|bmp)")

    def __init__(self, session):
        self._session = session
        self._service = self._session.service("ALTabletService")

    def show(self, url):
        if url:
            if re.findall(self.IMAGE_FORMATS, url.lower()):
                self._service.showImage(url)
            else:
                self._service.showWebview(url)

    def hide(self):
        self._service.hide()
