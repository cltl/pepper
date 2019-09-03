from pepper.framework.abstract.tablet import AbstractTablet
from pepper import logger
import re


class NAOqiTablet(AbstractTablet):

    IMAGE_FORMATS = re.compile("\.(jpeg|jpg|png|gif|bmp)")

    def __init__(self, session):
        self._session = session
        self._service = self._session.service("ALTabletService")
        self._log = logger.getChild(self.__class__.__name__)

    def show(self, url):
        if url:
            try:
                if re.findall(self.IMAGE_FORMATS, url.lower()):
                    self._service.showImage(url)
                else:
                    self._service.showWebview(url)

                self._log.info("Show {}".format(url))
            except:
                self._log.warning("Couldn't Show {}".format(url))

    def hide(self):
        self._service.hide()
