from threading import Lock
from time import sleep

class DIContainer(object):
    """
    Base class for Dependency Injection containers.

    DIContainers manage object creation (injecting necessary dependencies) and
    their life-cycle.
    """
    __lock = Lock()

    @property
    def _lock(self):
        return DIContainer.__lock


def singleton(method):
    """
    Decorator to provide singleton instances from methods of a DIContainer.
    """
    def decorated(self, *args, **kwargs):
        container_type = type(self)
        singleton_attr = "_" + method.__name__
        if not hasattr(container_type, singleton_attr):
            create_instance = False
            with self._lock:
                if not hasattr(container_type, singleton_attr):
                    #First set to None and then instantiate outside the lock to avoid dead-locks
                    setattr(container_type, singleton_attr, None)
                    create_instance = True
            if create_instance:
                instance = method(self, *args, **kwargs)
                if not instance:
                    print("Scheisse")
                    raise ValueError("could not set " + singleton_attr)
                setattr(container_type, singleton_attr, instance)

        # The instance is created outside the lock, therefore we can end up here with None
        while getattr(container_type, singleton_attr) is None:
            sleep(0.01)

        return getattr(container_type, singleton_attr)

    return decorated