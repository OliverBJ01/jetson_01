import sys
import os
import cv2
import logging
import traceback
import gi
import numpy as np
import time
import threading

os.environ['GST_DEBUG'] = '4'

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(sys.argv)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def on_bus_message(bus, message):
    t = message.type
    if t == Gst.MessageType.EOS:
        loop.quit()
        logging.info("EOS message received, quitting")
    elif t == Gst.MessageType.ERROR:
        err, debug_info = message.parse_error()
        logging.error(f"Error: {err} \n Debug Info: {debug_info}")
        loop.quit()

# def on_new_sample(appsink):
#     sample = appsink.emit('pull-sample')
#     buf = sample.get_buffer()
#     # caps = sample.get_caps()
#     # logging.info(caps.to_string())
# #do Inference
#     appsrc.emit('push-buffer', buf)
#     return Gst.FlowReturn.OK

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
    # Fill a numpy array with YUY2 data
    data = np.full((480, 640, 2), [66, 40], dtype=np.uint8)
    data[::2, ::2, 1] = 105  # Set V0 values
    data[1::2, ::2, 1] = 80  # Set U0 values

    # Create a GstMemory block from the numpy array
    mem = Gst.Memory.new_wrapped(0, data.tobytes(), len(data.tobytes()), 0, None, None)

    # Create a new Gst.Buffer and add memory
    buf = Gst.Buffer.new()
    buf.insert_memory(-1, mem)

    # Set timestamp and duration
    buf.pts = Gst.util_uint64_scale(appsrc.get_property('format'),
                                    appsrc.get_property('n-buffers') * appsrc.get_property('blocksize'), Gst.SECOND)
    buf.duration = Gst.util_uint64_scale(appsrc.get_property('format'), appsrc.get_property('blocksize'), Gst.SECOND)

    # Push the buffer
    appsrc.emit('push-buffer', buf)

    return Gst.FlowReturn.OK

# try:
#     # Create GStreamer pipeline for capturing and processing data
#     pipeline_in = Gst.parse_launch(
#     'v4l2src device=/dev/video0 ! '
#     'video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! '
#     'queue ! nvvideoconvert ! '
#     'appsink name=my_sink'
#     # 'nvvideoconvert ! autovideosink'
#     )
#
#     # Create GStreamer pipeline for displaying processed video
#     pipeline_out = Gst.parse_launch(
#     'appsrc name=my_src is-live=true '
#     'format=time caps=video/x-raw,format=YUY2,'
#     'width=640,height=480,framerate=30/1 ! '
#     'autovideosink'
#     )
# except GLib.GError as e:
#     logging.error("Failed to create pipeline: %s" % str(e))
#     sys.exit(1)

# pipeline_out = Gst.parse_launch(
#     'appsrc name=my_src is-live=true format=time caps=video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! '
#     'videoconvert !  autovideosink'
# )
pipeline_out = Gst.parse_launch(
    'appsrc name=my_src is-live=true format=GST_FORMAT_TIME caps=video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! '
    'autovideosink'
)
# create the pipeline elements
# appsink = pipeline_in.get_by_name("my_sink")
appsrc = pipeline_out.get_by_name("my_src")

# connect signal
# appsink.connect("new-sample", on_new_sample)

# play pipelines
# ret = pipeline_in.set_state(Gst.State.PLAYING)
# if ret == Gst.StateChangeReturn.FAILURE:
#     logging.error("Error starting the input pipeline")
#     exit(-1)
# else:
#     logging.info("Input pipeline started")

ret = pipeline_out.set_state(Gst.State.PLAYING)
if ret == Gst.StateChangeReturn.FAILURE:
    logging.error("Error starting the output pipeline")
    exit(-1)
else:
    logging.info("Output pipeline started")

logging.info("started pipeline")

# bus_in = pipeline_in.get_bus()
# bus_in.add_signal_watch()
# bus_in.connect("message", on_bus_message)
# logging.info("connected bus")

loop = GLib.MainLoop()
logging.info("created loop")

# Start a new thread running the MainLoop
threading.Thread(target=loop.run).start()

try:
    while True:
        on_new_sample(None)
        time.sleep(1 / 30)  # control the framerate
except KeyboardInterrupt:
    logging.info("Interrupted by user")
except Exception as e:
    logging.error(f"An error occurred: {e}")
    traceback.print_exc()
finally:
    # pipeline_in.set_state(Gst.State.NULL)
    print(f"from finally")
    pipeline_out.set_state(Gst.State.NULL)