from pepper.event import Event
import numpy as np


class FaceInfo:
    def __init__(self, info):
        self._location = np.array(info[0][1:3])
        self._size = np.array(info[0][3:5])
        self._id = int(info[1][0])
        self._score = float(info[1][1])
        self._label = info[1][2]

        self._eye_left = EyeInfo(info[1][3])
        self._eye_right = EyeInfo(info[1][4])
        self._nose = NoseInfo(info[1][7])
        self._mouth = MouthInfo(info[1][8])

    @property
    def location(self):
        """
        Returns
        -------
        location: np.array
            Location of the face [alpha, beta] in camera angles
        """
        return self._location

    @property
    def size(self):
        """
        Returns
        -------
        size: np.array
            Size of the face [x, y] in camera angles
        """
        return self._size

    @property
    def id(self):
        """
        Returns
        -------
        id: int
            ID of the face
        """
        return self._id

    @property
    def score(self):
        """
        Returns
        -------
        score: float
            Score returned by the face recognition process
        """
        return self._score

    @property
    def label(self):
        """
        Returns
        -------
        label: str
            If recognised, label associated with face
        """
        return self._label

    @property
    def eye_left(self):
        """
        Returns
        -------
        eye_left: EyeInfo
            Information about the left eye
        """
        return self._eye_left

    @property
    def eye_right(self):
        """
        Returns
        -------
        eye_right: EyeInfo
            Information about the right eye
        """
        return self._eye_right

    @property
    def nose(self):
        """
        Returns
        -------
        nose: NoseInfo
            Information about the nose
        """
        return self._nose

    @property
    def mouth(self):
        """
        Returns
        -------
        mouth: MouthInfo
            Information about the mouth
        """
        return self._mouth


class EyeInfo:
    def __init__(self, info):
        self._center = np.array(info[0:2])
        self._nose_side_limit = np.array(info[2:4])
        self._ear_side_limit = np.array(info[4:6])

    @property
    def center(self):
        """
        Returns
        -------
        center: np.array
            Center of eye [x, y] in camera angles
        """
        return self._center

    @property
    def nose_side_limit(self):
        """
        Returns
        -------
        nose_side_limit: np.array
            Nose side limit of eye [x, y] in camera angles
        """
        return self._nose_side_limit

    @property
    def ear_side_limit(self):
        """
        Returns
        -------
        ear_side_limit: np.array
            Ear side limit of eye [x, y] in camera angles
        """
        return self._ear_side_limit


class NoseInfo:
    def __init__(self, info):
        self._bottom_center_limit = np.array(info[0:2])
        self._bottom_left_limit = np.array(info[2:4])
        self._bottom_right_limit = np.array(info[4:6])

    @property
    def bottom_center_limit(self):
        """
        Returns
        -------
        bottom_center_limit: np.array
            Bottom center limit of nose [x, y] in camera angles
        """
        return self._bottom_center_limit

    @property
    def bottom_left_limit(self):
        """
        Returns
        -------
        bottom_left_limit: np.array
            Bottom left limit of nose [x, y] in camera angles
        """
        return self._bottom_left_limit

    @property
    def bottom_right_limit(self):
        """
        Returns
        -------
        bottom_right_limit: np.array
            Bottom right limit of nose [x, y] in camera angles
        """
        return self._bottom_right_limit


class MouthInfo:
    def __init__(self, info):
        self._left_limit = np.array(info[0:2])
        self._right_limit = np.array(info[2:4])
        self._top_limit = np.array(info[4:6])

    @property
    def left_limit(self):
        """
        Returns
        -------
        left_limit: np.array
            Left limit of mouth [x, y] in camera angles
        """
        return self._left_limit

    @property
    def right_limit(self):
        """
        Returns
        -------
        right_limit: np.array
            Right limit of mouth [x, y] in camera angles
        """
        return self._right_limit

    @property
    def top_limit(self):
        """
        Returns
        -------
        top_limit: np.array
            Top limit of mouth [x, y] in camera angles
        """
        return self._top_limit


class FaceDetectedEvent(Event):
    def __init__(self, session, callback):
        """
        Face Detected Event.

        Parameters
        ----------
        session: qi.Session
            Session to attach this event to
        callback: callable
            Function to call when event occurs
        """

        super(FaceDetectedEvent, self).__init__(session, callback)

        # Connect to 'FaceDetected' event
        self._subscriber = self.memory.subscriber("FaceDetected")
        self._subscriber.signal.connect(self._on_event)

        # Subscribe to ALFaceDetection service. This way the events will actually be cast.
        self._detection = self.session.service("ALFaceDetection")
        self._detection.subscribe(self.name)

    def _on_event(self, value):
        """
        Raw Face Detected Event: convert raw event data to structured data

        Parameters
        ----------
        value: list
            Structure specified at http://doc.aldebaran.com/2-5/naoqi/peopleperception/alfacedetection.html
        """
        if value:
            timestamp, info, torso, robot, camera = value

            time = float(timestamp[0]) + 1E-6 * float(timestamp[1])
            faces = [FaceInfo(face_info) for face_info in info[:-1]]
            recognition = info[-1]

            self.on_event(time, faces, recognition)

    def on_event(self, time, faces, recognition):
        """
        Face Detected Event: callback should have identical signature

        Parameters
        ----------
        time: float
            Time since Pepper boot
        faces: list of FaceInfo
            List of faces Pepper sees, with information for each of them.
        recognition: list
            List of recognised faces in the following format:
                []              : nothing new
                [2, [label]]    : one face recognised
                [3, label[n]]   : multiple faces recognised
                [4]             : new face detected for > 8 seconds
        """

        self.callback(time, faces, recognition)

    def close(self):
        """Cleanup by unsubscribing from 'ALFaceDetection' service"""
        self._detection.unsubscribe(self.name)


class LookingAtRobotEvent(Event):
    def __init__(self, session, callback):
        """
        Looking At Robot Event.

        Parameters
        ----------
        session: qi.Session
            Session to attach this event to
        callback: callable
            Function to call when event occurs
        """

        super(LookingAtRobotEvent, self).__init__(session, callback)

        # Connect to "GazeAnalysis/PersonStartsLookingAtRobot" event
        self._subscriber = self.memory.subscriber("GazeAnalysis/PersonStartsLookingAtRobot")
        self._subscriber.signal.connect(self.on_look)

        # Subscribe to ALGazeAnalysis service. This way the events will actually be cast.
        self._service = self.session.service("ALGazeAnalysis")
        self._service.subscribe(self.name)

    def on_look(self, person):
        """
        Looking At Robot Event: callback should have identical signature

        Parameters
        ----------
        person: int
            ID of person looking at Pepper
        """
        self.callback(person)

    def close(self):
        """Cleanup by unsubscribing from 'AlGazeAnalysis' service"""
        self._service.unsubscribe(self.name)