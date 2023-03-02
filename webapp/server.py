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
# WEB_LOGLEVEL=['INFO','DEBUG']..
app.logger.setLevel(level=os.environ.get('WEB_LOGLEVEL', 'INFO').upper())

load_known_faces(os.environ.get('MODEL_FILENAME', 'model.data'),app.logger)

# v4l2-ctl --list-devices
# v4l2-ctl -d /dev/video0 --list-formats-ext
cap = cv2.VideoCapture(int(os.environ.get('VIDEO_DEVICE_ID', 0)),cv2.CAP_V4L2)
video_fps = cap.get(cv2.CAP_PROP_FPS)
app.logger.info("FPS of the Videosource: %d",video_fps)
processing_fps = int(os.environ.get('VIDEO_PROCESSING_FPS', 1))

if video_fps > processing_fps:
    skip_rate = round(video_fps/processing_fps)
else:
    skip_rate = 1

app.logger.info("Caluclated skip rate based on VIDEO_PROCESSING_FPS:%d : %d",processing_fps,skip_rate)

if not (cap.isOpened()):
    app.logger.critical("Could not open video device")
    exit(1)


# MJPG: gets alot Corrupt JPEG data: 1060 extraneous bytes before marker 0xd9
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, os.environ.get('CAP_PROP_FRAME_WIDTH', 1280))
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, os.environ.get('CAP_PROP_FRAME_HEIGHT', 720))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, os.environ.get('CAP_PROP_FRAME_WIDTH', 800))
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, os.environ.get('CAP_PROP_FRAME_HEIGHT', 600))

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

    frame_no = 0  # Local variable to keep track of video frame number

    while(True):
        ret = cap.grab()
        if not ret:
            app.logger.info("Can't receive frame (stream end?). Exiting ...")
            time.sleep(3)
            break

        frame_no += 1
        if (frame_no % skip_rate == 0):  # Processing frame
            status, frame = cap.retrieve()

            if frame is not None:
                process_streamer_frame(frame)

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

