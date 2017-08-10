##########################################
#	Ian Mallarino
#	08/09/2017
#	
#	snake.py
#	A small game of snake to try to start
#	learning python
##########################################
# -*- coding: utf-8 -*-

print("Snake")

from random import *	#for spawning the food
seed(a=None)

from tkinter import *
from tkinter import messagebox	#for the end-of-game message boxes

DELAY=50
WIDTH=640
HEIGHT=480
RES=100
KEY_UP='w'
KEY_DOWN='s'
KEY_LEFT='a'
KEY_RIGHT='d'
KEY_START=' '	#start is set to the spacebar

class App(Frame):
	"""Main window for the game"""
	def __init__(self,master=None):
		"""Opens a new window for the app"""
		super(App,self).__init__()
		self.master.title("Snake")
		Frame.__init__(self,master)
		master.protocol('WM_DELETE_WINDOW',quit)
		master.geometry("%dx%d+100+100"%(WIDTH,HEIGHT))
		self.pack(fill="both",expand=True)
		self.master.resizable(width=False,height=False)
		master.bind("<Key>",keyPress)
		self.loadContent()
		self.after(DELAY,self.update)

	def loadContent(self):
		"""Generates the content that belongs in the window"""
		self.score=0
		self.canvas=Canvas(self,bg="black")
		self.canvas.pack(fill="both",expand=True)
		self.snake=SnakeHead(self.canvas,5)
		self.food=Food(self.snake,self.canvas)

	def endGame(self):
		"""Shows the player their score and resets the game"""
		messagebox.showinfo("Game Over","Game Over\nYour score: %d"%(self.score))
		self.snake.reset()
		self.score=0

	def update(self):
		"""Called continuously to move the snake and check for collisions"""
		self.snake.direction=self.snake.dir	#reduce the buffered inputs to the program's speed
		self.snake.moveSnake()
		
		if(self.snake.bodyOccupies(self.snake.x,self.snake.y)):	#the snake crossed itself
			self.endGame()

		if(self.snake.x<0 or self.snake.x>=RES or
			self.snake.y<0 or self.snake.y>=RES):	#out of bounds
			self.endGame()
			
		if(self.snake.isOccupying(self.food.x,self.food.y)):	#the snake ate food
			self.food.eat(self.snake)
		
		if(self.score==(RES*RES)-self.snake.startLength-1):	#maximum length snake (win condition)
			messagebox.showinfo("Congratulations","Congratulations, you win\nYour score: %d"%(self.score))
		
		self.after(DELAY,self.update)	#call back the update function

class Cell(object):
	"""Base class for a unit of space on the canvas"""
	def __init__(self,canvas,x,y):
		"""Creates a single square on a pre-defined grid"""
		self.x=x
		self.y=y
		self.height=HEIGHT/RES
		self.width=WIDTH/RES
		(x,y)=self.getPos(x,y)
		self.canvas=canvas
		self.rect=canvas.create_rectangle(x,y,x+self.width,y+self.height)
		canvas.itemconfig(self.rect,fill="blue")

	def move(self,dX,dY):
		"""Moves rectangle the designated number of units"""
		self.x+=dX
		self.y+=dY
		(dX,dY)=self.getPos(dX,dY)
		self.canvas.move(self.rect,dX,dY)

	def getPos(self,cellX,cellY):
		"""Converts from the grid coordinates to the absolute number of pixels on the canvas"""
		return(cellX*(WIDTH/RES),cellY*(HEIGHT/RES))

	def isOccupying(self,x,y):	#TODO: Check that there isn't a better way to implement
		"""Checks if the cell is occupyint the given coordinates"""
		if(x==self.x and y==self.y):
			return True
		else:
			return False

class SnakeSegment(Cell):
	"""A single part of the snake"""
	def __init__(self,canvas,x,y):
		"""Creates a piece of the snake"""
		super(SnakeSegment, self).__init__(canvas,x,y)
		canvas.itemconfig(self.rect,fill="white")

