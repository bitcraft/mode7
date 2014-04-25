"""
fake perspective tricks using rotozoom and scale
"""

import pygame
from pygame.locals import *
from pygame.transform import smoothscale, rotozoom, flip

ROTATION_SPEED = 100
PERSPECTIVE_SPEED = .35
ZOOM_SPEED = 2


def init_screen(width, height):
    return pygame.display.set_mode((width, height), pygame.RESIZABLE)


class Mode7(object):
    def __init__(self, filename):
        self.original = pygame.image.load(filename).convert_alpha()
        self._perspective = 0
        self._rotation = 0
        self._zoom = 1
        self._dirty = 1

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        if value > 0:
            if not value == self._zoom:
                self._dirty = 1
                self._zoom = value
        else:
            raise ValueError

    @property
    def perspective(self):
        return self._perspective

    @perspective.setter
    def perspective(self, value):
        if 1 > value > 0:
            if not value == self._perspective:
                self._dirty = 1
                self._perspective = value
        else:
            raise ValueError

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if not value == self._rotation:
            self._dirty = 1
            self._rotation = value % 360

    @property
    def image(self):
        if self._dirty:
            self._image = self.render()
        return self._image

    @property
    def size(self):
        return self.original.get_size()

    def render(self):
        image = rotozoom(self.original, self._rotation, self._zoom)
        w2, h2 = image.get_size()
        image = smoothscale(image, (w2, int(h2*self._perspective)))
        return image


class SimpleTest(object):
    def __init__(self, filename):
        self.running = False
        self.dirty = False
        self.exit_status = 0
        self.renderer = Mode7(filename)

        self._r = 0
        self._p = .5
        self._z = 1
        self.r_velocity = 0
        self.p_velocity = 0
        self.z_velocity = 0

    def draw(self, surface):
        surface.fill((0,0,0))
        rect = self.renderer.image.get_rect()
        rect.center = surface.get_rect().center
        surface.blit(self.renderer.image, rect)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.exit_status = 0
                self.running = False

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.exit_status = 0
                    self.running = False

            elif event.type == VIDEORESIZE:
                init_screen(event.w, event.h)
                self.dirty = True

        pressed = pygame.key.get_pressed()
        if pressed[K_UP]:
            self.p_velocity = -PERSPECTIVE_SPEED
        elif pressed[K_DOWN]:
            self.p_velocity = PERSPECTIVE_SPEED
        else:
            self.p_velocity = 0

        if pressed[K_LEFT]:
            self.r_velocity = ROTATION_SPEED
        elif pressed[K_RIGHT]:
            self.r_velocity = -ROTATION_SPEED
        else:
            self.r_velocity = 0

        if pressed[K_z]:
            self.z_velocity = ZOOM_SPEED
        elif pressed[K_x]:
            self.z_velocity = -ZOOM_SPEED
        else:
            self.z_velocity = 0

    def update(self, dt):
        p = self._p + self.p_velocity * dt
        try:
            self.renderer.perspective = p
        except ValueError:
            pass
        else:
            self._p = p

        self._z += self.z_velocity * dt
        self._r += self.r_velocity * dt
        self.renderer.rotation = self._r
        self.renderer.zoom = self._z

    def run(self):
        clock = pygame.time.Clock()
        fps = 60
        self.running = True
        self.exit_status = 1
        while self.running:
            dt = clock.tick(fps) / 1000.
            self.handle_input()
            self.update(dt)
            self.draw(screen)
            pygame.display.flip()

        return self.exit_status

if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    screen = init_screen(600, 600)
    pygame.display.set_caption('Mode7')

    filename = 'pygame_logo_med.png'

    try:
        SimpleTest(filename).run()
    except:
        pygame.quit()
        raise