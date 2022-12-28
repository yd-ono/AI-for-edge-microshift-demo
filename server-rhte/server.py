#!/usr/bin/python3
from flask import Flask
from flask import render_template
from flask import request
from flask import Response
import logging
import threading
import time
import cv2
import os
import time

from faces import *
# from mjpeg_streamer import MjpegReader

# frame to be shared via mjpeg server out
output_frame = None
lock = threading.Lock()

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

cap = cv2.VideoCapture(int(os.environ.get('VIDEO_DEVICE_ID', 0)))

if not (cap.isOpened()):
    app.logger.critical("Could not open video device")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, os.environ.get('CAP_PROP_FRAME_WIDTH', 1920))
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, os.environ.get('CAP_PROP_FRAME_HEIGHT', 1080))

@app.route('/healthz')
def healthz():
    """
    Check the health of this peakweb instance. OCP will hit this endpoint to verify the readiness
    of the peakweb pod.
    """
    return 'OK'

@app.route('/')
def index():
    app.logger.info("Start thread...")
    threading.Thread(target=streamer_thread, name=None, args=[os.environ.get('VIDEO_DEVICE_ID', '0')]).start()
    return render_template('index.html')

def streamer_thread(device_id):

    app.logger.info("starting streamer /dev/video%s", device_id)

    while(True):
        ret, frame = cap.read()

        if not ret:
            app.logger.info("Can't receive frame (stream end?). Exiting ...")
            time.sleep(3)
            break

        app.logger.info("TYPE: %s",type(frame))
        if frame is not None:
            process_streamer_frame(frame)

        time.sleep(3)

def process_streamer_frame(frame):
    global output_frame, lock
    frame_out = find_and_mark_faces(frame, app.logger)
    with lock:
        output_frame = frame_out.copy()


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate_video_feed(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


def generate_video_feed():
    # grab global references to the output frame and lock variables
    global output_frame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop

            if output_frame is None:
                time.sleep(0.01)
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)

            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'

        time.sleep(0.1)

