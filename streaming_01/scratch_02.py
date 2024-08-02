# gstreamer_03 sends camera stream to: image processing function and then to display

#!/usr/bin/env python3

#Notes:
# My USB Canm is [0] 'YUYV' (YUYV 4:2:2)
#                 [1] 'MJPG' (Motion-JPEG, compressed)

# to be tuned by reducing the buffer numbers


import sys
import os
import cv2
import logging
import traceback
import gi
import numpy as np

os.environ['GST_DEBUG'] = '4'

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(sys.argv)

# configure logging
#use `logging.info("My message")`, `logging.error("My error message")` etc for logging.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#bus callback function
def on_bus_message(bus, message):
    t = message.type
    if t == Gst.MessageType.EOS:
        loop.quit()
        logging.info("EOS message received, quitting")
    elif t == Gst.MessageType.ERROR:
        err, debug_info = message.parse_error()
        logging.error(f"Error: {err} \n Debug Info: {debug_info}")
        loop.quit()

def on_new_sample(appsink):
    sample = appsink.emit('pull-sample')    # Get GstSample from appsink's "pull-sample" method
    buf = sample.get_buffer()               # Get GstBuffer from GstSample
    caps = sample.get_caps()
    logging.info(caps.to_string())
# STUB - DO INFERENCE HERE
    appsrc.emit('push-buffer', buf)         # Send GstBuffer to appsrc
    return Gst.FlowReturn.OK

# Create GStreamer pipeline
pipeline = Gst.parse_launch(
    ' v4l2src device=/dev/video0 num-buffers=500 io-mode=4 !'  # num-buffers=50 was empty, io-mode 4 (DMABUF)
    ' video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 !'
    ' queue ! nvvideoconvert ! appsink name=my_appsink '
    ' appsrc name=my_src ! tee name=t'
    ' t. ! queue ! videoconvert ! autovideosink '
    ' t. ! queue ! nvvideoconvert ! nvv4l2h264enc control-rate=1 bitrate=8000000 maxperf-enable=1 ! '
    ' h264parse ! rtph264pay pt=96 config-interval=1 ! '
    ' udpsink host=10.1.1.48 port=5000 sync=false async=false'
)

# Set appsink properties
appsink = pipeline.get_by_name("my_appsink")    # Get appsink from pipeline
appsink.set_property("emit-signals", True)
appsink.set_property("max-buffers", 50) # from 20 to 50 buffers in appsink queue
appsink.set_property('drop', True)  #  If the buffer fills up, start dropping old frames
appsink.connect('new-sample', on_new_sample)

# Set appsource properties; set the cap of appsrc to match the buffer being pushed:
appsrc = pipeline.get_by_name('my_src')

appsrc.set_property('caps', Gst.Caps.from_string('video/x-raw,format=YUY2,width=640,height=480,framerate=30/1'))
# appsrc.set_property('caps', Gst.Caps.from_string('video/x-raw,format=(string)RGB,width=640,height=480'))
# appsrc.set_property('caps', Gst.Caps.from_string('video/x-raw,format=GRAY8,width=640,height=480'))  #greyscale

# Start playing pipeline
ret = pipeline.set_state(Gst.State.PLAYING)
if ret == Gst.StateChangeReturn.FAILURE:
    logging.error("Error starting the pipeline")
    exit(-1)
logging.info("started pipeline")

# Get pipeline's bus and listen for EOS and ERROR messages
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message", on_bus_message)
logging.info("connected bus")

loop = GLib.MainLoop()
logging.info("created loop")
try:

    loop.run()
    logging.info("created loop")
    loop.run()
except Exception as e:
    logging.error(f"An error occurred: {e}")
    traceback.print_exc()
finally:
    pipeline.set_state(Gst.State.NULL)
























