class Tictactoe:
    def __init__(self, cross_player: str, circle_player: str) -> None:
        self.cr = cross_player
        self.ci = circle_player
        self.board_list = ["▢"] * 9
        self.current_turn = self.cr  # Set the first turn to the cross player
        self.game_over = False

    def draw_board(self) -> str:
        board_str = ""
        for i in range(1, len(self.board_list) + 1):
            board_str += str(self.board_list[i - 1]) + " "
            if i % 3 == 0:
                board_str += "\n"
        return board_str

    def check_win(self, symbol: str) -> bool:
        for i in range(3):
            if (self.board_list[i * 3] == self.board_list[1 + i * 3] == self.board_list[2 + i * 3] == symbol or  # Rows
                self.board_list[i] == self.board_list[3 + i] == self.board_list[6 + i] == symbol):  # Columns
                return True
        if (self.board_list[0] == self.board_list[4] == self.board_list[8] == symbol or  # Diagonal 1
            self.board_list[2] == self.board_list[4] == self.board_list[6] == symbol):  # Diagonal 2
            return True
        return False

    def make_move(self, position: int, symbol: str) -> bool:
        if self.board_list[position] == "▢":
            self.board_list[position] = symbol
            return True
        return False

    def reset_game(self):
        self.board_list = ["▢"] * 9
        self.current_turn = self.cr  # Reset current turn to cross player
        self.game_over = False