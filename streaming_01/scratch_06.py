#!/usr/bin/env python3

#  gstream_02.py = scratch_06.py

# USB cam streamed to inference stub then to display and stream out as RTP
#   pipeline_in from USB camera to appsink (inference stub)
#   output_out_vid displays
#   pipeline_out_rtp streams via rtp

# Notes: USB Cam is [0] 'YUYV' (YUYV 4:2:2)

import sys
import os
os.environ['GST_DEBUG'] = '*:6'
# os.environ['GST_DEBUG_FILE'] = '/home/bernard/Projects/gst_logfile.txt'
os.environ['GST_DEBUG_DUMP_DOT_DIR'] = "/home/bernard/Projects/dot_files"
import logging
import traceback
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
Gst.init(None)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def on_bus_message(bus, message):
    t = message.type
    if t == Gst.MessageType.EOS:
        loop.quit()
        logging.info("EOS message received, quitting")
    elif t == Gst.MessageType.ERROR:
        err, debug_info = message.parse_error()
        logging.error(f"BUS ERROR Error: {err} \n Debug Info: {debug_info}")
        loop.quit()

# def on_new_sample(appsink):
#     sample = appsink.emit('pull-sample')
#     buf = sample.get_buffer()
#     if buf is None:
#         print("Buffer is None")
#         return Gst.FlowReturn.ERROR
#     else:
#         print(f"Buffer size: {buf.get_size()}")
#
#     ret = appsrc.emit('push-buffer', buf)
#     if ret != Gst.FlowReturn.OK:
#         print("Error pushing buffer to appsrc")
#         return ret
#
#     print("Buffer successfully pushed to appsrc")
#     return Gst.FlowReturn.OK

def on_new_sample(appsink):
    # print("Getting new sample...")
    sample = appsink.emit('pull-sample')
    if sample is None:
        # print("Sample is None")
        return Gst.FlowReturn.ERROR
    buf = sample.get_buffer()
    if buf is None:
        print("Buffer is None")
        return Gst.FlowReturn.ERROR
    else:
        # print(f"Buffer size: {buf.get_size()}")
        pass

#  STUB   DO INFERENCE HERE

    # push buffer to appsrc_vid for display
    ret = appsrc_vid.emit('push-buffer', buf)
    if ret != Gst.FlowReturn.OK:
        print(f"Error pushing buffer to appsrc_vid. Error: {ret}")
        return ret
    # print("Buffer successfully pushed to appsrc_vid")

    # push buffer to RTP appsrc_rtp
    ret = appsrc_rtp.emit('push-buffer', buf.copy())
    if ret != Gst.FlowReturn.OK:
        print(f"Error pushing buffer to RTP appsrc_rtp. Error: {ret}")
        return ret

    return Gst.FlowReturn.OK

# create the pipelines

# pipeline_in = Gst.parse_launch(
#    'v4l2src device=/dev/video0 ! '
#    'video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! '
#    'queue ! nvvideoconvert ! '
#    'appsink name=my_sink')


# receive RSTP stream from IP cam
pipeline = Gst.parse_launch(
    "rtspsrc location=rtsp://admin:roxywashere@10.1.1.80:554/h264Preview_01_sub ! rtpjitterbuffer ! "
    "application/x-rtp, media=video, encoding-name=H264 ! queue ! "
    "rtph264depay ! h264parse !   nvv4l2decoder ! nvvidconv !"
    "videoscale ! video/x-raw(memory:NVMM),width=640,height=480 !"
    'appsink name=my_sink')
    # "nv3dsink sync=false")




pipeline_out_vid = Gst.parse_launch(
    'appsrc name=src_vid  is-live=true   caps=video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! '
    'autovideosink')
#dummy
# pipeline_out_rtp = Gst.parse_launch(
#     'appsrc name=src_rtp  is-live=true   caps=video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! '
#     'autovideosink' )

try:
    pipeline_out_rtp = Gst.parse_launch(
         'appsrc name=src_rtp caps=video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 !'
         'queue ! nvvideoconvert ! nvv4l2h264enc control-rate=1 bitrate=8000000 maxperf-enable=1 ! '
         'queue ! h264parse ! rtph264pay pt=96 config-interval=1 ! '
         'udpsink host=10.1.1.48 port=5000 sync=false async=false')
except GLib.Error as e:
    logging.error(f"Unable to create input pipeline: {e.message}")
    sys.exit(1)

# create the sink / sources
appsink = pipeline_in.get_by_name("my_sink")        # Get name from pipeline
appsrc_vid = pipeline_out_vid.get_by_name("src_vid")
appsrc_rtp = pipeline_out_rtp.get_by_name("src_rtp")

# set appsink pipeline properties
appsink.set_property('emit-signals', True)
appsink.set_property('sync', False)
# appsink.set_property("max-buffers", 50)           # from 20 to 50 buffers in appsink queue
appsink.set_property('drop', True)                  # If the buffer fills up, start dropping old frames
appsink.connect('new-sample', on_new_sample)        # Register handler to the "new-sample" signal

# assign a bus to the RTP pipeline for debugging
bus = pipeline_out_rtp.get_bus()
bus.add_signal_watch()
bus.connect("message", on_bus_message)

# Start the pipelines
ret = pipeline_in.set_state(Gst.State.PLAYING)
# Gst.debug_bin_to_dot_file(pipeline_in, Gst.DebugGraphDetails.ALL, "pipeline_in_playing")
if ret == Gst.StateChangeReturn.FAILURE:
    logging.error("Error starting the input pipeline")
    exit(-1)
else:
    logging.info("Input pipeline started")

ret = pipeline_out_vid.set_state(Gst.State.PLAYING)
# Dump dot file. This will create a .dot file under the directory you set, you can view this file with software
# # such as xdot or convert it to a PNG image by dot -Tpng -oimage.png pipeline.dot.
# Gst.debug_bin_to_dot_file(pipeline_out_vid, Gst.DebugGraphDetails.ALL, "pipeline_out_vid_playing")
if ret == Gst.StateChangeReturn.FAILURE:
    logging.error("Error starting pipeline_out_vid")
    exit(-1)
else:
    logging.info("pipeline_out_vid started")

ret = pipeline_out_rtp.set_state(Gst.State.PLAYING)
Gst.debug_bin_to_dot_file(pipeline_out_rtp, Gst.DebugGraphDetails.ALL, "pipeline_out_rtp_playing")
if ret == Gst.StateChangeReturn.FAILURE:
    logging.error("Error starting pipeline_out_rtp pipeline")
    exit(-1)
else:
    logging.info("pipeline_out_rtp started")

loop = GLib.MainLoop()
logging.info("created loop")

try:
    loop.run()
except KeyboardInterrupt:
    logging.info("Interrupted by user")
except Exception as e:
    logging.error(f"An error occurred: {e}")
    traceback.print_exc()
finally:
    pipeline_in.set_state(Gst.State.NULL)
    print(f"from finally")
    pipeline_out_vid.set_state(Gst.State.NULL)
    pipeline_out_rtp.set_state(Gst.State.NULL)

# use GST_DEBUG=nvv4l2h264enc:5,udpsink:5 to only enable debug logs for the nvv4l2h264enc and udpsink elements.