class Paddle:
    def __init__(self, x, y, width=100, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def move_left(self):
        self.x -= 20

    def move_right(self, board_width):
        if self.x + self.width < board_width:
            self.x += 20