class SnakeHead(SnakeSegment):
	"""Front of the snake"""
	def __init__(self,canvas,length):
		"""Sets the snake to the middle of the field and initializes the body list of segments"""
		self.x=RES/2
		self.y=RES/2
		self.body=[]
		self.startLength=length
		super(SnakeHead, self).__init__(canvas,self.x,self.y)
		self.reset()

	def reset(self):
		"""Puts the snake back to the starting position, sets it back to its starting size and resets the score"""
		self.dir="none"
		self.direction="none"
		
		if(len(self.body)>0):
			for a in range(0,len(self.body)):
				self.canvas.delete(self.body[len(self.body)-1].rect)
				del self.body[len(self.body)-1]
		
		self.move(RES/2-self.x,RES/2-self.y)
		self.x=RES/2
		self.y=RES/2

		while(len(self.body)<self.startLength):
			self.grow()

	def getChange(self):	#TODO: Add different multiples to scale up(?)
		"""Gets the change to the x and y coordinates based on the direction of the snake"""
		if(self.direction=="none"):
			return(0,0)
		if(self.direction=="up"):
			return(0,-1)
		if(self.direction=="down"):
			return(0,1)
		if(self.direction=="left"):
			return(-1,0)
		if(self.direction=="right"):
			return(1,0)

	def grow(self):
		"""Increases the size of the snake by one segment"""
		if(self.direction=="none"):
			if(len(self.body)==0):
				self.body+=[SnakeSegment(self.canvas,self.x+1,self.y)]
			else:
				self.body+=[SnakeSegment(self.canvas,
					self.body[len(self.body)-1].x+1,
					self.body[len(self.body)-1].y)]
		else:
			self.body+=[SnakeSegment(self.canvas,
				self.body[len(self.body)-1].x,
				self.body[len(self.body)-1].y)]

	def bodyOccupies(self,x,y):
		"""Checks if any part of the body lies on the given coordinates"""
		for a in range(0,len(self.body)-1):
			if(self.body[a].isOccupying(x,y)):
				return True
		return False

	def moveSnake(self):
		"""Moves the snake toward the given direction"""
		if(self.direction!="none"):
			if(len(self.body)>0):
				for a in range(0,len(self.body)-1):
					self.body[len(self.body)-1-a].move(
						self.body[len(self.body)-2-a].x-self.body[len(self.body)-1-a].x,
						self.body[len(self.body)-2-a].y-self.body[len(self.body)-1-a].y)
				self.body[0].move(self.x-self.body[0].x,self.y-self.body[0].y)

		(dX,dY)=self.getChange()
		self.move(dX,dY)

class Food(Cell):
	"""The items the player must collect to increase their snake's size and their score"""
	def __init__(self,snake,canvas):
		"""Creates a food item and sets it to a random location"""
		(self.x,self.y)=self.getCoords(snake)
		self.canvas=canvas
		super(Food, self).__init__(canvas,self.x,self.y)
		canvas.itemconfig(self.rect,fill="green")

	def eat(self,snake):
		"""Removes the food, creates a new food, increases the player's score and increases the snake's size"""
		app.score+=1
		self.reset(snake)
		snake.grow()

	def reset(self,snake):
		"""Removes the food and creates food in a different location"""
		(x,y)=self.getCoords(snake)
		self.move(x-self.x,y-self.y)

	def getCoords(self,snake):
		"""Generates a random set of coordinates within the field and tests that it isn't occupied by the snake"""
		unoccupied=True
		while(True):
			x=randint(0,RES-1)
			y=randint(0,RES-1)
			
			if(snake.isOccupying(x,y)):
				unoccupied=False
			if(snake.bodyOccupies(x,y)):
				unoccupied=False
					
			if(unoccupied==True):
				return (x,y)

def keyPress(event):
	"""Event handler for the user's keypresses"""
	if(event.char==KEY_UP and app.snake.direction!="down"):	#TODO: Find some way to clean up
		app.snake.dir="up"
	if(event.char==KEY_DOWN and app.snake.direction!="up"):
		app.snake.dir="down"
	if(event.char==KEY_LEFT and app.snake.direction!="right"):
		app.snake.dir="left"
	if(event.char==KEY_RIGHT and app.snake.direction!="left" and app.snake.direction!="none"):
		app.snake.dir="right"

root=Tk()
app=App(master=root)
app.mainloop()
app.destroy()
