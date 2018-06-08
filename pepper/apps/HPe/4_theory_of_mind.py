import pepper


class TheoryOfMindApp(pepper.SensorApp):
    def __init__(self):
        super(TheoryOfMindApp, self).__init__(pepper.ADDRESS)

    def on_transcript(self, transcript, person):
        super(TheoryOfMindApp, self).on_transcript(transcript, person)


if __name__ == "__main__":
    TheoryOfMindApp().run()
