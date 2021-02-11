import base64
import json
import time

import websocket
from websocket import ABNF

try:
    import thread
except ImportError:
    import _thread as thread

URL = "ws://localhost:8008/"


def on_message(ws, message):
    print("on_message: " + message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    # with open("./sample_input.wav", 'rb') as input_file:
    #     ws.send(input_file.read(), websocket.ABNF.OPCODE_BINARY)

    def run(*args):
        # ws.send(bytearray([0]), ABNF.OPCODE_BINARY)
        for i in range(3):
            init_dict = {}
            init_dict['right_text'] = f'right_text_{i}'
            init_dict['session_id'] = f'session_id_{i}'
            init_dict['sequence_id'] = i

            ws.send(json.dumps(init_dict))

            for j in range(10):
                binary_data = f'Hello {j}'.encode('utf8')
                ws.send(binary_data, ABNF.OPCODE_BINARY)
                time.sleep(1)

            time.sleep(1)
        # ws.send(bytearray([1]), ABNF.OPCODE_BINARY)
        ws.close()
        print("thread terminating...")

    thread.start_new_thread(run, ())
    # print("### opened ###")


if __name__ == "__main__":
    websocket.enableTrace(True)

    credentials = b"username_1:test_password_1"
    encoded_credentials = base64.b64encode(credentials)
    print(encoded_credentials)
    encoded_credentials = encoded_credentials.decode("utf-8")
    print(encoded_credentials)

    ws = websocket.WebSocketApp(URL,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                header={"Authorization": f"Basic {encoded_credentials}"})
    ws.on_open = on_open
    ws.run_forever()
