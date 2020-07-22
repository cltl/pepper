Setup
-----

### Run on Laptop
1. Build the Docker image for [pepper_tensorflow](https://github.com/cltl/pepper_tensorflow)
  by running

    ```> docker build -t cltl/pepper_tensorflow .```

  in that repository.
2. Download GraphDB binary (`graphdb-free-<version>-dist.zip`) into `setup/graphdb-docker/lib`
3. Run `> docker-compose up` from the `setup/` folder. This starts
    * bamos/openface
    * GraphDB
    * pepper_tensorflow

  Data used by these containers is stored in `setup/data` and can be reset by removing all subfolders of that folder.
4. Make sure there is a GraphDB repository named `leolani`. If  not, run `> ./setup/setup-graphdb-repo.sh`.
5. Set ```APPLICATION_BACKEND``` to ```pepper.ApplicationBackend.SYSTEM``` in ```pepper/config.py```
6. Start any Application in ```pepper/apps/..```
7. Done
8. Start/Stop Docker by running `docker-compose start/stop`.

### Run on Robot
1. Build the Docker image for [pepper_tensorflow](https://github.com/cltl/pepper_tensorflow)
  by running

    ```> docker build -t cltl/pepper_tensorflow .```

  in that repository.
2. Download GraphDB binary (`graphdb-free-<version>-dist.zip`) into `setup/graphdb-docker/lib`
3. Run `> docker-compose up` from the `setup/` folder. This starts
    * bamos/openface
    * GraphDB
    * pepper_tensorflow

  Data used by these containers is stored in `setup/data` and can be reset by removing all subfolders of that folder.
4. Make sure there is a GraphDB repository named `leolani`. If not, run `> ./setup/setup-graphdb-repo.sh`.
5. Set ```APPLICATION_BACKEND``` to ```pepper.ApplicationBackend.NAOQI``` in ```pepper/config.py```
6. Set ```NAOQI_IP``` and ```NAOQI_PORT``` in accordance with robot's address
7. Start any Application in ```pepper/apps/..```
8. Done
9. Start/Stop Docker by running `docker-compose start/stop`.

Pepper Troubleshooting
----------------------
> No Pepper-laptop connection can be established

1. Make sure Pepper and the laptop are on the same network
2. Verify Pepper has access to network (by pressing belly-button)
3. Make sure ```NAOQI_IP``` and ```NAOQI_PORT``` are set correctly in ```pepper/config.py```

> Pepper cannot connect to network

1. Connect Pepper to network using ethernet cable
2. Press belly-button to obtain IP and update ```pepper/config.py -> NAOQI_IP``` accordingly
3. Go to robot web page (by entering IP in browser)
4. Go to network settings and connect to wifi
    - If unlisted, reboot robot (and wifi). Make sure wifi is online before robot is.
5. Shutdown robot, remove ethernet cable, and boot again. It now should work...

> Problems with speech audio

1. Start an application with StatisticsComponent and look at the STT (Speech to Text) activity
2. If no signal (i.e ```STT [..........]```):
    1. Check if the NAOqi or System Microphone is used: ```pepper/config.py -> NAOQI_USE_SYSTEM_MICROPHONE```
    2. Make sure external mic, if used, is switched on and sensitive enough (use OS settings)
    3. Make sure Pepper mic, if used, is not broken?
3. If signal is low (i.e ```STT [|||.......]``` < ```pepper/config.py -> VOICE_ACTIVITY_DETECTION_THRESHOLD```):
    1. Make sure you talk loud enough (noisy fans in Peppers head make it difficult)
    2. Make sure you talk in the right microphone (i.e. ```pepper/config.py -> NAOQI_USE_SYSTEM_MICROPHONE```)
    3. Make sure the external mics volume is high enough!
4. If signal is too high (i.e. ```STT [||||||||||]```) all the time:
    1. Peppers own mics cannot handle very loud/noisy environments, like fairs
    2. Use a microphone attached to the laptop, instead!
        - don't forget to set ```pepper/config.py -> NAOQI_USE_SYSTEM_MICROPHONE = True```
5. Microphone should process audio at 16 kHz  (i.e. Statistics: ```Mic 16.0 kHz```), if not:
    1. Lower ```CAMERA_RESOLUTION``` and/or ```CAMERA_FRAME_RATE``` in order to meet performance requirements
