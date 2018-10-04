import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template

from PIL import Image
import webbrowser

from io import BytesIO
import base64
import os

import logging


class VideoFeedApplication(tornado.web.Application):

    HANDLERS = set()
    PORT = 9090

    def __init__(self):

        self._log = logging.getLogger(self.__class__.__name__)

        class BaseHandler(tornado.web.RequestHandler):
            def get(self):
                loader = tornado.template.Loader(os.path.dirname(__file__))
                self.write(loader.load("index.html").generate())

        class WSHandler(tornado.websocket.WebSocketHandler):
            def __init__(self, application, request, **kwargs):
                super(WSHandler, self).__init__(application, request, **kwargs)

            def open(self):
                VideoFeedApplication.HANDLERS.add(self)

            def on_close(self):
                VideoFeedApplication.HANDLERS.remove(self)

        super(VideoFeedApplication, self).__init__([(r'/ws', WSHandler), (r'/', BaseHandler)])

    def start(self):
        self.listen(self.PORT)
        webbrowser.open("http://localhost:{}".format(self.PORT))
        self._log.info("Booted")

        tornado.ioloop.IOLoop.instance().start()

    def update(self, image):
        """
        Parameters
        ----------
        image: Image.Image
        """
        for handler in self.HANDLERS:
            handler.write_message(self.encode_image(image))

    @staticmethod
    def encode_image(image):
        """
        Parameters
        ----------
        image: Image.Image

        Returns
        -------
        base64: str
            Base64 encoded PNG string
        """
        with BytesIO() as png:
            image.save(png, 'png')
            png.seek(0)
            return base64.b64encode(png.read())
