from typing import Self
from typing import Optional
from typing import Callable

import pygame as pg
from pygame.typing import Point
from pygame.typing import ColorLike


# If _rect is set by child class, child class should make sure
# it takes scroll into account
class _Widget(object):
    def __init__(self: Self, pos: Point, size: Point=(0, 0)) -> None:
        self._surf = pg.Surface(size)
        self._rect = pg.Rect(pos, size)
        self._pos = pos
        self._scroll = 0

    @property
    def surf(self: Self) -> pg.Surface:
        return self._surf

    @property
    def pos(self: Self) -> tuple:
        return (self._pos[0], self._pos[1] + self._scroll)

    @property
    def scroll(self: Self) -> Real:
        return self._scroll

    @scroll.setter
    def scroll(self: Self, value: Real) -> None:
        self._scroll = value
        self._rect.y = self._pos[1] + value

    def handle_event(self: Self, event: pg.Event) -> None:
        pass

    def update(self: Self,
               mouse_pos: Point,
               mouse_pressed: tuple[bool]) -> None:
        pass


class Surface(_Widget):
    def __init__(self: Self, pos: Point, surf: pg.Surface) -> None:
        super().__init__(pos)
        self._surf = surf

    @property
    def surf(self: Self) -> pg.Surface:
        return self._surf

    @surf.setter
    def surf(self: Self, value: pg.Surface) -> None:
        self._surf = value


class Label(_Widget):
    def __init__(self: Self,
                 pos: Point,
                 text: str,
                 font: pg.Font,
                 bgcolor: Optional[ColorLike]=None,
                 wraplength: int=0) -> None:
        super().__init__(pos)
        self._bgcolor = bgcolor
        self._wraplength = wraplength
        self._font = font
        self.text = text

    @property
    def text(self: Self) -> str:
        return self._text

    @text.setter
    def text(self: Self, value: str) -> None:
        self._text = value
        self._surf = self._font.render(
            value,
            1,
            (255, 255, 255),
            bgcolor=self._bgcolor,
            wraplength=self._wraplength,
        )


class Button(_Widget): # Text Button
    # COLORS
    # default: red
    # hover: blue
    # click: outline blue

    def __init__(self: Self,
                 pos: Point,
                 text: str,
                 func: Callable,
                 font: pg.Font) -> None:

        super().__init__(pos)
        self._func = func
        self._font = font
        self.text = text
        self._surf = self._surfs[0]

    @property
    def text(self: Self) -> str:
        return self._text

    @text.setter
    def text(self: Self, value: str) -> None:
        self._text = value
        text = self._font.render(value, 1, (255, 255, 255))
        self._rect = pg.Rect(self._pos, text.size)
        self._rect.y = self._pos[1] + self._scroll
        
        # Surfs
        default = pg.Surface(text.size)
        default.fill((0, 0, 255))
        hover = pg.Surface(text.size)
        hover.fill((255, 0, 0))
        click = pg.Surface(text.size)
        pg.draw.rect(
            click,
            (255, 0, 0),
            (0, 0, text.width, text.height),
            width=2,
        )

        self._surfs = (default, hover, click)
        for surf in self._surfs:
            surf.blit(text, (0, 0))

    def handle_event(self: Self, event: pg.Event) -> None:
        if (event.type == pg.MOUSEBUTTONDOWN
            and self._rect.collidepoint(event.pos)):
                self._func()

    def update(self: Self,
               mouse_pos: Point,
               mouse_pressed: tuple[bool]) -> None:
        # slick boolean index
        collision = self._rect.collidepoint(mouse_pos)
        self._surf = self._surfs[collision]
        if mouse_pressed[0] and collision:
            self._surf = self._surfs[2]

class Toggle(_Widget):
    # COLORS
    # default: outline red
    # hover: outline blue
    # click: blue

    def __init__(self: Self,
                 pos: Point,
                 font: pg.Font,
                 text: str=' X ') -> None:

        super().__init__(pos)
        self._font = font
        self.text = text
        self._surf = self._surfs[0]
        self._state = False

    @property
    def state(self: Self) -> bool:
        return self._state

    @state.setter
    def state(self: Self, value: bool) -> None:
        self._state = value

    @property
    def text(self: Self) -> str:
        return self._text

    @text.setter
    def text(self: Self, value: str) -> None:
        self._text = value
        text = self._font.render(value, 1, (255, 255, 255))
        self._rect = pg.Rect(self._pos, text.size)
        self._rect.y = self._pos[1] + self._scroll
        
        # Surfs
        untoggled = pg.Surface(text.size)
        pg.draw.rect(
            untoggled,
            (0, 0, 255),
            (0, 0, text.width, text.height),
            width=2,
        )
        untoggled_hover = pg.Surface(text.size)
        pg.draw.rect(
            untoggled_hover,
            (255, 0, 0),
            (0, 0, text.width, text.height),
            width=2,
        )
        toggled = pg.Surface(text.size)
        toggled.fill((0, 0, 255))
        toggled_hover = pg.Surface(text.size)
        toggled_hover.fill((255, 0, 0))
        self._surfs = (untoggled, untoggled_hover, toggled, toggled_hover)

        toggled.blit(text, (0, 0))
        toggled_hover.blit(text, (0, 0))

    def handle_event(self: Self, event: pg.Event) -> None:
        if (event.type == pg.MOUSEBUTTONDOWN
            and self._rect.collidepoint(event.pos)):
                self._state = not self._state

    def update(self: Self,
               mouse_pos: Point,
               mouse_pressed: tuple[bool]) -> None:
        # slick boolean index
        collision = self._rect.collidepoint(mouse_pos)
        self._surf = self._surfs[collision]
        if self._state:
            self._surf = self._surfs[2 + collision]

