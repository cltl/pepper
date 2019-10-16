import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template

import webbrowser

import os


class DisplayServer(tornado.web.Application):
    """Display Server for :class:`~pepper.framework.component.display.display.DisplayComponent`"""

    ROOT = os.path.join(os.path.dirname(__file__), "web")
    PORT = 9090
    HANDLERS = set()

    def __init__(self):

        # Host web/index.html
        class BaseHandler(tornado.web.RequestHandler):
            def get(self):
                loader = tornado.template.Loader(DisplayServer.ROOT)
                self.write(loader.load("index.html").generate())

        # Accept Web Socket Connections
        class WSHandler(tornado.websocket.WebSocketHandler):
            def __init__(self, application, request, **kwargs):
                super(WSHandler, self).__init__(application, request, **kwargs)

            def open(self):
                DisplayServer.HANDLERS.add(self)

            def on_close(self):
                DisplayServer.HANDLERS.remove(self)

        super(DisplayServer, self).__init__([(r'/ws', WSHandler), (r'/', BaseHandler)])

    def start(self):
        # type: () -> None
        """Start WebServer"""
        self.listen(self.PORT)
        webbrowser.open("http://localhost:{}".format(self.PORT))
        tornado.ioloop.IOLoop.instance().start()

    def update(self, json):
        # type: (str) -> None
        """Update WebServer"""
        if json:
            for handler in self.HANDLERS:
                handler.write_message(json)
