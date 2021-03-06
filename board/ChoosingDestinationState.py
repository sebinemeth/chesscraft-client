from board.AbstractBoardState import AbstractBoardState
from data_classes.FigureActOptions import FigureActOptions
from enums.FieldOccupation import FieldOccupation
from figure.King import King
from figure.Queen import Queen
from figure.Peasant import Peasant
from player.AIPlayer import AIPlayer
from player.PlayerManager import PlayerManager


class ChoosingDestinationState(AbstractBoardState):
    """ Handles simple moving/attacking. """

    def __init__(self, board):
        super(AbstractBoardState, self).__init__()
        self._board = board
        self.__possible_steps = []
        self.__possible_attacks = []
        self.__chosen_x = -1
        self.__chosen_y = -1

    def reset(self, **messages):
        self.__possible_steps = messages["possible_steps"]
        self.__possible_attacks = messages["possible_attacks"]
        self.__chosen_x = messages["chosen_x"]
        self.__chosen_y = messages["chosen_y"]
        self._board.chosen_field = self.field_xy(messages["chosen_x"], messages["chosen_y"])
        self._board.acts = FigureActOptions(True, messages["possible_steps"], messages["possible_attacks"])

    def change_to_queen(self):
        for row in self._board.fields:
            for f in row:
                if f.figure is not None and isinstance(f.figure, Peasant) and (f.x == 0 or f.x == 7):
                    f.add_figure(Queen(f.figure.owner))  # occupy new field
                    # abandon old field

    def field_clicked(self, x: int, y: int):
        chosen_field = self.field_xy(self.__chosen_x, self.__chosen_y)
        clicked_field = self.field_xy(x, y)
        occupation = clicked_field.get_occupation_type(PlayerManager.get_instance().my_player)
        chosen_fig = chosen_field.figure
        action_successful = False
        f = None
        if occupation == FieldOccupation.EMPTY and (x, y) in self.__possible_steps:  # step
            chosen_field.figure.has_not_moved_yet = False
            clicked_field.add_figure(chosen_fig)  # occupy new field
            chosen_field.remove_figure()  # abandon old field
            action_successful = True

        elif occupation == FieldOccupation.ENEMY and (x, y) in self.__possible_attacks:  # attack
            chosen_field.figure.has_not_moved_yet = False
            f = clicked_field.remove_figure()  # killing figure there
            clicked_field.add_figure(chosen_fig)  # occupy new field
            chosen_field.remove_figure()  # abandon old field
            action_successful = True

        if action_successful:
            self._board.transition_to(self._board.frozen_state)
            self.change_to_queen()
            if isinstance(PlayerManager.get_instance().other_player, AIPlayer):
                PlayerManager.get_instance().other_player.turn_started(self._board)
        else:
            self._board.transition_to(self._board.choosing_acting_figure_state)
        if f is not None and isinstance(f, King):
            print("shit happens")
            self._board.transition_to(self._board.won_game)
        return None

    def type_of_state(self):
        return "choosing_destination"