class Input(_Widget): # Text Input
    def __init__(self: Self,
                 pos: Point,
                 width: int,
                 max_chars: int,
                 font: pg.Font) -> None:

        super().__init__(pos)
        self._width = width
        self._height = font.get_height()
        self._font = font
        self._max_chars = max_chars

        self._focused = 0
        self._cursor_pos = 0
        self._rect = pg.Rect(self._pos, (self._width, self._height))
        self.text = ''

    @property
    def surf(self: Self) -> None:
        surf = self._surf.copy()
        if self._focused:
            width = self._font.size(self._text[:self._cursor_pos])[0]
            pg.draw.rect(surf, (255, 255, 255), (width, 0, 1, self._height))
        return surf

    @property
    def text(self: Self) -> str:
        return self._text

    @text.setter
    def text(self: Self, value: str) -> None:
        self._text = value[:self._max_chars]
        self._cursor_pos = min(self._cursor_pos, len(value))
        text = self._font.render(self._text, 1, (255, 255, 255))
        self._surf = pg.Surface((self._width, self._height))
        self._surf.blit(text, (0, 0))
        pg.draw.rect(
            self._surf,
            (0, 0, 255),
            (0, 0, self._width, self._height),
            width=1,
        )

    @property
    def focused(self: Self) -> bool:
        return self._focused

    @focused.setter
    def focused(self: Self, value: bool) -> None:
        self._focused = value

    @property
    def cursor_pos(self: Self) -> int:
        return self._cursor_pos

    @cursor_pos.setter
    def cursor_pos(self: Self, value: int) -> None:
        self._cursor_pos = pg.math.clamp(self._cursor_pos, 0, len(self._text))

    def handle_event(self: Self, event: pg.Event) -> None:
        length = len(self._text)
        if event.type == pg.MOUSEBUTTONDOWN:
            collision = self._rect.collidepoint(event.pos)
            if collision: # calculate cursor pos
                x = event.pos[0] - self._pos[0]
                old = 0 # last width calculated
                for dex in range(len(self._text) + 1):
                    width = self._font.size(self._text[:dex])[0]
                    if old <= x < width:
                        # past middle it will go to dex
                        # before middile it will go to dex - 1
                        self._cursor_pos = dex - (x < (width + old) / 2)
                        break
                    old = width
                else:
                    self._cursor_pos = len(self._text)
            self._focused = collision
        if self._focused:
            if event.type == pg.TEXTINPUT:
                text = self._text[:self._cursor_pos] + event.text
                if self._cursor_pos < length:
                    text += self._text[self._cursor_pos:]
                self.text = text
                self._cursor_pos = min(self._cursor_pos + 1, self._max_chars)
            elif event.type == pg.KEYDOWN:
                ctrl = event.mod & pg.KMOD_CTRL
                # Terminal Keybindings
                if ((event.key == pg.K_h and ctrl)
                    or event.key == pg.K_BACKSPACE):
                    text = self._text[:self._cursor_pos - 1]
                    if self._cursor_pos < length:
                        text += self._text[self._cursor_pos:]
                        self._cursor_pos = max(self._cursor_pos - 1, 0)
                    self.text = text
                if ((event.key == pg.K_d and ctrl)
                    or event.key == pg.K_DELETE):
                    text = self._text[:self._cursor_pos]
                    if self._cursor_pos < length - 1:
                        text += self._text[self._cursor_pos + 1:]
                    self.text = text
                elif event.key == pg.K_u and event.mod & pg.KMOD_CTRL:
                    text = self._text[self._cursor_pos:]
                    self.text = text
                    self._cursor_pos = 0
                elif ((event.key == pg.K_b and ctrl)
                      or event.key == pg.K_LEFT):
                    self._cursor_pos = max(self._cursor_pos - 1, 0)
                elif ((event.key == pg.K_f and ctrl)
                      or event.key == pg.K_RIGHT):
                    self._cursor_pos = min(self._cursor_pos + 1, length)
                elif event.key == pg.K_a and ctrl:
                    self._cursor_pos = 0
                elif event.key == pg.K_e and ctrl:
                    self._cursor_pos = len(self._text)
                elif event.key == pg.K_ESCAPE:
                    self._focused = 0


class Panel(object):
    def __init__(self: Self, widgets: set[_Widget], min_scroll: Real) -> None:
        self._widgets = widgets
        self._scroll = 0
        self._min_scroll = min_scroll

    @property
    def focused(self: Self) -> bool:
        return any(
            isinstance(widget, Input)
            and widget._focused
            for widget in self._widgets
        )

    @property
    def widgets(self: Self) -> set[_Widget]:
        return self._widgets

    @widgets.setter
    def widgets(self: Self, value: set[_Widget]) -> None:
        self._widgets = value
    
    @property
    def scroll(self: Self) -> Real:
        return self._scroll

    @scroll.setter
    def scroll(self: Self, value: Real) -> None:
        self._scroll = pg.math.clamp(value, self._min_scroll, 0)
        for widget in self._widgets:
            widget.scroll = self._scroll

    def handle_event(self: Self, event: pg.Event) -> None:
        for widget in self._widgets:
            widget.handle_event(event)
        if event.type == pg.MOUSEWHEEL:
            self.scroll += event.precise_y * 10

    def update(self: Self,
               mouse_pos: Point,
               mouse_pressed: tuple[bool]) -> None:
        for widget in self._widgets:
            widget.update(mouse_pos, mouse_pressed)

    def render(self: Self, surf: pg.Surface) -> None:
        for widget in self._widgets:
            surf.blit(widget.surf, widget.pos)

