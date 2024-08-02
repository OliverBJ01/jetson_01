#!/usr/bin/env python3

# basic GStreamer example   single pipelines to a) receive USB and IP Cams, b) transmit RTP stream
# pipelines
# Notes:
#   1. my Cam is YUYV but v4l2src requires YUY2
#   2. nvv4l2camerasrc only supports YUV capture in UYVY format.
#      ref https://docs.nvidia.com/jetson/archives/r35.4.1/DeveloperGuide/text/SD/Multimedia/AcceleratedGstreamer.html

# monitor for UDP with
#    tcpdump -i eth0 -n udp port 5000
# receive UDP on other PC with :
#    gst-launch-1.0 udpsrc port=5000 ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! Autovideosink

# ISSUE: HIGH LATENCY AT OTHER PC

import os
import gi

os.environ['GST_DEBUG'] = '3'

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
Gst.init("aa")

# cam_uri = 'rtsp://admin:roxywashere@10.1.1.80:554/h264Preview_01_main'

# receive RSTP stream from IP cam
pipeline = Gst.parse_launch(
    "rtspsrc location=rtsp://admin:roxywashere@10.1.1.80:554/h264Preview_01_sub ! rtpjitterbuffer ! "
    "application/x-rtp, media=video, encoding-name=H264 ! queue ! "
    "rtph264depay ! h264parse !   nvv4l2decoder ! nvvidconv !"
    "videoscale ! video/x-raw(memory:NVMM),width=640,height=480 ! "
    "nv3dsink sync=false")
    # "autovideosink sync=false")
    # "nvdrmvideosink sync=false")
    # "nveglgless?ink sync=false")

# receive raw video from USB cam and stream as RTP
# pipeline = Gst.parse_launch(
#     "v4l2src device=/dev/video0 ! "
#     "video/x-raw, width=640, height=480, format=(string)YUY2 ! "
#     "videoconvert ! video/x-raw, format=(string)I420 ! nvvidconv ! video/x-raw(memory:NVMM), format=(string)NV12 ! "
#     "nvv4l2h264enc ! rtph264pay mtu={mtu} ! udpsink host=10.1.1.48 port=5000".format(
#         width=320, height=240, framerate=15, mtu=1200    ))

# receive raw video from USB cam and display it
# pipeline = Gst.parse_launch(
#     "v4l2src device=/dev/video0 ! "
#      "video/x-raw, width=640, height=480, format=(string)YUY2 ! "
#       # " nvvideoconvert ! nv3dsink  ")
#      "xvimagesink ")

# pipeline = Gst.parse_launch(
#     ' v4l2src device=/dev/video0 !'
#     ' video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 !'
#     ' nvvideoconvert ! autovideosink' )

pipeline.set_state(Gst.State.PLAYING)
loop = GLib.MainLoop()
loop.run()



