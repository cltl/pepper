import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


NAME_PATH = r"C:\Users\Bram\Documents\Pepper\pepper\tests\data\lfw\names.txt"
MATRIX_PATH = r"C:\Users\Bram\Documents\Pepper\pepper\tests\data\lfw\matrix.bin"
MIN_PICTURES = 30

def distance(matrix, vector):
    # return np.sum((matrix - vector) ** 2, 1)
    return np.linalg.norm(matrix - vector, 2, 1)

matrix = np.fromfile(MATRIX_PATH, np.float32).reshape(-1, 128)

with open(NAME_PATH) as name_file:
    names_raw = name_file.read().split("\n")

name_indices = {}

# Assemble Matrix Indices for Names
for i, name in enumerate(names_raw):
    if name in name_indices: name_indices[name].append(i)
    else: name_indices[name] = [i]

names = [name for (name, index) in name_indices.iteritems() if len(index) >= MIN_PICTURES]

# Get Mean, Inner Distance and Outer Distance Matrices
mean = np.empty((len(names), 128), np.float32)
inner_distance = np.empty((len(names), 2), np.float32)
outer_distance = np.empty((len(names), 2), np.float32)

for i, name in enumerate(names):
    face = matrix[name_indices[name]]
    mean[i] = np.mean(face, 0)
    dist = distance(face, mean[i])
    inner_distance[i] = np.mean(dist), np.std(dist)

for i, name in enumerate(names):
    dist = np.concatenate((distance(mean[:i], mean[i]), distance(mean[i+1:], mean[i])))
    outer_distance[i] = np.min(dist), np.std(dist)


with open(r"C:\Users\Bram\Documents\Pepper\pepper\tests\data\lfw\submatrix.bin", 'wb') as submatrix_file:
    submatrix_file.write(mean)

with open(r"C:\Users\Bram\Documents\Pepper\pepper\tests\data\lfw\subnames.txt", 'w') as subnames_file:
    for name in names:
        subnames_file.write("{}\n".format(name))


INNER_DISTANCE_MEAN, INNER_DISTANCE_STD = np.mean(inner_distance, 0)
OUTER_DISTANCE_MEAN, OUTER_DISTANCE_STD = np.mean(outer_distance, 0)

print("Comparing {} people with {} or more pictures".format(len(names), MIN_PICTURES))
print("Inner Distance: {}".format((INNER_DISTANCE_MEAN, INNER_DISTANCE_STD)))
print("Outer Distance: {}".format((OUTER_DISTANCE_MEAN, OUTER_DISTANCE_STD)))


# Accuracy

def classify_face(face):
    dist = distance(mean, face)
    dist_min_index = int(np.argmin(dist))

    # Known Face
    if dist[dist_min_index] < INNER_DISTANCE_MEAN:
        return names[dist_min_index]

    # New Face
    elif dist[dist_min_index] > OUTER_DISTANCE_MEAN:
        return False

    # Unsure
    else: return None


def classify_face_probability(face, threshold=0.8):
    dist = distance(mean, face)
    dist_min_index = int(np.argmin(dist))

    inner_probability = stats.norm.sf(dist[dist_min_index], INNER_DISTANCE_MEAN, INNER_DISTANCE_STD)
    outer_probability = stats.norm.cdf(dist[dist_min_index], OUTER_DISTANCE_MEAN, OUTER_DISTANCE_STD)

    if inner_probability > threshold:
        return names[dist_min_index]
    elif outer_probability > threshold:
        return False
    else:
        return None


known_accuracy = []
new_accuracy = []

total = len(matrix)
non_classified = 0

# Testing
for name, face in zip(names_raw, matrix):
    classification = classify_face_probability(face)

    if classification:
        known_accuracy.append(classification == name)
    elif classification == False:
        new_accuracy.append(not name in names)
    else:
        non_classified += 1


print("\n")
print("Known Accuracy: {}".format(np.mean(known_accuracy)))
print("New Accuracy: {}".format(np.mean(new_accuracy)))
print("Fraction Classified: {}".format((total - non_classified) / float(total)))


# from pepper.vision.camera import SystemCamera
# from pepper.vision.classification.face import FaceRecognition
# from time import sleep
#
# recognition = FaceRecognition()
#
# for i in range(3):
#     print(3 - i)
#     sleep(1)
#
# for i in range(10):
#     print("Picture {}".format(i))
#     result = recognition.representation(SystemCamera().get())
#
#     if result:
#         bounds, representation = result
#         print(classify_face_probability(representation))
#     else:
#         print("Couldn't Find Face")


BINS = 20
plt.hist(inner_distance[:, 0], bins=BINS, label='inner')
plt.hist(outer_distance[:, 0], bins=BINS, label='outer')
plt.legend()
plt.show()
