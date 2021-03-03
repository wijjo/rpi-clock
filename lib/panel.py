from .viewport import Viewport


class Panel:

    def on_check(self) -> bool:
        raise NotImplementedError

    def on_display(self, viewport: Viewport):
        raise NotImplementedError
