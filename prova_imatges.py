"""
This program is based on this YouTube tutorial:
https://youtu.be/V62M9d8QkYM
A import is missing as a library appears to only be available in macOS (cringe), however the TTS can be implemented
without that library, it just makes it "cleaner" in theory.

Apart from that, while the plane will obviously not be talking about what it finds on-screen as this program does,
the TTS will still be useful for communications with the control tower, if that's a thing we end up doing.
"""

import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox

# We take the output from the camera at index 0. In my case it's OBS virtual cam as I don't have a webcam installed.
video = cv2.VideoCapture(0)

# Main loop, plays every frame:
while True:
    ret, frame = video.read()
    bbox, label, conf = cv.detect_common_objects(frame, model="yolov3-tiny", confidence=0)  # Try enabling GPU later
    output_image = draw_bbox(frame, bbox, label, conf)

    cv2.imshow("Object Detection", output_image)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break