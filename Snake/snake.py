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

random.seed(a=None)

WIDTH, HEIGHT = 640, 480  # window size
RES = 100
KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT = 'e', 'd', 's', 'f'  # 'esdf' directional keys
KEY_START = ' '     # start is set to the space bar


class App(tk.Frame):
    DELAY = 50
    score = 0
    canvas = None
    snake = None
    food = None

    """Main window for the game"""
    def __init__(self, master=None):
        """Opens a new window for the app"""
        super(App, self).__init__()
        self.master.title("Snake")
        tk.Frame.__init__(self, master)
        master.protocol('WM_DELETE_WINDOW', quit)
        master.geometry("%dx%d+100+100" % (WIDTH, HEIGHT))
        self.pack(fill="both", expand=True)
        self.master.resizable(width=False, height=False)
        master.bind("<Key>", lambda key: key_press(self, key))
        self.load_content()
        self.after(self.DELAY, self.update)

    def load_content(self):
        """Generates the content that belongs in the window"""
        self.score = 0
        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.snake = SnakeHead(self, 5)
        self.food = Food(self, self.snake, self.canvas)

    def end_game(self):
        """Shows the player their score and resets the game"""
        tk.messagebox.showinfo("Game Over", f"Game Over\nYour score: {self.score}")
        self.snake.reset()
        self.score = 0

    def update(self):
        """Called continuously to move the snake and check for collisions"""
        self.snake.direction = self.snake.direction_buffered  # reduce the buffered inputs to the program's speed
        self.snake.move_snake()

        if self.snake.body_occupies(self.snake.x, self.snake.y):  # the snake crossed itself
            self.end_game()

        if self.snake.x < 0 or self.snake.x >= RES or self.snake.y < 0 or self.snake.y >= RES:  # out of bounds
            self.end_game()

        if self.snake.is_occupying(self.food.x, self.food.y):  # the snake ate food
            self.food.eat(self.snake)

        if self.score == (RES*RES)-self.snake.startLength-1:  # maximum length snake (win condition)
            tk.messagebox.showinfo("Congratulations", f"Congratulations, you win\nYour score: {self.score}")

        self.after(self.DELAY, self.update)  # call back the update function


class Cell(object):
    """Base class for a unit of space on the canvas"""
    def __init__(self, app, x, y):
        """Creates a single square on a pre-defined grid"""
        self.x = x
        self.y = y
        self.height = HEIGHT/RES
        self.width = WIDTH/RES
        (x, y) = self.get_pos(x, y)
        self.app = app
        self.rect = self.app.canvas.create_rectangle(x, y, x+self.width, y+self.height)
        self.app.canvas.itemconfig(self.rect, fill="blue")

    def move(self, d_x, d_y):
        """Moves rectangle the designated number of units"""
        self.x += d_x
        self.y += d_y
        (d_x, d_y) = self.get_pos(d_x, d_y)
        self.app.canvas.move(self.rect, d_x, d_y)

    @staticmethod
    def get_pos(cell_x, cell_y):
        """Converts from the grid coordinates to the absolute number of pixels on the canvas"""
        return cell_x * (WIDTH / RES), cell_y * (HEIGHT / RES)

    def is_occupying(self, x, y):  # TODO: Check that there isn't a better way to implement
        """Checks if the cell is occupying the given coordinates"""
        if x == self.x and y == self.y:
            return True
        else:
            return False

    def __del__(self):
        self.app.canvas.delete(self.rect)


class SnakeSegment(Cell):
    """A single part of the snake"""
    def __init__(self, app, x, y):
        """Creates a piece of the snake"""
        super(SnakeSegment, self).__init__(app, x, y)
        app.canvas.itemconfig(self.rect, fill="white")


class SnakeHead(SnakeSegment):
    direction_buffered = None
    direction = None

    """Front of the snake"""
    def __init__(self, app, length):
        """Sets the snake to the middle of the field and initializes the body list of segments"""
        self.x = RES/2
        self.y = RES/2
        self.app = app
        self.body = []
        self.startLength = length
        super(SnakeHead, self).__init__(self.app, self.x, self.y)
        self.reset()

    def reset(self):
        """Puts the snake back to the starting position, sets it back to its starting size and resets the score"""
        self.direction_buffered = None
        self.direction = None

        del self.body[:]

        self.move(RES/2-self.x, RES/2-self.y)
        self.x = RES/2
        self.y = RES/2

        while len(self.body) < self.startLength:
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
                self.body.extend([SnakeSegment(self.app, self.x+1, self.y)])
            else:
                self.body.extend([SnakeSegment(
                    self.app,
                    self.body[len(self.body)-1].x+1,
                    self.body[len(self.body)-1].y
                )])
        else:
            self.body.extend([SnakeSegment(
                self.app,
                self.body[len(self.body)-1].x,
                self.body[len(self.body)-1].y
            )])

    def body_occupies(self, x, y):
        """Checks if any part of the body lies on the given coordinates"""
        for a in range(0, len(self.body)-1):
            if self.body[a].is_occupying(x, y):
                return True
        return False

    def move_snake(self):
        """Moves the snake toward the given direction"""
        if self.direction is not None:
            if len(self.body) > 0:
                for a in range(0, len(self.body)-1):
                    self.body[len(self.body)-1-a].move(
                        self.body[len(self.body)-2-a].x-self.body[len(self.body)-1-a].x,
                        self.body[len(self.body)-2-a].y-self.body[len(self.body)-1-a].y)
                self.body[0].move(self.x-self.body[0].x, self.y-self.body[0].y)

        d_x, d_y = self.get_change()
        self.move(d_x, d_y)


class Food(Cell):
    """The items the player must collect to increase their snake's size and their score"""
    def __init__(self, app, snake, canvas):
        """Creates a food item and sets it to a random location"""
        self.x, self.y = self.get_coords(snake)
        self.app = app
        self.canvas = canvas
        super(Food, self).__init__(self.app, self.x, self.y)
        canvas.itemconfig(self.rect, fill="green")

    def eat(self, snake):
        """Removes the food, creates a new food, increases the player's score and increases the snake's size"""
        self.app.score += 1
        self.reset(snake)
        snake.grow()

    def reset(self, snake):
        """Removes the food and creates food in a different location"""
        x, y = self.get_coords(snake)
        self.move(x-self.x, y-self.y)

    @staticmethod
    def get_coords(snake):
        """Generates a random set of coordinates within the field and tests that it isn't occupied by the snake"""
        while True:
            unoccupied = True
            x = random.randint(0, RES-1)
            y = random.randint(0, RES-1)

            if snake.is_occupying(x, y):
                unoccupied = False
            if snake.body_occupies(x, y):
                unoccupied = False

            if unoccupied:
                return x, y


def key_press(app, event):
    """Event handler for the user's key presses"""
    if event.char == KEY_UP and app.snake.direction != "down":  # TODO: Find some way to clean up
        app.snake.direction_buffered = "up"
    if event.char == KEY_DOWN and app.snake.direction != "up":
        app.snake.direction_buffered = "down"
    if event.char == KEY_LEFT and app.snake.direction != "right":
        app.snake.direction_buffered = "left"
    if event.char == KEY_RIGHT and app.snake.direction != "left" and app.snake.direction is not None:
        app.snake.direction_buffered = "right"


def main():
    root = tk.Tk()
    app = App(master=root)
    app.mainloop()
    app.destroy()


if __name__ == "__main__":
    main()
