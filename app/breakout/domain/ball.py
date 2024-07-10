class Ball:
    def __init__(self, x, y, dx=2, dy=-2, radius=10):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = radius

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def bounce_x(self):
        self.dx = -self.dx

    def bounce_y(self):
        self.dy = -self.dy
