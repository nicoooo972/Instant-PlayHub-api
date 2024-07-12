# morpion/domain/board.py

class Board:
    def __init__(self):
        self.grid = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'

    def make_move(self, row, col):
        if self.grid[row][col] != '':  # Check if the cell is already occupied
            return False  # Return False if the cell is occupied
        self.grid[row][col] = self.current_player
        return True

    def check_winner(self):
        # Check rows, columns and diagonals
        lines = self.grid[:]
        lines.extend([list(col) for col in zip(*self.grid)])
        lines.append([self.grid[i][i] for i in range(3)])
        lines.append([self.grid[i][2-i] for i in range(3)])

        for line in lines:
            if line[0] == line[1] == line[2] != '':
                return line[0]
        return None

    def is_full(self):
        return all(cell != '' for row in self.grid for cell in row)

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def get_current_player(self):
        return self.current_player

    def reset_board(self):
        self.grid = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
