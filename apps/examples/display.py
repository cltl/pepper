"""Example Application that displays what it sees in the browser"""

from pepper.app_container import ApplicationContainer
from pepper.framework.abstract import AbstractApplication
from pepper.framework.component import StatisticsComponent, DisplayComponent, SceneComponent, ContextComponent, \
    ObjectDetectionComponent, FaceRecognitionComponent, SpeechRecognitionComponent, TextToSpeechComponent


class DisplayApp(ApplicationContainer,
                 AbstractApplication,           # Each Application inherits from AbstractApplication
                 StatisticsComponent,           # Show Performance Statistics in Terminal
                 DisplayComponent,              # Display what Robot (or Computer) sees in browser
                 SceneComponent,                # Scene (dependency of DisplayComponent)
                 ContextComponent,              # Context (dependency of DisplayComponent)
                 ObjectDetectionComponent,      # Object Detection (dependency of DisplayComponent)
                 FaceRecognitionComponent,      # Face Recognition (dependency of DisplayComponent)
                 SpeechRecognitionComponent,    # Speech Recognition Component (dependency)
                 TextToSpeechComponent):        # Text to Speech (dependency)

    pass  # Application does not need to react to events :)


if __name__ == '__main__':
    DisplayApp().run()
