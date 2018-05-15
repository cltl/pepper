import pepper


camera = pepper.SystemCamera()
openface = pepper.OpenFace()

people = pepper.load_people()
people.update(pepper.load_people('paradiso'))

cluster = pepper.PeopleCluster(people)

while True:
    face = openface.represent(camera.get())

    if face:
        bounds, representation = face
        print(cluster.classify(representation))