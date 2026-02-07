import os
import sys
import platform
import math
import time
import copy
from typing import Self

import pygame as pg
from pygame.typing import Point

from panel import Surface
from panel import Label
from panel import Button
from panel import Toggle
from panel import Input
from panel import Panel


def gen_data_path(*args: str):
    if getattr(sys, "frozen", False):
        directory = sys.prefix
    else:
        directory = os.getcwd()
    return os.path.join(directory, 'data', *args)


class Game(object):

    _SCREEN_SIZE = (1080, 810)
    _SCREEN_FLAGS = pg.RESIZABLE | pg.SCALED
    _GAME_SPEED = 60

    def __init__(self: Self) -> None:
        pg.init()

        self._settings = {
            'vsync': 1,
        }
        self._screen = pg.display.set_mode(
            self._SCREEN_SIZE,
            flags=self._SCREEN_FLAGS,
            vsync=self._settings['vsync']
        )
        pg.display.set_caption('Coyote')
        self._running = 0

        pg.key.set_repeat(300, 75)

        self._FONTS = {
            'title': pg.font.SysFont('Andale Mono', 16),
            'main': pg.font.SysFont('Andale Mono', 16),
        }
        self._FONTS['title'].underline = 1

        self._COLORS = {
            'fill': (0, 0, 0),
            'point': (255, 255, 255),
            'selected': (255, 0, 255),
            'number': (0, 255, 0),
            'line': (255, 0, 0),
            'heading': (0, 255, 255),
            'robot': (0, 0, 255), # cannot be (0, 0, 0)
        }
        self._KEYS = {
            'mod': (
                pg.KMOD_META if platform.system() == 'Darwin'
                else pg.KMOD_CTRL
            ), 
            'mod2': pg.KMOD_SHIFT,
        }
        self._FIELD_SIZE = (144, 144)
        self._FIELD_IMAGE_SIZE = (self._SCREEN_SIZE[1], self._SCREEN_SIZE[1])
        self._robot_size = [16, 15.5]
        self._robot_rect_size = (
            self._robot_size[0]
            / self._FIELD_SIZE[0]
            * self._FIELD_IMAGE_SIZE[0],
            self._robot_size[1]
            / self._FIELD_SIZE[1]
            * self._FIELD_IMAGE_SIZE[1],
        )
        self._images = {
            'field': pg.transform.scale(
                pg.image.load(gen_data_path('field.png')).convert(),
                (self._SCREEN_SIZE[1], self._SCREEN_SIZE[1]),
            )
        }
        
        self._point_radius = 4
        self._point_select_radius = 8
        self._line_width = 2
        self._line_point_distance = 4 # point on a line that already exists
        self._heading_length = 24
        self._robot_line_width = 2
        self._field_pos_precision = 2
            
        # currently selected
        self._points = []
        self._screen_points = []
        self._clicking = -1
        self._selected = -1
        
        # History
        self._history = [copy.deepcopy(self._screen_points)] # screen points
        self._change = 0
        
        # Widgets
        self._widgets = {
            'robot': {
                'show': Toggle(
                    (self._FIELD_IMAGE_SIZE[0] + 60, 130),
                    font=self._FONTS['main'],
                ),
                'width': Input(
                    (self._FIELD_IMAGE_SIZE[0] + 60, 150),
                    width=200,
                    max_chars=25,
                    font=self._FONTS['main'],
                ),
                'length': Input(
                    (self._FIELD_IMAGE_SIZE[0] + 60, 170),
                    width=200,
                    max_chars=25,
                    font=self._FONTS['main'],
                ),
            },
            'point': {
                'x': Input(
                    (self._FIELD_IMAGE_SIZE[0] + 60, 230),
                    width=200,
                    max_chars=25,
                    font=self._FONTS['main'],
                ),
                'y': Input(
                    (self._FIELD_IMAGE_SIZE[0] + 60, 250),
                    width=200,
                    max_chars=25,
                    font=self._FONTS['main'],
                ),
                'heading': Input(
                    (self._FIELD_IMAGE_SIZE[0] + 60, 270),
                    width=200,
                    max_chars=25,
                    font=self._FONTS['main'],
                ),
            },
            'points': Label(
                (self._FIELD_IMAGE_SIZE[0] + 10, 330),
                text='',
                font=self._FONTS['main'],
            ),
        }
        self._widgets['robot']['show'].state = True
        self._widgets['robot']['length'].text = str(self._robot_size[0])
        self._widgets['robot']['width'].text = str(self._robot_size[1])
        self._panel = Panel(
            widgets={
                Label(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 10),
                    text='Path',
                    font=self._FONTS['title'],
                ),
                Button(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 30),
                    text='Clear',
                    func=self._clear_path,
                    font=self._FONTS['main'],
                ),
                Button(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 50),
                    text='Flip',
                    func=self._flip_path,
                    font=self._FONTS['main'],
                ),
                Button(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 70),
                    text='Copy code',
                    func=self._copy_code,
                    font=self._FONTS['main'],
                ),
                Label(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 110),
                    text='Robot Display',
                    font=self._FONTS['title'],
                ),
                Label(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 130),
                    text='Show',
                    font=self._FONTS['main'],
                ),
                self._widgets['robot']['show'],
                Label(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 150),
                    text='Widt',
                    font=self._FONTS['main'],
                ),
                self._widgets['robot']['width'],
                Label(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 170),
                    text='Leng',
                    font=self._FONTS['main'],
                ),
                self._widgets['robot']['length'],
                Label(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 210),
                    text='Point',
                    font=self._FONTS['title'],
                ),
                Label(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 230),
                    text='X',
                    font=self._FONTS['main'],
                ),
                self._widgets['point']['x'],
                Label(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 250),
                    text='Y',
                    font=self._FONTS['main'],
                ),
                self._widgets['point']['y'],
                Label(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 270),
                    text='Head',
                    font=self._FONTS['main'],
                ),
                self._widgets['point']['heading'],
                Label(
                    (self._FIELD_IMAGE_SIZE[0] + 10, 310),
                    text='Points',
                    font=self._FONTS['title'],
                ),
                self._widgets['points'],
            },
            min_scroll=-self._SCREEN_SIZE[1],
        )

    def _update_widgets(self: Self) -> None:
        text = ''
        for point in self._points:
            text += '['
            text += str(round(point[0][0], self._field_pos_precision))
            text += ', '
            text += str(round(point[0][1], self._field_pos_precision))
            text += ', '
            text += str(round(point[1], self._field_pos_precision))
            text += ']'
            text += '\n'
        self._widgets['points'].text = text
        
        if self._selected != -1:
            # I'm not sure if there's a better way
            x = self._widgets['point']['x']
            try:
                x = float(x.text)
            except:
                x = 0
            y = self._widgets['point']['y']
            try:
                y = float(y.text)
            except:
                y = 0
            self._points[self._selected][0] = (x, y)
            self._screen_points[self._selected] = self._gen_screen_pos((x, y))
            heading = self._widgets['point']['heading']
            try:
                heading = float(heading.text)
            except:
                heading = 0
            self._points[self._selected][1] = heading

        width = self._widgets['robot']['width']
        try:
            width = float(width.text)
        except:
            width = 18
        length = self._widgets['robot']['length']
        try:
            length = float(length.text)
        except:
            length = 18
        self._robot_size = (length, width)
        self._robot_rect_size = (
            self._robot_size[0]
            / self._FIELD_SIZE[0]
            * self._FIELD_IMAGE_SIZE[0],
            self._robot_size[1]
            / self._FIELD_SIZE[1]
            * self._FIELD_IMAGE_SIZE[1],
        )

    def _gen_field_pos(self: Self, screen_pos: Point) -> tuple:
        return (
            (screen_pos[0] - self._FIELD_IMAGE_SIZE[0] / 2)
            / self._FIELD_IMAGE_SIZE[0]
            * self._FIELD_SIZE[1],
            -(screen_pos[1] - self._FIELD_IMAGE_SIZE[1] / 2)
            / self._FIELD_IMAGE_SIZE[1]
            * self._FIELD_SIZE[1],
        )

    def _gen_screen_pos(self: Self, field_pos: Point) -> tuple:
        return pg.Vector2(
            (field_pos[0] / self._FIELD_SIZE[0] + 0.5)
            * self._FIELD_IMAGE_SIZE[0],
            (-field_pos[1] / self._FIELD_SIZE[1] + 0.5)
            * self._FIELD_IMAGE_SIZE[1],
        )

    def _set_point_widget(self: Self, point: list[Point, Real]) -> None:
        self._widgets['point']['x'].text = str(point[0][0])
        self._widgets['point']['y'].text = str(point[0][1])
        self._widgets['point']['heading'].text = str(point[1])

    def _set_point_widget_auto(self: Self, pos: Point) -> None:
        # auto means not using keyboard, which is manually
        # also this only accepts x and y not heading
        self._widgets['point']['x'].text = str(
            round(pos[0], self._field_pos_precision),
        )
        self._widgets['point']['y'].text = str(
            round(pos[1], self._field_pos_precision),
        )

    def _clear_path(self: Self) -> None:
        self._screen_points = []
        self._points = []
        self._clicking = self._selected = -1
        self._finish_change()

    def _flip_path(self: Self) -> None:
        for dex, point in enumerate(self._points):
            point[0] = (point[0][0], -point[0][1])
            point[1] = -point[1]
            if dex == self._selected:
                self._set_point_widget(point)
        for point in self._screen_points:
            point[1] = self._FIELD_IMAGE_SIZE[1] - point[1]
        self._finish_change()
        self._update_widgets()

    def _copy_code(self: Self) -> None:
        if self._points:
            with open(gen_data_path('code', 'start.txt')) as file:
                code = file.read().format(
                    self._points[0][0][0],
                    self._points[0][0][1],
                    self._points[0][1],
                )
            with open(gen_data_path('code', 'leg.txt')) as file:
                leg = file.read()
            for dex, point in enumerate(self._points[1:]):
                code += leg.format(point[0][0], point[0][1], point[1], dex)
            pg.scrap.put_text(code)
            pg.display.message_box('Code copied to clipboard', '')
            return None
        pg.display.message_box('No points set', '')

    def _finish_change(self: Self) -> None:
        if self._change < len(self._history) - 1:
            self._history = self._history[:self._change + 1]
        if self._history[-1] != self._points:
            self._change += 1
            self._history.append(copy.deepcopy(self._points))

    def run(self: Self) -> None:
        self._running = 1
        start_time = time.time()

        while self._running:
            delta_time = time.time() - start_time
            start_time = time.time()

            rel_game_speed = delta_time * self._GAME_SPEED

            for event in pg.event.get():
                self._panel.handle_event(event)
                if event.type == pg.QUIT:
                    self._running = 0
                elif (event.type == pg.MOUSEBUTTONDOWN
                      and event.pos[0] < self._FIELD_IMAGE_SIZE[0]):
                    # clicking - creating on a line - creating is priority
                    vector = pg.Vector2(event.pos)
                    for i in range(len(self._screen_points) - 1, -1, -1):
                        point = self._screen_points[i]
                        if (vector.distance_to(point)
                            <= self._point_select_radius):
                            self._clicking = self._selected = i
                            self._set_point_widget(self._points[i])
                            break
                    else:
                        for dex, point in enumerate(self._screen_points):
                            if not dex:
                                continue
                            # https://stackoverflow.com/a/1501725/24845999
                            # projects point onto line segment
                            # then calculates distance to that point
                            prev = self._screen_points[dex - 1]
                            difference = point - prev
                            t = pg.math.clamp(
                                difference.dot(vector - prev)
                                / difference.magnitude_squared(),
                                0, 1,
                            )
                            projection = prev + t * difference
                            distance = vector.distance_to(projection)
                            if distance <= self._line_point_distance:
                                self._clicking = self._selected = dex
                                self._screen_points.insert(dex, vector)
                                pos = self._gen_field_pos(event.pos)
                                self._points.insert(dex, [pos, 0])
                                break
                        else:
                            self._clicking = len(self._screen_points)
                            self._selected = self._clicking
                            self._screen_points.append(vector)
                            pos = self._gen_field_pos(event.pos)
                            self._points.append([pos, 0])
                        self._set_point_widget_auto(pos)
                        self._widgets['point']['heading'].text = '0'
                elif event.type == pg.MOUSEMOTION and self._clicking != -1:
                    new = self._screen_points[self._clicking] + event.rel
                    new[0] = pg.math.clamp(
                        new[0], 0, self._FIELD_IMAGE_SIZE[0],
                    )
                    new[1] = pg.math.clamp(
                        new[1], 0, self._FIELD_IMAGE_SIZE[1],
                    )
                    self._screen_points[self._clicking] = new
                    pos = self._gen_field_pos(new)
                    self._points[self._clicking][0] = pos
                    self._set_point_widget_auto(pos)
                elif event.type == pg.MOUSEBUTTONUP:
                    self._clicking = -1
                    self._finish_change()
                elif event.type == pg.KEYDOWN and not self._panel.focused:
                    if event.key == pg.K_BACKSPACE and self._selected != -1:
                        del self._screen_points[self._selected]
                        del self._points[self._selected]
                        self._clicking = self._selected = -1
                        self._finish_change()
                    elif event.key == pg.K_z and event.mod & self._KEYS['mod']:
                        if event.mod & self._KEYS['mod2']: # redo
                            self._change = min(
                                self._change + 1, len(self._history) - 1,
                            )
                        else: # undo
                            self._change = max(self._change - 1, 0)
                        self._points = copy.deepcopy(self._history[self._change])
                        self._screen_points = []
                        for point, heading in self._points:
                            self._screen_points.append(
                                self._gen_screen_pos(point)
                            )
                        self._clicking = self._selected = -1
                self._update_widgets()

            self._panel.update(pg.mouse.get_pos(), pg.mouse.get_pressed())
            
            # Draw Field
            self._screen.fill(self._COLORS['fill'])
            self._screen.blit(self._images['field'], (0, 0))
            # Draw Path
            if len(self._screen_points) > 1:
                pg.draw.aalines(
                    self._screen,
                    self._COLORS['line'],
                    0,
                    self._screen_points,
                    self._line_width,
                )
            for dex, point in enumerate(self._screen_points):
                heading = self._points[dex][1]
                color = (
                    self._COLORS['selected'] if dex == self._selected
                    else self._COLORS['point']
                )
                pg.draw.aacircle(
                    self._screen, color, point, self._point_radius,
                )
                if self._widgets['robot']['show'].state: # Drawing Robot
                    surf = pg.Surface(self._robot_rect_size)
                    surf.set_colorkey((0, 0, 0))
                    pg.draw.rect(
                        surf,
                        self._COLORS['robot'],
                        ((0, 0), self._robot_rect_size),
                        width=self._robot_line_width,
                    )
                    surf = pg.transform.rotate(surf, heading)
                    self._screen.blit(
                        surf,
                        (point[0] - surf.width / 2,
                         point[1] - surf.height / 2),
                    )
                self._screen.blit(
                    self._FONTS['main'].render(
                        str(dex),
                        1,
                        self._COLORS['number'],
                    ),
                    point,
                )
                angle = math.radians(heading)
                vector = (
                    pg.Vector2(math.cos(angle), -math.sin(angle))
                    * self._heading_length
                )
                pg.draw.aaline(
                    self._screen,
                    self._COLORS['heading'],
                    point,
                    point + vector,
                )

            # Draw Panel
            self._panel.render(self._screen)

            pg.display.update()

        pg.quit()


if __name__ == '__main__':
    Game().run()

