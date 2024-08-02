#  test of on_new_sample() where inference done

import sys
import os
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
#     # Create a buffer with green YUY2 image.
#     data = np.full((480, 640, 2), 255, dtype=np.uint8)
#     data[::2, ::2, 1] = 0  # Chroma blue
#     data[1::2, ::2, 1] = 0  # Chroma red
#     # Create a GstBuffer from the NumPy data.
#     buf = Gst.Buffer.new_wrapped(bytes(data))
#     # Push the buffer into the appsrc.
#     appsrc.emit('push-buffer', buf)
#     return Gst.FlowReturn.OK

def on_new_sample(appsink):
    # Fill a numpy array with YUY2 data
    # U (Cb) and V (Cr) set to 0 (neutral chroma), Y set to 150 (greenish
    # luma), according to Y'CbCr in TV/video (ITU-R Rec. 601)
    w, h = 640, 480
    data = np.zeros([h, w, 2], dtype=np.uint8)
    data[..., 0] = 150  # Y0 and Y1
    data[0::2, 1::2, 1] = -86  # U
    data[1::2, 1::2, 1] = 29  # V
    # post processing here
    buf = Gst.Buffer.new_wrapped(bytes(data))
    # buf.pts = Gst.util_uint64_scale(appsrc.get_property('format'),
    #                                               buf.n_buffer * buf.frames, Gst.SECOND)
    # buf.duration = Gst.util_uint64_scale(appsrc.get_property('format'), buf.frames, Gst.SECOND)
    appsrc.emit('push-buffer', buf)
    return Gst.FlowReturn.OK


# Create GStreamer pipeline for capturing and processing data
pipeline_in = Gst.parse_launch(
    'v4l2src device=/dev/video0 ! '
    'video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! '
    'queue ! nvvideoconvert ! '
    'appsink name=my_sink'
    # 'nvvideoconvert ! autovideosink'
)

pipeline_out = Gst.parse_launch(
    'appsrc name=my_src is-live=true format=GST_FORMAT_TIME caps=video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! '
    'autovideosink'
)

appsrc = pipeline_out.get_by_name("my_src")

ret = pipeline_out.set_state(Gst.State.PLAYING)
if ret == Gst.StateChangeReturn.FAILURE:
    logging.error("Error starting the output pipeline")
    exit(-1)
else:
    logging.info("Output pipeline started")

logging.info("started pipeline")

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