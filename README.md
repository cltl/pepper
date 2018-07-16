CLTL Pepper/Nao Repository
--------------------------

This is the (WIP) repository for CLTL Pepper/Nao Applications.

#### (To Be Implemented) Features
- [x] Object-Oriented wrapper around nao(qi)
- [x] Creating apps that run both on the robot and on host machine
- [ ] Framework for creating BDI applications
- [ ] Machine Learning necessary for Human-Robot conversation
- [ ] Realtime (interactive?) visualisation of BDI state in web browser


#### Installation

##### 0: Python 2.7 (32-bit Windows / 64-bit Linux)
The CLTL Pepper/Nao Repository is dependent on the ``Naoqi Python SDK`` by Softbank Robotics,
which is only available for 32-bit Python 2.7 on Windows and 64-bit Python 2.7 on Linux.

##### 1: Naoqi Python SDK by Softbank Robotics
This project builds onto the ``Naoqi Python SDK`` by SoftBank Robotics.
Please refer to their [install guide](http://doc.aldebaran.com/2-5/dev/python/install_guide.html) for more information.
Please make sure the ``PYTHONPATH`` environment variable reflects the location of the SDK and you're using Python 2.7!

##### 3: Google Cloud Speech-to-Text
The [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text/) is used as Speech Recognition solution for this project.
Please refer to their website for licencing and installation instructions.
It is of course possible to use a different Automatic Speech Recognition (ASR) solution, if you wish!

##### 4: OpenFace (Docker)
Face recognition in this project is done using the open source OpenFace project ([Site](http://cmusatyalab.github.io/openface/), [Git](https://github.com/cmusatyalab/openface)),
which is, to put it mildly, difficult to install; Probably even impossible on Windows.
Luckily, the developers were so kind to provide a [Docker](https://www.docker.com/) image, which can be obtained using `docker pull bamos/openface`.
If you're planning to run Docker on a Windows machine, make sure you have Windows Pro/Enterprise!

##### 5: Object Recognition (Pepper Tensorflow)
In order to use the [Inception](https://www.tensorflow.org/tutorials/images/image_recognition) and [COCO](cocodataset.org/) models natively within this project,
you need to clone pepper's sister-project: [pepper_tensorflow](https://github.com/cltl/pepper_tensorflow), which includes the Tensorflow services within Python 3.6.
These services need to run as a separate process either locally or remotely next to the main application.
Since Tensorflow requires Python 3, this is our way of using Tensorflow in an otherwise Python 2.7 repo.


##### 6: Other Python Dependencies
This project depends on ``numpy``, ``OpenCV (cv2)``, ``pyaudio`` and ``webrtcvad``.
Most of these packages can be installed using ``pip``,  with one notable exception being ``OpenCV``,
which needs to be [downloaded](https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_setup/py_table_of_contents_setup/py_table_of_contents_setup.html) and build manually (Windows binaries exist).