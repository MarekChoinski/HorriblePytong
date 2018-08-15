"""Class representing snake chracter."""
from enum import Enum


class Snake:
    """Object representing snake."""

    class Direction(Enum):
        """Enum of available directions of snake."""
        up = 1,
        down = 2,
        left = 3,
        right = 4

    def __init__(self, start_position, map_size):
        """Initializer of snake."""
        self._direction = Snake.Direction.up

        self.map_size = map_size

        # list of tuples of coordinates of position of each segment 
        self.body = []
        self.body.append(start_position)

        # points
        self.points = 0

    @property
    def direction(self):
        """Property representing actual direction of snake."""
        return self._direction
    
    @direction.setter
    def direction(self, value):
        """Setter of direction of snake.
        
            You can't move snake in backward direction unless snake lenght is 1.
        """
        if len(self.body) == 1:
            self._direction = value

        if value == Snake.Direction.up and self._direction == Snake.Direction.down:
            return
        elif value == Snake.Direction.down and self._direction == Snake.Direction.up:
            return
        elif value == Snake.Direction.left and self._direction == Snake.Direction.right:
            return
        elif value == Snake.Direction.right and self._direction == Snake.Direction.left:
            return
        else:
            self._direction = value
        

    def move(self):
        """Move snake accordingly to set direction."""
        first_y, first_x = self.body[0]

        # move head
        if self._direction == Snake.Direction.up:
            first_y, first_x = first_y-1, first_x
        elif self._direction == Snake.Direction.down:
            first_y, first_x = first_y+1, first_x
        elif self._direction == Snake.Direction.left:
            first_y, first_x = first_y, first_x-1
        elif self._direction == Snake.Direction.right:
            first_y, first_x = first_y, first_x+1
        else:
            raise ValueError("Unknown direction of snake!")

        # test edges of map
        if first_y < 0:
            first_y = self.map_size-1
        elif first_y == self.map_size:
            first_y = 0
        elif first_x < 0:
            first_x = self.map_size-1
        elif first_x == self.map_size:
            first_x = 0
        
        self.body.insert(0, (first_y, first_x))
        self.body.pop()

    def die(self):
        """Snake dies because of collision with wall"""
        self.body.clear()