# TODO possibly refactor this to some GUI system
import pygame

from data_classes.FigureActOptions import FigureActOptions
from game.Game import Game
from gui_widgets.field_widget import FieldWidget
from player.PlayerManager import PlayerManager

STEP_COLOR = (100, 155, 0)
ATTACK_COLOR = (230, 80, 0)
SELECT_COLOR = (120, 250, 120)
KERNEL_COLOR = (20, 60, 100)
KERNEL_RECTANGLE = (140, 80, 440, 440)
PLAYER_COLOR = ('white', 'black')


def font():
    return pygame.font.Font('freesansbold.ttf', 32)


def gui_log(func):
    def console_log(*args, **kwargs):
        print(f'Screen log: {func.__name__} with parameters: ', end='')
        print(args)
        return func(*args, **kwargs)

    return console_log


def get_players():
    my_player = PlayerManager.get_instance().my_player
    other_player = PlayerManager.get_instance().other_player
    return [my_player, other_player]


def screen_size():
    return pygame.display.get_surface().get_size()


def delete_top_text(screen):
    pygame.draw.rect(screen, (250, 250, 250), (0, 0, screen_size()[0], 80))


class Screen:
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Screen.__instance is None:
            Screen()
        return Screen.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Screen.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Screen.__instance = self
            self.__ready = False
            self.__fields = None
            self.__steps = None
            self.__attacks = None
            self.__current_text = None
            self.__waiting_for_opponent_text = None
            self.__opponents_turn_text = None
            self.__choose_figure_text = None
            self.__choose_action_text = None
            self.__won_text = None
            self.__lost_text = None
            self.__player_id = None

    @property
    def fields(self):
        return self.__fields

    @property
    def ready(self):
        return self.__ready

    def set_ready(self, ready):
        self.__ready = ready

    def init_fields(self):
        size = Game.get_instance().board.SIZE
        self.__fields = tuple(tuple(FieldWidget(x, y) for y in range(size)) for x in range(size))

    def set_acts(self, act_options: FigureActOptions):
        if act_options is not None:
            self.__steps = act_options.possible_steps
            self.__attacks = act_options.possible_attacks

    def setup_board(self, screen, player):
        self.set_ready(True)
        self.init_fields()
        pygame.draw.rect(screen, KERNEL_COLOR, KERNEL_RECTANGLE)
        self.__player_id = player.id
        self.player_color_text(screen)

    def setup_texts(self, screen):
        self.__waiting_for_opponent_text = font().render('Waiting for a worthy opponent', True, KERNEL_COLOR)
        self.__opponents_turn_text = font().render('Opponent\'s turn...', True, KERNEL_COLOR)
        self.__choose_figure_text = font().render('Choose a figure', True, KERNEL_COLOR)
        self.__choose_action_text = font().render('Move: green, Attack: red', True, KERNEL_COLOR)
        self.__won_text = font().render('You won!!! Next time won\'t be so easy!', True, KERNEL_COLOR)
        self.__lost_text = font().render('Run you fool!', True, KERNEL_COLOR)

    def update_text(self, screen, text, center):
        if self.__current_text is not text:
            if self.__current_text is not None:
                pygame.draw.rect(screen, (250, 250, 250), (0, 0, 720, 390))
                pygame.draw.rect(screen, KERNEL_COLOR, KERNEL_RECTANGLE)
                self.player_color_text(screen)
            self.__current_text = text
            text_rect = self.__current_text.get_rect()
            text_rect.center = center
            screen.blit(self.__current_text, text_rect)

    def player_color_text(self, screen):
        player_text = font().render(f'Your color is {PLAYER_COLOR[self.__player_id]}', True, KERNEL_COLOR)
        text_rect = player_text.get_rect()
        text_rect.center = (360, 65)
        screen.blit(player_text, text_rect)

    def update(self, screen, mouse):
        if self.__waiting_for_opponent_text is None:
            self.setup_texts(screen)

        X, Y = pygame.display.get_surface().get_size()
        if not self.ready:
            self.update_text(screen, self.__waiting_for_opponent_text, (X // 2, Y // 3))
            if get_players()[0] is not None and get_players()[1] is not None:
                self.setup_board(screen, get_players()[0])
        else:
            board = Game.get_instance().board
            if board.state.type_of_state() == 'lost_game':
                self.update_text(screen, self.__lost_text, (X // 2, 30))
            elif board.state.type_of_state() == 'won_game':
                self.update_text(screen, self.__won_text, (X // 2, 30))
            elif board.state.type_of_state() == 'frozen':
                X, Y = pygame.display.get_surface().get_size()
                self.update_text(screen, self.__opponents_turn_text, (X // 2, 30))

            board_fields = board.fields
            for x in range(len(board_fields)):
                for y in range(len(board_fields[0])):
                    self.fields[x][y].reset_color()
                    if board.state.type_of_state() == 'choosing_figure':
                        self.update_text(screen, self.__choose_figure_text, (X // 2, 30))
                        if self.fields[x][y].is_over(mouse):
                            self.fields[x][y].set_color(SELECT_COLOR)
                    if board.state.type_of_state() == 'choosing_destination':
                        self.update_text(screen, self.__choose_action_text, (X // 2, 30))
                        if self.__steps is not None and (x, y) in self.__steps:
                            self.fields[x][y].set_color(STEP_COLOR)
                        if self.__attacks is not None and (x, y) in self.__attacks:
                            self.fields[x][y].set_color(ATTACK_COLOR)
                    self.fields[x][y].draw(screen)
                    if board_fields[x][y].figure is not None:
                        self.fields[x][y].draw_figure(screen, board_fields[x][y].figure)
        pygame.display.update()

    def handle(self, events, pressed_keys):
        for ev in events:
            if ev.type == pygame.QUIT:
                return False
            # Handle mouse buttons
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for x in range(len(self.fields)):
                    for y in range(len(self.fields[0])):
                        if self.fields[x][y].is_over(ev.pos):
                            self.set_acts(Game.get_instance().board.field_clicked(x, y))
        return True
