from pepper import OpenFace
from scipy.ndimage import imread
import matplotlib.pyplot as plt

IMAGE_PATH = r"C:\Users\Bram\Documents\Pepper\data\people\lfw\Alexa_Loren\Alexa_Loren_0001.jpg"
image = imread(IMAGE_PATH)

openface = OpenFace()
bounds, representation = openface.represent(image)
print(bounds)
print(representation)

openface.stop()

plt.imshow(image[int(bounds.x):int(bounds.x+bounds.width), int(bounds.y):int(bounds.y+bounds.height)])
plt.show()
