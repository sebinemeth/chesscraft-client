from board.AbstractBoardState import AbstractBoardState
from player.PlayerManager import PlayerManager
from enums.FieldOccupation import FieldOccupation


class LostGameState(AbstractBoardState):
    def field_clicked(self, x: int, y: int):
        pass

    def type_of_state(self):
        return 'lost_game'

