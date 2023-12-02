from classes.util import *
from classes.abstract import Controler


class ManualControler(Controler):

    def __init__(self):
        super().__init__()

    def compute_action(self, grid: Array2D[Cell], snake: List[Vector2], apple: Vector2) -> Action:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            return Action.UP
        if keys[pygame.K_s]:
            return Action.DOWN
        if keys[pygame.K_a]:
            return Action.LEFT
        if keys[pygame.K_d]:
            return Action.RIGHT
        
        return Action.NONE
