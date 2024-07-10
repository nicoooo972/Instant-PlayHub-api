from breakout.domain.board import Board
from breakout.domain.paddle import Paddle
from breakout.domain.ball import Ball

class GameService:
    def __init__(self):
        self.board = Board()
        self.paddle1 = Paddle(x=100, y=450)
        self.paddle2 = Paddle(x=100, y=30)
        self.ball = Ball(x=150, y=200)

    def start_new_game(self):
        self.paddle1 = Paddle(x=100, y=450)
        self.paddle2 = Paddle(x=100, y=30)
        self.ball = Ball(x=150, y=200)

    def make_move(self, player, direction):
        if player == 'player1':
            if direction == 'left':
                self.paddle1.move_left()
            elif direction == 'right':
                self.paddle1.move_right(self.board.width)
        elif player == 'player2':
            if direction == 'left':
                self.paddle2.move_left()
            elif direction == 'right':
                self.paddle2.move_right(self.board.width)

    def update_ball(self):
        self.ball.move()

        # Check for wall collisions
        if self.ball.x - self.ball.radius < 0 or self.ball.x + self.ball.radius > self.board.width:
            self.ball.bounce_x()
        if self.ball.y - self.ball.radius < 0 or self.ball.y + self.ball.radius > self.board.height:
            self.ball.bounce_y()

        # Check for paddle collisions
        if (self.paddle1.y < self.ball.y + self.ball.radius < self.paddle1.y + self.paddle1.height and
                self.paddle1.x < self.ball.x < self.paddle1.x + self.paddle1.width):
            self.ball.bounce_y()
        if (self.paddle2.y < self.ball.y - self.ball.radius < self.paddle2.y + self.paddle2.height and
                self.paddle2.x < self.ball.x < self.paddle2.x + self.paddle2.width):
            self.ball.bounce_y()

    def get_game_state(self):
        return {
            'ball': {'x': self.ball.x, 'y': self.ball.y},
            'paddle1': {'x': self.paddle1.x, 'y': self.paddle1.y},
            'paddle2': {'x': self.paddle2.x, 'y': self.paddle2.y}
        }
