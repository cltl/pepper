from contextlib import contextmanager, closing
from threading import Thread

import socket
import subprocess
import logging
import os

from time import sleep


class NER(object):

    ROOT = os.path.join(os.path.dirname(__file__), 'stanford-ner')
    IP = 'localhost'

    def __init__(self, classifier = 'english.all.3class.distsim.crf.ser'):
        self._log = logging.getLogger(self.__class__.__name__)
        self._port = self._find_free_port()

        self._ner_server_process = None

        self._ner_server_thread = Thread(target=self._start_server, args=(classifier,))
        self._ner_server_thread.daemon = True
        self._ner_server_thread.start()

        self._log.debug("Booted: ({}:{})".format(self.IP, self._port))

    def tag(self, text):
        with self._connect() as s:
            s.send((text.strip() + '\n').encode('utf-8'))
            return [
                tuple(s.rsplit('/', 1))
                for s in self._recv_all(s).replace('\n', '').strip().split(' ')
                if len(s.rsplit('/', 1)) == 2
            ]

    def close(self):
        self._ner_server_process.kill()

    def _start_server(self, classifier):
        self._ner_server_process = subprocess.Popen([
            'java', '-cp', os.path.join(NER.ROOT, 'stanford-ner.jar'), 'edu.stanford.nlp.ie.NERServer',
            '-port', str(self._port), '-loadClassifier', os.path.join(NER.ROOT, classifier)])

    def _find_free_port(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    @contextmanager
    def _connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            while sock.connect_ex(('localhost', self._port)):
                sleep(0.1)
            yield sock
        finally:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except Exception as e:
                pass
            finally:
                sock.close()

    def _recv_all(self, socket):
        buffer = bytearray()

        while True:
            data = socket.recv(4096)
            if not data: break
            buffer.extend(data)

        return buffer.decode('utf-8')

    def __del__(self):
        self.close()


if __name__ == '__main__':
    ner = NER()
    ner.tag("Marie, how'd you like an ice cream?")
