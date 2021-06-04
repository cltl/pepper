# VU Amsterdam - CLTL - Robot Framework

Repository for Robot Applications created as part of the [Computational Lexicology & Terminology Lab (CLTL)](http://www.cltl.nl) at the Vrije Universiteit, Amsterdam.

| **This is the original Python 2 version of the Leolani platform. This version was intended for the robot use as it supports the NAOqi backend. However, development on this repository has stopped due to the [sunsetting of Python 2](https://www.python.org/doc/sunset-python-2/). For the latest version of this software please see the [Python 3 version of the repository](https://github.com/leolani/pepper).** |
|---|

![Pepper Robot Leolani](https://github.com/cltl/pepper/blob/develop/docs/images/pepper.png)

### Features
 - A framework for creating interactive Robot Applications using Python, to enable:
   - Human-Robot conversation using Speech-to-Text and Text-to-Speech
   - Recognising friends by face and learning about them and the world through conversation
   - Recognising and positioning the people and objects in its enviroment.
 - Natural Language Understanding through Syntax Trees (Grammars)
 - Knowledge Representation of all learned facts through a RDF Graph: the robot's Brain!
 - Curiosity based on Knowledge Gaps and Conflicts resulting from learned facts
 - Realtime visualisation in web browser

## Getting started
Check out our [WIKI](https://github.com/cltl/pepper/wiki) for information on [how it works](https://github.com/cltl/pepper/wiki/2.-How-it-works) and [how to set up](https://github.com/cltl/pepper/wiki/1.-Set-up).

Check out our [API Reference](https://cltl.github.io/pepper/) and [Sample Applications](https://github.com/cltl/pepper/tree/develop/apps/examples)!


### Prerequisites

* NAOqi Python SDK (version 2.5.10) from the [Softbank robotics download page](https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares/former-versions?category=108)
* [Python 2.7.10](https://www.python.org/downloads/release/python-2710/) 
* An application on [Wolfram Alpha](https://products.wolframalpha.com/api/) with API access
* A project on the [Google Cloud Platform](https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries) supporting Text-To-Speech and Speech-To-Text APIs
* [Docker Engine](https://docs.docker.com/engine/install/)
* [OpenFace](http://cmusatyalab.github.io/openface/) 
* Pepper's sister-project: [pepper_tensorflow](https://github.com/cltl/pepper_tensorflow), which includes the Tensorflow services within Python 3.6.
* [GraphDB](http://graphdb.ontotext.com/) with a repository named `leolani`

Detailed instructions on [how to set up](https://github.com/cltl/pepper/wiki/1.-Set-up).


## More information
More information on the Make Robots Talk project at CLTL can be found on its [website](http://makerobotstalk.nl)

###  Citation

Please cite (at least one of) the following papers if you use this software in your research:

[Leolani: a reference machine with a theory of mind for social communication](https://arxiv.org/abs/1806.01526)
```
@inproceedings{vossen2018leolani,
      title={Leolani: a reference machine with a theory of mind for social communication},
      author={Vossen, Piek and Baez, Selene and Bajc̆eti{\'c}, Lenka and Kraaijeveld, Bram},
      booktitle={International conference on text, speech, and dialogue},
      pages={15--25},
      year={2018},
      organization={Springer},
}
```

[A communicative robot to learn about us and the world](http://www.dialog-21.ru/media/4636/vossenpplusetal-050.pdf)
```
@inproceedings{vossen2019communicative,
      title={A communicative robot to learn about us and the world},
      author={Vossen, Piek and Santamaria, Selene Baez and Bajc̆eti{\'c}, Lenka and Ba{\v{s}}i{\'c}, Suzana and Kraaijeveld, Bram},
      booktitle={2019 Annual International Conference on Computational Linguistics and Intellectual Technologies, Dialogue 2019},
      pages={728--743},
      year={2019}
}
```

[Leolani: A robot that communicates and learns about the shared world](http://ceur-ws.org/Vol-2456/paper47.pdf)
```
@inproceedings{vossen2019leolani,
      title={Leolani: A robot that communicates and learns about the shared world},
      author={Vossen, Piek and Baez, Selene and Baj{\v{c}}eti{\'c}, Lenka and Ba{\v{s}}i{\'c}, Suzana and Kraaijeveld, Bram},
      booktitle={2019 ISWC Satellite Tracks (Posters and Demonstrations, Industry, and Outrageous Ideas), ISWC 2019-Satellites},
      pages={181--184},
      year={2019},
      organization={CEUR-WS}
}
```

[Modelling context awareness for a situated semantic agent](https://link.springer.com/chapter/10.1007/978-3-030-34974-5_20)
```
@inproceedings{vossen2019modelling,
      title={Modelling context awareness for a situated semantic agent},
      author={Vossen, Piek and Baj{\v{c}}eti{\'c}, Lenka and Baez, Selene and Ba{\v{s}}i{\'c}, Suzana and Kraaijeveld, Bram},
      booktitle={International and Interdisciplinary Conference on Modeling and Using Context},
      pages={238--252},
      year={2019},
      organization={Springer}
}
```

### License

Distributed under the MIT License. See [`LICENSE`](https://github.com/cltl/pepper/blob/develop/LICENCE) for more information.

### Authors
* [Bram Kraaijeveld](https://github.com/as-the-crow-flies)
* [Selene Báez Santamaría](https://github.com/selBaez)
* [Lenka Bajc̆etic](https://github.com/lenkaB)
* [Piek Vossen](https://github.com/piekvossen)