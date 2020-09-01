from pepper.framework.abstract.backend import AbstractBackend
from pepper.framework.di_container import DIContainer

class BackendContainer(DIContainer):
    @property
    def backend(self):
        # type: () -> AbstractBackend
        """
        Returns
        -------
        backend: AbstractBackend :class:`~pepper.framework.abstract.backend.AbstractBackend`
        """
        raise ValueError("No backend configured")