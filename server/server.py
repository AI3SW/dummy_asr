import _thread as thread
import json
import logging
import os
import random
import string
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import click
import tornado.ioloop
import tornado.websocket

os.makedirs('./logs', exist_ok=True)

logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s : %(message)s',
                    level=logging.INFO,
                    handlers=[
                        TimedRotatingFileHandler("logs/log.txt",
                                                 when='D', backupCount=30),
                        logging.StreamHandler()
                    ])

sockets = []
_socket_index = 0


def get_sock_index():
    global _socket_index

    sock_index = _socket_index
    _socket_index = _socket_index + 1
    return sock_index


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        logging.info("WebSocket opened")

    def on_message(self, message):
        logging.info("on_message: message length %s" % len(message))
        utc_now = datetime.utcnow().isoformat()
        logging.info("Sending %s ..." % utc_now)
        self.write_message(utc_now)

    def on_close(self):
        logging.info("WebSocket closed")


class DummyASRWebSocket(tornado.websocket.WebSocketHandler):
    SLEEP_INTERVAL = 3
    PARTIAL_INTERVAL = 3

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

        self.start_transmission = False
        self.utt_id = 0

    def open(self):
        sockets.append(self)
        self.sock_index = get_sock_index()
        logging.info("[Sock %s] DummyASRWebSocket opened" % self.sock_index)

    def on_message(self, message):

        def run(*args):
            logging.info("[Sock %s] Starting transmission for utt_id %s"
                         % (self.sock_index, self.utt_id))

            for i in range(self.PARTIAL_INTERVAL):
                response = {}
                response['uttID'] = self.utt_id

                # return random combination of strings and digits
                # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
                random_str = ''.join(random.choices(string.ascii_uppercase
                                                    + string.digits, k=3))
                response['result'] = f"{self.utt_id}_{i}_{random_str}"

                if i == self.PARTIAL_INTERVAL - 1:
                    response['cmd'] = 'asrfull'
                    self.start_transmission = False
                    self.utt_id = self.utt_id + 1
                else:
                    response['cmd'] = 'asrpartial'

                try:
                    self.write_message(response)
                    logging.info("[Sock %s] Sent result: %s" %
                                 (self.sock_index, response))
                    time.sleep(self.SLEEP_INTERVAL)
                except tornado.websocket.WebSocketClosedError as e:
                    logging.error(
                        "[Sock %s] Websocket already closed." % self.sock_index)

        logging.info("[Sock %s] Message received: %s" %
                     (self.sock_index, message))

        # following protocol of ASR engine
        # 1 byte value of '0' indicates start of stream
        # 1 byte value of '1' indicates end of stream
        if isinstance(message, bytes) and len(message) == 1:
            if message[0] == 0:
                logging.info('[Sock %s] Start stream' % self.sock_index)
                self.start_transmission = True
            if message[0] == 1:
                logging.info('[Sock %s] Ending stream' % self.sock_index)
                self.close()
                # self.close does not call on_close callback
                self.on_close()

        elif self.start_transmission:
            self.start_transmission = False
            thread.start_new_thread(run, ())

    def on_close(self):
        sockets.remove(self)
        logging.info("[Sock %s] Removed sock %s from socket list" %
                     (self.sock_index, self.sock_index))
        logging.info("[Sock %s] DummyASRWebSocket closed" % self.sock_index)


def make_app():
    return tornado.web.Application([
        (r"/", DummyASRWebSocket),
        (r"/echo", EchoWebSocket)
    ])


@click.command()
@click.option('--port', '-p', default=5000)
def main(port: int):
    # reference: https://gist.github.com/timsavage/d412d9e321e9f6d358abb335c8d41c63
    app = make_app()
    app.listen(port)

    logging.info("Starting websocket server on port %s" % port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
