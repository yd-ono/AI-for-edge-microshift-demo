#!/usr/bin/python3
from flask import Flask
from flask import request
from flask import Response
import logging
import threading
import time
import cv2

# frame to be shared via mjpeg server out
outputFrames = {}
lock = threading.Lock()

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

cap = cv2.VideoCapture(4)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

@app.route("/")
def hello_world():
    threading.Thread(target=streamer_thread, name=None, args=['4']).start()

    return "<p>Hello, World!</p><a href='/video_feed'>Link</a>"

def streamer_thread(device_id):

    app.logger.info("starting streamer /dev/video%s", device_id)

    while(True):
        ret, frame = cap.read()
        process_streamer_frame(frame,device_id)


def process_streamer_frame(frame,device_id):
    global outputFrames, lock
    #frame_out = find_and_mark_faces(frame, app.logger, cam_ip)
    with lock:
        outputFrames[device_id] = frame.copy()


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate_video_feed(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


def generate_video_feed():
    # grab global references to the output frame and lock variables
    global outputFrames, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if not outputFrames:
                time.sleep(0.01)
                continue

            # encode the frame in JPEG format

            frames = []
            for camIP, frame in sorted(outputFrames.items()):
                frames.append(frame)

            all_cams = cv2.hconcat(frames)

            (flag, encodedImage) = cv2.imencode(".jpg", all_cams)

            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'

        time.sleep(0.1)
