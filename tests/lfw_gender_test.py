from pepper.vision.classification.face import FaceRecognition
from pepper.vision.classification.data import load_lfw, load_lfw_gender
import numpy as np

names, matrix = load_lfw()
gender = load_lfw_gender()

classification = np.empty(len(gender), np.bool)
probability = np.empty(len(gender), np.float32)

for i in range(len(gender)):
    c,p = FaceRecognition.gender(matrix[i])
    classification[i] = c
    probability[i] = p


threshold = 0.75
classification = classification[probability > threshold]
gender = gender[probability > threshold]

# Actual - Predicted
male_male = np.sum(np.logical_and(gender == 0, classification == 0))
male_female = np.sum(np.logical_and(gender == 0, classification == 1))
female_female = np.sum(np.logical_and(gender == 1, classification == 1))
female_male = np.sum(np.logical_and(gender == 1, classification == 0))

total = float(male_male + male_female + female_female + female_male)
accuracy = (male_male + female_female) / total
male_accuracy = male_male / float(male_male + male_female)
female_accuracy = female_female / float(female_female + female_male)

print(accuracy, male_accuracy, female_accuracy, np.average(probability > threshold))