from pepper.framework.abstract.tablet import AbstractTablet


class SystemTablet(AbstractTablet):
    """Access Robot Tablet to show URLs"""

    def show(self, url):
        # type: (str) -> None
        """
        Show URL

        Parameters
        ----------
        url: str
            WebPage/Image URL
        """
        pass

    def hide(self):
        # type: () -> None
        """Hide whatever is shown on tablet"""
        pass
