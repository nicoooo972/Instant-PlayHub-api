class ConnectFour:
    def __init__(self):
        self.board = [[' ' for _ in range(7)] for _ in range(6)]
        self.current_player = 'X'

    def drop_piece(self, column):
        if column < 0 or column >= 7 or self.board[0][column] != ' ':
            return False
        for row in reversed(self.board):
            if row[column] == ' ':
                row[column] = self.current_player
                return True
        return False

    def check_winner(self):
        for row in range(6):
            for col in range(7):
                if self.board[row][col] == self.current_player:
                    if self.check_direction(row, col, 1, 0) or \
                       self.check_direction(row, col, 0, 1) or \
                       self.check_direction(row, col, 1, 1) or \
                       self.check_direction(row, col, 1, -1):
                        return True
        return False

    def check_direction(self, row, col, row_dir, col_dir):
        count = 0
        for i in range(4):
            r, c = row + i * row_dir, col + i * col_dir
            if 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == self.current_player:
                count += 1
            else:
                break
        return count == 4

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def is_draw(self):
        return all(self.board[0][col] != ' ' for col in range(7))
