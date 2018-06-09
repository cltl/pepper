# Pepper
This is the repository for Pepper applications. Use Python 2.7 32 bit

## Installation

This project build onto existing software and API's and therefore has quite an extensive setup.
This guide helps you to get up and running.

### 0. Python
The Python SDK for Pepper by SoftBank Robotics requires the use of Python 2.7 32-bit.
Please make sure you are using that version (or create a virtual environment)

### 1. Python SDK for Pepper
This project builds onto the Python SDK provided by [SoftBank Robotics](https://www.ald.softbankrobotics.com/en).
Grab the SDK for your system at the [SoftBank Robotics Download Page](https://developer.softbankrobotics.com/us-en/downloads/pepper).
Depending on your system, the `PYTHONPATH` system variable has to be set to the location of the SDK.
Instructions on how to do so can be found at the [Python SDK Install Guide](http://doc.aldebaran.com/2-5/dev/python/install_guide.html) page.

Do test if the SDK is installed correctly by verifying `import naoqi` runs without errors.

### 2. Speech to Text
This project uses either the [IBM Watson Speech to Text API](https://www.ibm.com/watson/services/speech-to-text/) or
the [Google Cloud Speech to Text API](https://cloud.google.com/speech/). Setting up an (academic) licence is explained
at those pages.

Experimental [Kaldi](http://kaldi-asr.org/) support is there, using the [Kaldi Gstreamer Docker Server](https://github.com/jcsilva/docker-kaldi-gstreamer-server).
A setup is made for a model which is trained on TED-talks, which can be downloaded [here (1.4GB!)](https://phon.ioc.ee/~tanela/tedlium_nnet_ms_sp_online.tgz).
The model is not included in the repository for storage space reasons. Please make absolutely sure, 
you put the the `tedlium_nnet_ms_sp_online` folder (at the deepest level) at `pepper/speech/kaldi/models/test/models/english`.
This is necessary because of the strict paths in the config files inside the model.
In order to use the model for speech recognition, you will need to install [Docker](https://www.docker.com/) and call `docker pull jcsilva/docker-kaldi-gstreamer-server`.
The code in this package will then automatically run the Docker image and set up the server.
Please keep in mind that, at least with this particular model, Kaldi is not performing nearly on par with Google or IBM.

### 3. Object Recognition
Object recognition is possible using Google's Inception Model, described in the [TensorFlow Image Recognition Tutorial](https://www.tensorflow.org/tutorials/image_recognition).
Since [TensorFlow](https://www.tensorflow.org/install/install_windows) is only available in Python 3
and this repository is forced to work in Python 2, because of the Python SDK for Pepper, 
a separate repository is used for the Tensorflow applications and can be found at the [Pepper TensorFlow GitHub](https://github.com/cltl/pepper_tensorflow).
This repository contains the model and the server needed to do object recognition using this package.

### 4. Face Recognition
Face recognition is done using the open source OpenFace project ([Site](http://cmusatyalab.github.io/openface/), [Git](https://github.com/cmusatyalab/openface)),
which is, to put it mildly, difficult to install; Probably even impossible on Windows.
Luckily, the developers were so kind to provide a Docker image, which can be obtained using `docker pull bamos/openface`.
This repository will communicate with and run the image, providing face recognition for Pepper.

#### 5. Brain in a triple store
The brain is stored in a triple store. Currently, you need to have a local instance of [GraphDB](https://ontotext.com/graphdb-free-download/). You need to get an account to get a free download.

Once launched, set up a repository with id and name: leolani. To populate the brain with some basic statements you can go to the menu Import >> RDF upload the file on pepper/knowledge_representation/brainOutput/brainBase.trig

Alternatively, you can the main on run pepper/knowledge/theory_of_mind.py which automatically uploads every test statement.

### 6. Reference

When using our implementation or ideas, please make reference to:

Vossen, Piek , Selene Baez, Lenka Bajčetić , and Bram Kraaijeveld (2018), Leolani: a reference machine with a theory of mind for social communication, Invited Keynote speech, TSD-2018, Brno.
