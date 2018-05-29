import naoqi
import random
import time

ADDRESS = '192.168.1.101', 9559
DEVICE_TARGET = "ALVideoDevice"
CLIENT_ID = str(random.getrandbits(32))

device_proxy = naoqi.ALProxy(DEVICE_TARGET, *ADDRESS)

client = device_proxy.subscribeCamera(
    CLIENT_ID,
    0,  # Top Camera
    2,  # Resolution
    8,  # RGB
    0,  # FrameRate
)

t0 = time.time()

mean_time = 0.0
index = 0

for i in range(50):
    result = device_proxy.getImageRemote(client)[6]
    mean_time = (index * mean_time + time.time() - t0) / (index + 1)

    fps = 1/mean_time
    kbps = fps * len(result) / 1024

    index += 1
    print("{:3.4f} fps : {:3.4f} kbps".format(1/mean_time, kbps))
    t0 = time.time()

device_proxy.unsubscribe(client)