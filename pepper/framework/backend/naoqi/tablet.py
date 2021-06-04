from pepper.framework.abstract.tablet import AbstractTablet
from pepper import logger

import qi

import re

from time import sleep


class NAOqiTablet(AbstractTablet):
    """Access Robot Tablet to show URLs"""

    IMAGE_FORMATS = re.compile("\.(jpeg|jpg|png|gif|bmp)")

    def __init__(self, session):
        # type: (qi.Session) -> None
        self._session = session
        self._service = self._session.service("ALTabletService")
        self._service.setOnTouchWebviewScaleFactor(1)
        self._log = logger.getChild(self.__class__.__name__)

        self.hide()


    def show(self, url):
        # type: (str) -> None
        """
        Show URL

        Parameters
        ----------
        url: str
            WebPage/Image URL
        """

        if url:
            try:
                if re.findall(self.IMAGE_FORMATS, url.lower()):
                    if not self._service.showImage(url):
                        raise RuntimeError()
                else:
                    if not self._service.showWebview(url):
                        raise RuntimeError()
                
                self._log.debug("Show {}".format(url))
            except Exception as e:
                self._log.warning("Couldn't Show {}".format(url, e))

    def hide(self):
        # type: () -> None
        """Hide whatever is shown on tablet"""
        self._service.hide()
