from threading import Lock
from time import sleep

class DIContainer(object):
    """
    Base class for Dependency Injection containers.

    Dependency Injection containers manages manages object creation and it's
    life-time, and also injects dependencies to the class.
    """
    __lock = Lock()

    @property
    def _lock(self):
        return DIContainer.__lock


def singleton(method):
    def decorated(self, *args, **kwargs):
        container_type = type(self)
        singleton_attr = "_" + method.__name__
        if not hasattr(container_type, singleton_attr):
            create_instance = False
            with self._lock:
                if not hasattr(container_type, singleton_attr):
                    #First set to None and then instanciate outside the lock to avoid dead-locks
                    setattr(container_type, singleton_attr, None)
                    create_instance = True
            if create_instance:
                setattr(container_type, singleton_attr, method(self, *args, **kwargs))

        # The instance is created outside the lock, therefore we can end up here with None
        while getattr(container_type, singleton_attr) is None:
            sleep(0.001)

        return getattr(container_type, singleton_attr)

    return decorated