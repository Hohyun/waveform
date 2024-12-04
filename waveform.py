import wave
import os
import math
import json
import datetime
import numpy
import hashlib
import requests
import traceback
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from pydub import AudioSegment


def get_waveform(url):
    try:
        try:
            resp = requests.get(url)
            if not resp.ok:
                return None
            data = resp.content
        except Exception:
            return None

        try:
            filepath = hashlib.md5(str(datetime.datetime.now())).hexdigest() + '.mp3'
            f = open(filepath, 'w')
            f.write(data)
            f.close()
        except IOError:
            return None

        wf_filepath = hashlib.md5(str(datetime.datetime.now())).hexdigest() + '.wav'
        BIN_COUNT = 30000
        FRAME_RATE = 8000
        audio = AudioSegment.from_mp3(filepath)
        audio.set_frame_rate(FRAME_RATE)
        audio.set_channels(1)
        audio.export(wf_filepath, format='wav')
        spf = wave.open(wf_filepath, 'r')
        signal = spf.readframes(-1)
        signal = numpy.fromstring(signal, 'Int16')
        signal_len = len(signal)
        data = [0,] * BIN_COUNT

        count = 0
        agg_val = 0
        prev_idx = 0
        max_val = -1
        for idx, val in enumerate(signal):
            i = math.floor(idx * BIN_COUNT / signal_len)
            if prev_idx != i:
                mean = agg_val / count
                data[int(i - 1)] = mean
                agg_val = 0
                count = 0

                if mean > max_val:
                    max_val = mean

            agg_val += math.fabs(val)
            count += 1
            prev_idx = i

        for idx, val in enumerate(data):
            data[idx] = int(round(val * 100 / max_val))

        try:
            os.remove(filepath)
            os.remove(wf_filepath)
        except (OSError, IOError):
            pass

        return json.dumps(data)
    except Exception:
        traceback.print_exc()
        try:
            os.remove(filepath)
            os.remove(wf_filepath)
        except Exception:
            pass
        return None


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        waveform = get_waveform(self.get_argument('url'))
        if waveform is not None:
            self.set_header('Content-Type', 'application/javascript')
            self.write('abc(' + waveform + ')')
        else:
            self.write('Failed')


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
