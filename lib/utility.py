import pygame


def sub_rect(outer_rect,
             left=None,
             top=None,
             width=None,
             height=None,
             fleft=None,
             ftop=None,
             fwidth=None,
             fheight=None):
    """Calculate sub-rect of outer rect using x, y, w, h values between 0 and 1."""
    if fwidth is None:
        if width is None:
            width = outer_rect.width
    else:
        width = int(outer_rect.width * fwidth)
    if fheight is None:
        if height is None:
            height = outer_rect.height
    else:
        height = int(outer_rect.height * fheight)
    if fleft is None:
        if left is None:
            left = outer_rect.left
        else:
            left = outer_rect.left + left
    else:
        left = outer_rect.left + int(fleft * (outer_rect.width - width))
    if ftop is None:
        if top is None:
            top = outer_rect.top
        else:
            top = outer_rect.top + top
    else:
        top = outer_rect.top + int(ftop * (outer_rect.height - height))
    return pygame.Rect(left, top, width, height)
