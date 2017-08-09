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

from random import *
seed(a=None)

from tkinter import *
from tkinter import messagebox

DELAY=50
WIDTH=640
HEIGHT=480
RES=100
KEY_UP='w'
KEY_DOWN='s'
KEY_LEFT='a'
KEY_RIGHT='d'
KEY_START=' '

class App(Frame):
	def __init__(self,master=None):
		super(App,self).__init__()
		self.master.title("Snake")
		Frame.__init__(self,master)
		master.protocol('WM_DELETE_WINDOW',quit)
		master.geometry("%dx%d+100+100"%(WIDTH,HEIGHT))
		self.pack(fill="both",expand=True)
		self.master.resizable(width=False,height=False)
		master.bind("<Key>",SnakeHead.keyPress)
		self.loadContent()
		self.after(DELAY,self.update)
		return

	def loadContent(self):
		self.score=0
		self.canvas=Canvas(self,bg="black")
		self.canvas.pack(fill="both",expand=True)
		self.snake=SnakeHead(self.canvas,5)
		self.food=Food(self.snake,self.canvas)
		return
		
	def endGame(self):
		messagebox.showinfo("Game Over","Game Over\nYour score: %d"%(self.score))
		self.snake.reset()
		self.score=0
		return
	
	def update(self):
		self.snake.direction=self.snake.dir	#reduce the buffered inputs to the program's speed
		self.snake.moveSnake()
		
		for a in range(0,len(self.snake.body)-1):	#the snake crossed itself
			if(self.snake.body[a].isOccupying(self.snake.x,self.snake.y)):
				self.endGame()
				break

		if(self.snake.x<0 or self.snake.x>=RES or
			self.snake.y<0 or self.snake.y>=RES):	#out of bounds
			self.endGame()
			
		if(self.snake.isOccupying(self.food.x,self.food.y)):	#the snake ate food
			self.food.eat(self.snake)
		
		if(self.score==
			(RES*RES)-self.snake.startLength-1):	#maximum length snake (win condition)
			messagebox.showinfo("Congratulations",
				"Congratulations, you win\nYour score: %d"%(self.score))
		
		self.after(DELAY,self.update)	#call back the update function
		return

class Cell(object):
	def __init__(self,canvas,x,y):
		self.x=x
		self.y=y
		self.height=HEIGHT/RES
		self.width=WIDTH/RES
		(x,y)=self.getPos(x,y)
		self.canvas=canvas
		self.color="blue"
		self.rect=canvas.create_rectangle(x,y,x+self.width,y+self.height)
		canvas.itemconfig(self.rect,fill=self.color)
		return
		
	def move(self,dX,dY):
		self.x+=dX
		self.y+=dY
		(dX,dY)=self.getPos(dX,dY)
		self.canvas.move(self.rect,dX,dY)
		return
		
	def getPos(self,cellX,cellY):
		return(cellX*(WIDTH/RES),cellY*(HEIGHT/RES))
		
	def isOccupying(self,x,y):
		if(x==self.x and y==self.y):
			return True
		else:
			return False
		
class SnakeSegment(Cell):
	def __init__(self,canvas,x,y):
		super(SnakeSegment, self).__init__(canvas,x,y)
		self.color="white"
		canvas.itemconfig(self.rect,fill=self.color)
		return

class SnakeHead(SnakeSegment):
	def __init__(self,canvas,length):
		self.x=RES/2
		self.y=RES/2
		self.body=[]
		self.startLength=length
		super(SnakeHead, self).__init__(canvas,self.x,self.y)
		self.reset()
		return

	def reset(self):
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
		
		return
		
	def grow(self):
		dX=0
		dY=0
		if(self.direction=="up"):
			dX=0
			dY=1
		if(self.direction=="down"):
			dX=0
			dY=-1
		if(self.direction=="left" or self.direction=="none"):
			dX=1
			dY=0
		if(self.direction=="right"):
			dX=-1
			dY=0

		if(len(self.body)==0):
			self.body+=[SnakeSegment(self.canvas,self.x+1,self.y)]
		else:
			self.body+=[SnakeSegment(self.canvas,
				self.body[len(self.body)-1].x+dX,
				self.body[len(self.body)-1].y+dY)]
		return

	def moveSnake(self):
		if(self.direction!="none"):
			if(len(self.body)>0):
				for a in range(0,len(self.body)-1):
					self.body[len(self.body)-1-a].move(
						self.body[len(self.body)-1-a-1].x-self.body[len(self.body)-1-a].x,
						self.body[len(self.body)-1-a-1].y-self.body[len(self.body)-1-a].y
					)
				
			self.body[0].move(self.x-self.body[0].x,self.y-self.body[0].y)

		if(self.direction=="up"):
			self.move(0,-1)
			return
		if(self.direction=="down"):
			self.move(0,1)
			return
		if(self.direction=="left"):
			self.move(-1,0)
			return
		if(self.direction=="right"):
			self.move(1,0)
			return

	def keyPress(event):
		if(event.char==KEY_UP and app.snake.direction!="down"):
			app.snake.dir="up"
		if(event.char==KEY_DOWN and app.snake.direction!="up"):
			app.snake.dir="down"
		if(event.char==KEY_LEFT and app.snake.direction!="right"):
			app.snake.dir="left"
		if(event.char==KEY_RIGHT and app.snake.direction!="left" and app.snake.direction!="none"):
			app.snake.dir="right"

class Food(Cell):
	def __init__(self,snake,canvas):
		self.x=0
		self.y=0
		self.canvas=canvas
		self.consumption=0
		super(Food, self).__init__(canvas,self.x,self.y)
		self.reset(snake)
		self.color="green"
		canvas.itemconfig(self.rect,fill=self.color)
		return
		
	def eat(self,snake):
		app.score+=1
		self.reset(snake)
		snake.grow()
		return
		
	def reset(self,snake):
		(x,y)=self.getCoords(snake)
		self.move(x-self.x,y-self.y)
		return
		
	def getCoords(self,snake):
		unoccupied=True
		while(True):
			x=randint(0,RES-1)
			y=randint(0,RES-1)
			
			if(snake.isOccupying(x,y)):
				unoccupied=False
			
			for a in range(0,len(snake.body)):
				if(snake.body[a].isOccupying(x,y)):
					unoccupied=False
					
			if(unoccupied==True):
				return (x,y)

root=Tk()
app=App(master=root)
app.mainloop()
app.destroy()