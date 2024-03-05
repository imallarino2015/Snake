##########################################
#   Ian Mallarino
#   08/09/2017
#
#   snake.py
#   A small game of snake to try to start
#   learning python
##########################################
# -*- coding: utf-8 -*-

import random  # for spawning the food
import tkinter as tk
import tkinter.messagebox


def key_press(app, event):
    """Event handler for the user's key presses"""
    if event.char == Controls.KEY_UP and app.snake.direction != "down":  # TODO: Find some way to clean up
        app.snake.direction_buffered = "up"
    if event.char == Controls.KEY_DOWN and app.snake.direction != "up":
        app.snake.direction_buffered = "down"
    if event.char == Controls.KEY_LEFT and app.snake.direction != "right":
        app.snake.direction_buffered = "left"
    if event.char == Controls.KEY_RIGHT and app.snake.direction != "left" and app.snake.direction is not None:
        app.snake.direction_buffered = "right"


class Cell(object):
    """Base class for a unit of space on the canvas"""
    def __init__(self, app, x: int, y: int, fill_color: str | None = None):
        """Creates a single square on a pre-defined grid"""
        self.app = app
        self.x, self.y = x, y
        self.height, self.width = self.app.height/self.app.resolution, self.app.width/self.app.resolution
        (x, y) = self.get_pos(x, y)
        self.rect = self.app.canvas.create_rectangle(x, y, x+self.width, y+self.height)

        if fill_color is not None:
            self.app.canvas.itemconfig(self.rect, fill=fill_color)

    def move(self, d_x, d_y):
        """Moves rectangle the designated number of units"""
        self.x += d_x
        self.y += d_y
        (d_x, d_y) = self.get_pos(d_x, d_y)
        self.app.canvas.move(self.rect, d_x, d_y)

    def get_pos(self, cell_x, cell_y):
        """Converts from the grid coordinates to the absolute number of pixels on the canvas"""
        return cell_x * self.width, cell_y * self.height

    def is_occupying(self, x, y):
        """Checks if the cell is occupying the given coordinates"""
        return x == self.x and y == self.y

    def __del__(self):
        self.app.canvas.delete(self.rect)


class SnakeSegment(Cell):
    """A single part of the snake"""
    def __init__(self, app, x: int | float, y: int | float):
        """Creates a piece of the snake"""
        super().__init__(app, x, y, "#FFFFFF")


class SnakeHead(SnakeSegment):
    direction_buffered = None
    direction = None

    """Front of the snake"""
    def __init__(self, app, start_length):
        """Sets the snake to the middle of the field and initializes the body list of segments"""
        self.app = app
        self.x = self.app.resolution / 2
        self.y = self.app.resolution / 2
        self.body = []
        self.start_length = start_length
        super().__init__(self.app, self.x, self.y)
        self.reset()

    def reset(self):
        """Puts the snake back to the starting position, sets it back to its starting size and resets the score"""
        self.direction_buffered = None
        self.direction = None

        del self.body[:]

        self.move(self.app.resolution/2-self.x, self.app.resolution/2-self.y)
        self.x = self.app.resolution/2
        self.y = self.app.resolution/2

        while len(self.body) < self.start_length:
            self.grow()

    def get_change(self):  # TODO: Add different multiples to scale up(?)
        """Gets the change to the x and y coordinates based on the direction of the snake"""
        if self.direction is None:
            return 0, 0
        if self.direction == "up":
            return 0, -1
        if self.direction == "down":
            return 0, 1
        if self.direction == "left":
            return -1, 0
        if self.direction == "right":
            return 1, 0

    def grow(self):
        """Increases the size of the snake by one segment"""
        if self.direction is None:
            if len(self.body) == 0:
                self.body.append(SnakeSegment(self.app, self.x+1, self.y))
            else:
                self.body.append(SnakeSegment(self.app, self.body[len(self.body)-1].x+1, self.body[len(self.body)-1].y))
        else:
            self.body.append(SnakeSegment(self.app, self.body[len(self.body)-1].x, self.body[len(self.body)-1].y))

    def body_occupies(self, x, y):
        """Checks if any part of the body lies on the given coordinates"""
        for body_part in self.body:
            if body_part.is_occupying(x, y):
                return True
        return False

    def move_snake(self):
        """Moves the snake toward the given direction"""
        if self.direction is not None:
            if len(self.body) > 0:
                for a in range(0, len(self.body)-1):
                    self.body[len(self.body)-1-a].move(
                        self.body[len(self.body)-2-a].x-self.body[len(self.body)-1-a].x,
                        self.body[len(self.body)-2-a].y-self.body[len(self.body)-1-a].y
                    )
                self.body[0].move(self.x-self.body[0].x, self.y-self.body[0].y)

        d_x, d_y = self.get_change()
        self.move(d_x, d_y)


