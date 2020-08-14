from pepper import ApplicationBackend
from pepper.config import APPLICATION_BACKEND
from pepper.framework.event.memory import SynchronousEventBusContainer

if APPLICATION_BACKEND is ApplicationBackend.SYSTEM:
    from pepper.framework.backend.system import SystemBackendContainer as backend_container
elif APPLICATION_BACKEND is ApplicationBackend.NAOQI:
    from pepper.framework.backend.naoqi import NAOqiBackendContainer as backend_container
else:
    raise ValueError("Unknown backend configured: " + str(APPLICATION_BACKEND))


class ApplicationContainer(backend_container, SynchronousEventBusContainer):
    pass