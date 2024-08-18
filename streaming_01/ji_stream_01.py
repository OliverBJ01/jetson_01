#!/usr/bin/env python3

# Jetson-Inference Package streaming
# Refer: Camera Streaming and Multimedia at https://github.com/dusty-nv/jetson-inference/blob/master/docs/aux-streaming.md#source-code

# This code is from video-viewer at https://github.com/dusty-nv/jetson-utils/blob/master/python/examples/video-viewer.py
# it uses videoSource and video

# NO DELAY AT ORIN DISPLAY OR REMOTE PC RTP DISPLAY

from jetson_utils import videoSource, videoOutput, Log

# create video sources & outputs: pass options dictionary to the videoSource/videoOutput initializer,
input = videoSource("/dev/video0", options={'width': 640, 'height': 480, 'framerate': 30})
# input = videoSource("/dev/video0", options={})
# input = videoSource("rtsp://admin:roxywashere@10.1.1.80:554/h264Preview_01_sub", options={})

# RTP Output
# output = videoOutput("my_video.mp4", options={'codec': 'h264', 'bitrate': 4000000})
output = videoOutput("rtp://10.1.1.48:5000", options={'codec': 'h2645', 'bitrate': 4000000})


# capture frames until EOS or user exits
numFrames = 0

while True:
    # capture the next image
    img = input.Capture()


    if img is None:  # timeout
        continue

    if numFrames % 25 == 0 or numFrames < 15:
        Log.Verbose(f"video-viewer:  captured {numFrames} frames ({img.width} x {img.height})")

    numFrames += 1

    # render the image
    output.Render(img)

    # update the title bar
    output.SetStatus("Video Viewer | {:d}x{:d} | {:.1f} FPS".format(img.width, img.height, output.GetFrameRate()))

    # exit on input/output EOS
    if not input.IsStreaming() or not output.IsStreaming():
        break