class Food(Cell):
    """The items the player must collect to increase their snake's size and their score"""
    def __init__(self, app):
        """Creates a food item and sets it to a random location"""
        self.app = app
        self.x, self.y = self.get_coords()
        super().__init__(self.app, self.x, self.y, "green")

    def eat(self):
        """Removes the food, creates a new food, increases the player's score and increases the snake's size"""
        self.app.score += 1
        self.reset()
        self.app.snake.grow()

    def reset(self):
        """Removes the food and creates food in a different location"""
        x, y = self.get_coords()
        self.move(x-self.x, y-self.y)

    def get_coords(self):
        """Generates a random set of coordinates within the field and tests that it isn't occupied by the snake"""
        valid = [
            [
                (x, y)
                for y
                in range(self.app.resolution)
                if not self.app.snake.is_occupying(x, y)
                and not self.app.snake.body_occupies(x, y)
            ]
            for x
            in range(self.app.resolution)
        ]
        valid = sum(valid, [])
        return random.choice(valid)


class App(tk.Tk):
    DELAY: int = 50
    score: int = 0
    canvas: tk.Canvas = None
    snake: SnakeHead = None
    food: Food = None

    """Main window for the game"""
    def __init__(self, width, height, grid_resolution):
        """Opens a new window for the app"""
        super().__init__()

        self.width, self.height = width, height
        self.resolution = grid_resolution

        self.title("Snake")
        self.protocol('WM_DELETE_WINDOW', quit)
        self.geometry(f"{self.width}x{self.height}+100+100")
        self.resizable(width=False, height=False)

        self.bind("<Key>", lambda key: key_press(self, key))
        self.load_content()
        self.after(self.DELAY, self.update)

    def load_content(self):
        """Generates the content that belongs in the window"""
        self.score = 0
        self.canvas = tk.Canvas(self, bg="#000000")
        self.canvas.pack(fill="both", expand=True)
        self.snake = SnakeHead(self, 5)
        self.food = Food(self)

    def end_game(self):
        """Shows the player their score and resets the game"""
        tk.messagebox.showinfo("Game Over", f"Game Over\nYour score: {self.score}")
        self.snake.reset()
        self.score = 0

    def update(self):
        """Called continuously to move the snake and check for collisions"""
        # self.title(f"Snake - Score: {self.score}")
        self.snake.direction = self.snake.direction_buffered  # reduce the buffered inputs to the program's speed
        self.snake.move_snake()

        if self.snake.body_occupies(self.snake.x, self.snake.y):  # the snake crossed itself
            self.end_game()

        if (
            self.snake.x < 0 or self.snake.x >= self.resolution
                or self.snake.y < 0 or self.snake.y >= self.resolution
        ):  # out of bounds
            self.end_game()

        if self.snake.is_occupying(self.food.x, self.food.y):  # the snake ate food
            self.food.eat()

        if self.score == (self.resolution ** 2) - self.snake.start_length - 1:  # maximum length snake (win condition)
            tk.messagebox.showinfo(
                "Congratulations",
                f"Congratulations, you win\nYour score: {self.score}"
            )

        self.after(self.DELAY, self.update)  # call back the update function


class Controls:
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT = 'e', 'd', 's', 'f'  # 'esdf' directional keys
    KEY_START = ' '  # start is set to the space bar


def main():
    random.seed(a=None)

    app = App(640, 480, 100)
    app.mainloop()
    app.destroy()


if __name__ == "__main__":
    main()
