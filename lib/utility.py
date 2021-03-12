import pygame
from dataclasses import dataclass
from typing import Optional

from . import log
from .typing import Margins


@dataclass
class MarginData:
    left: int
    top: int
    right: int
    bottom: int

    def adjust_rect(self, rect: pygame.Rect):
        return pygame.Rect(rect.left + self.left,
                           rect.top + self.top,
                           rect.width - (self.left + self.right),
                           rect.height - (self.top + self.bottom))

    @classmethod
    def from_raw(cls, margins: Optional[Margins]) -> 'MarginData':
        """
        Convert margin spec as tuple, integer, or None to (left, top, right, bottom) tuple.

        :param margins: margin specification
        :return: (left, top, right, bottom) tuple
        """
        if margins is None:
            return cls(0, 0, 0, 0)
        if isinstance(margins, int):
            return cls(margins, margins, margins, margins)
        # Handle lists as tuples, to accommodate data from external configurations.
        if isinstance(margins, (tuple, list)) and len(margins) == 2:
            return cls(margins[0], margins[1], margins[0], margins[1])
        if isinstance(margins, (tuple, list)) and len(margins) == 4:
            return cls(margins[0], margins[1], margins[2], margins[3])
        log.error(f'Bad margins value: {margins}')
        return cls(0, 0, 0, 0)


def sub_rect(outer_rect: pygame.Rect,
             left=None,
             top=None,
             width=None,
             height=None,
             fleft=None,
             ftop=None,
             fwidth=None,
             fheight=None,
             margins: Margins = None):
    """Calculate sub-rect of outer rect using x, y, w, h values between 0 and 1."""
    inner_rect = MarginData.from_raw(margins).adjust_rect(outer_rect)
    if fwidth is None:
        if width is None:
            width = inner_rect.width
    else:
        width = int(inner_rect.width * fwidth)
    if fheight is None:
        if height is None:
            height = inner_rect.height
    else:
        height = int(inner_rect.height * fheight)
    if fleft is None:
        if left is None:
            left = inner_rect.left
        else:
            left = inner_rect.left + left
    else:
        left = inner_rect.left + int(fleft * (inner_rect.width - width))
    if ftop is None:
        if top is None:
            top = inner_rect.top
        else:
            top = inner_rect.top + top
    else:
        top = inner_rect.top + int(ftop * (inner_rect.height - height))
    ret_rect = pygame.Rect(left, top, width, height)
    return ret_rect
