from pepper.vision.classification.data import load_lfw
import requests
import re

# Get Unique Names and sort them alphabetically
names = sorted(list(set(re.findall('([A-Za-z]+)', name)[0] for name in load_lfw()[0])))

with open('lfw_gender3.txt', 'w') as file:
    for i in range(names.index("Sven")+1, len(names), 10):

        # Create Request URL
        url = "https://api.genderize.io/?"
        for ii, name in enumerate(names[i:i+10]):
            url += "name[{}]={}&".format(ii, name)
        url = url[:-1]

        file.write("{}\n".format(requests.get(url).text))