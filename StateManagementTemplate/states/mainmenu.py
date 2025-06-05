import pygame
import pygame.freetype
from states.state import State
from states.etkultspill import EtKultSpill
from states.mrpresident import MrPresident
from states.CatchTheFallingBlock import CatchTheFallingBlock
from states.SubToWaluigi import SubToWaluigi
# Importer flere states her etter hvert som du lager dem
# from states.annenstate import AnnenState

class Button:
    def __init__(self, rect, text, font, text_color=(255,255,255), color=(130,0,130), hover_color=(100,0,100)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface, selected=False):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)
        # Bruk hover_color hvis mus over ELLER hvis valgt med tastatur
        active = is_hover or selected
        pygame.draw.rect(surface, self.hover_color if active else self.color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)

class MainMenu(State):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.bg = pygame.image.load("StateManagementTemplate/assets/MainMenu_bg.png")
        self.bg = pygame.transform.scale(self.bg, (self.game.screen.get_width(), self.game.screen.get_height()))
        self.states = [
            ("MrPresident", MrPresident),
            ("CatchTheFallingBlock", CatchTheFallingBlock),
            ("SubToWaluigi", SubToWaluigi),
            ("EtKultSpill", EtKultSpill),
            # Legg til flere spill her!
        ]

        # Layout-innstillinger
        max_buttons_per_col = 5
        num_states = len(self.states)
        num_cols = max(1, (num_states + max_buttons_per_col - 1) // max_buttons_per_col)

        spacing_x = 30
        spacing_y = 10

        # Beregn knappbredde slik at alle kolonner får plass
        total_spacing_x = spacing_x * (num_cols - 1)
        button_width = min(200, (self.game.screen.get_width() - total_spacing_x) // num_cols)
        button_height = 60

        total_width = num_cols * button_width + total_spacing_x
        start_x = (self.game.screen.get_width() - total_width) // 2
        start_y = 100

        self.buttons = []
        for idx, (name, _) in enumerate(self.states):
            col = idx // max_buttons_per_col
            row = idx % max_buttons_per_col
            rect = (
                start_x + col * (button_width + spacing_x),
                start_y + row * (button_height + spacing_y),
                button_width,
                button_height
            )
            self.buttons.append(Button(rect, f"{name}", self.game.font))
        self.selected_index = 0

    def update(self, actions, dt):
        num_states = len(self.states)
        max_buttons_per_col = 5
        num_cols = max(1, (num_states + max_buttons_per_col - 1) // max_buttons_per_col)
        num_rows = max_buttons_per_col

        # Finn nåværende rad og kolonne
        col = self.selected_index // max_buttons_per_col
        row = self.selected_index % max_buttons_per_col

        # Finn antall rader i denne kolonnen
        def col_length(c):
            if c == num_cols - 1:
                # Siste kolonne kan ha færre knapper
                return num_states - c * max_buttons_per_col
            return max_buttons_per_col

        # Navigasjon ned
        if actions["down"].pressed:
            if row + 1 < col_length(col):
                row += 1
            else:
                row = 0  # Gå til toppen av kolonnen

        # Navigasjon opp
        if actions["up"].pressed:
            if row - 1 >= 0:
                row -= 1
            else:
                row = col_length(col) - 1  # Gå til bunnen av kolonnen

        # Navigasjon høyre
        if actions["right"].pressed and num_cols > 1:
            new_col = (col + 1) % num_cols
            # Juster rad hvis ny kolonne er kortere
            new_row = min(row, col_length(new_col) - 1)
            col, row = new_col, new_row

        # Navigasjon venstre
        if actions["left"].pressed and num_cols > 1:
            new_col = (col - 1) % num_cols
            new_row = min(row, col_length(new_col) - 1)
            col, row = new_col, new_row

        self.selected_index = col * max_buttons_per_col + row
        if self.selected_index >= num_states:
            self.selected_index = num_states - 1

        # ENTER: Velg valgt knapp
        if actions["return"].pressed:
            self.game.state = self.states[self.selected_index][1](self.game)

        # MUSEKLIKK: Sjekk om noen knapp er klikket
        for i, button in enumerate(self.buttons):
            if actions["leftmouse"].pressed and button.is_hovered():
                self.game.state = self.states[i][1](self.game)
                break

        # Hvis musen er over en knapp, marker den som valgt
        for i, button in enumerate(self.buttons):
            if button.is_hovered():
                self.selected_index = i
                break

        # Nullstill pressed-flagg
        actions["leftmouse"].pressed = False
        actions["up"].pressed = False
        actions["down"].pressed = False
        actions["left"].pressed = False
        actions["right"].pressed = False
        actions["return"].pressed = False

    def render(self, display):
        self.game.screen.blit(self.bg, (0, 0))
        for i, button in enumerate(self.buttons):
            if i == self.selected_index:
                pygame.draw.rect(display, (255,255,0), button.rect.inflate(8,8), 4)  # Gul ramme
            button.draw(display, i == self.selected_index)
