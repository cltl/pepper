from pepper.framework.system import SystemCamera
from pepper.framework import CameraResolution

from pepper.util.image import ImageAnnotator

from PIL import Image
from io import BytesIO
import base64

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template

import webbrowser


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader(".")
        self.write(loader.load("index.html").generate())


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'connection opened...'

        self._annotator = ImageAnnotator()

        self._camera = SystemCamera(CameraResolution.QVGA, 5, [self.on_frame])
        self._camera.start()

    def on_message(self, message):
        print 'received:', message

    def on_close(self):
        print 'connection closed...'

    def on_frame(self, image):

        image = Image.fromarray(image)
        image = self._annotator.annotate(image)
        image = self.encode_image(image)

        self.write_message(image)

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


if __name__ == "__main__":

    PORT = 9090

    application = tornado.web.Application([
        (r'/ws', WSHandler),
        (r'/', MainHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./resources"}),
    ])

    application.listen(PORT)
    webbrowser.open("localhost:{}".format(PORT))
    tornado.ioloop.IOLoop.instance().start()
