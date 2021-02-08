from typing import Union


class AbstractTablet(object):
    """Access Robot Tablet to show URLs"""

    def show(self, url):
        # type: (Union[str, unicode]) -> None
        """
        Show URL

        Parameters
        ----------
        url: str
            WebPage/Image URL
        """
        raise NotImplementedError()

    def hide(self):
        # type: () -> None
        """Hide whatever is shown on tablet"""
        raise NotImplementedError()
