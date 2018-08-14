from contextlib import contextmanager
from threading import Thread

import socket
import subprocess
import logging
import os

from time import sleep

class NER(object):

    ROOT = os.path.join(os.path.dirname(__file__), 'stanford-ner')
    PORT = 9199
    ADDRESS = ('localhost', PORT)

    def __init__(self, classifier = 'english.all.3class.distsim.crf.ser'):
        self._log = logging.getLogger(self.__class__.__name__)

        self._ner_server_thread = Thread(target=self._start_server, args=(classifier,))
        self._ner_server_thread.daemon = True
        self._ner_server_thread.start()

    def tag(self, text):
        with self._connect() as s:
            s.send((text.strip() + '\n').encode('utf-8'))
            return [
                tuple(s.rsplit('/', 1))
                for s in self._recv_all(s).replace('\n', '').strip().split(' ')
                if len(s.rsplit('/', 1)) == 2
            ]

    def _start_server(self, classifier):
        subprocess.call([
            'java', '-cp', os.path.join(NER.ROOT, 'stanford-ner.jar'), 'edu.stanford.nlp.ie.NERServer',
            '-port', str(NER.PORT), '-loadClassifier', os.path.join(NER.ROOT, classifier)])

    @contextmanager
    def _connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(NER.ADDRESS)
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
