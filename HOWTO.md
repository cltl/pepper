TODO
----

- Add base cases to GraphDB 'leolani' (I get errors?)
- Fix lower/upper-case names in brain (pushing to brain works, pulling from does not)
- Fix double mentioning of items 'likes baseball and likes baseball and likes baseball'
- Fix ``IndexError: list index out of range``, when sentence is weirdly formed (e.g. some word is missing)

How To Git
----------
- pull: ``git pull origin restructure``
- push: ``git push origin restructure``

How To Boot
-----------

1. Start GraphDB Free
    - Connect within browser (Setup - Repositories - check "leolani")

2. Start Docker

3. Start COCO (pepper_tensorflow - coco.py - ctrl-shift-F10)

4. Start any app (e.g. ``pepper/intention/reactive.py``)

Enjoy (& Check settings/IP's in ``pepper/config.py``)!

How to switch between PC/Robot Host
-----------------------------------
- for Robot
```python
from pepper.framework.naoqi import NaoqiApp
app = NaoqiApp()
```
- for PC
```python
from pepper.framework.system import SystemApp
app = SystemApp()
```


Common Issues
-------------

- **I receive some error related to Docker/OpenFace**
    - Reboot Docker & try again! :)
- **Microphone samples are dropped / stuff is slow on the robot!!**
    - Make sure network is as optimal as can be
    - Tweak ``CAMERA_RESOLUTION`` & ``CAMERA_FRAMERATE`` in ``pepper/config.py``
- **Robot has weird (or local) IP**
    - Reboot robot and hope for the best!
