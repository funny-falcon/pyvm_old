#
#
# Found at comp.lang.python
#
# you are supposed to pretend that you are playing this game while in reality you are
# testing that Tkinter works.
#

from math import sin
from Tkinter import *
from math import *

class Hammurabi:
        def __init__(self,parent):
		
            self.frame=Frame(parent)
            self.year=0
            self.work=0
            self.food=100
            self.population=100
            self.starve=0
            self.title=Label(self.frame,text="Hammurabi's House of Whores")
            self.title.grid(column=0,row=0)
            self.titlespacer=Label(self.frame,text="Year")
            self.titlespacer.grid(column=1,row=0)
            self.yearLabel=Label(self.frame,text="0")
            self.yearLabel.grid(column=2,row=0)
            self.peasantsLabel=Label(self.frame,text="Peasants")
            self.peasantsLabel.grid(column=1,row=2)
            self.peasantsData=Label(self.frame,text="100")
            self.peasantsData.grid(column=2,row=2)
            self.foodLabel=Label(self.frame,text="Food")
            self.foodLabel.grid(column=1,row=3)
            self.foodData=Label(self.frame,text="100")
            self.foodData.grid(column=2,row=3)
            self.workLabel=Label(self.frame,text="Work towards garden")
            self.workLabel.grid(column=1,row=4)
            self.workData=Label(self.frame,text="0")
            self.workData.grid(column=2,row=4)
            self.go=Button(self.frame,command=self.update,text="Go to next year")
            self.go.configure(bg="green")
            self.go.grid(row=8,column=2)
            self.peopleFood=Scale(self.frame,command=self.wackySliders)
            self.peopleFood.grid(row=7,column=0)
            self.peopleFoodLabel=Label(self.frame,text="Food")
            self.peopleFoodLabel.grid(column=0,row=6)
            self.peopleWork=Scale(self.frame,command=self.wackySliders)
            self.peopleWork.grid(row=7,column=1)
            self.peopleWorkLabel=Label(self.frame,text="Work")
            self.peopleWorkLabel.grid(column=1,row=6)
            self.peopleBaby=Scale(self.frame,command=self.wackySliders)
            self.peopleBaby.configure(to=25)
            self.peopleBaby.grid(row=7,column=2)
            self.peopleBabyLabel=Label(self.frame,text="Babies")
            self.peopleBabyLabel.grid(column=2,row=6)
            self.status=Label(self.frame,text="")
            self.status.grid(row=8,column=1)
            self.frame.pack()
        def update(self):
		self.status.configure(text="")
		
		if ((self.peopleFood.get()+self.peopleBaby.get()+self.peopleWork.get())<self.population):
			self.status.configure(text="You are not using all your people!")
		if (self.starve>=3):
			self.status.configure(text="For starving the people, you have been killed")
			self.work=0
			self.population=0
			self.food=0
			self.go.configure(bg="red")
		if (self.year%15==13):
			self.status.configure(text="There was a flood.  50 people died")
			self.population-=50
		self.year=self.year+1
		self.work=self.work+self.peopleWork.get()
		self.population=int(self.population*0.95+self.peopleBaby.get()/2)
		self.food=2*self.peopleFood.get()+0.5*self.food

		if (self.food>self.population):
			self.food=self.food-self.population
			self.starve=0
		else:
			self.population=self.food
			self.food=0
			self.starve=self.starve+1
		self.yearLabel.configure(text=self.year)
		self.foodData.configure(text=self.food)
		self.peasantsData.configure(text=self.population)
		self.workData.configure(text=self.work)
		if (self.work>=1000):
			self.status.configure(text=("Game won in the year "+to_string(self.year)))
			self.population=0
			self.work=0
			self.food=0
			self.go.configure(bg="red")
		self.wackySliders(self)
		
	def wackySliders(self,hmm):
		self.peopleFood.configure(to=self.population-self.peopleWork.get()-self.peopleBaby.get())
		self.peopleWork.configure(to=self.population-self.peopleFood.get()-self.peopleBaby.get())
		self.peopleBaby.configure(to=self.population-self.peopleWork.get()-self.peopleFood.get())

def to_string(in_int):
    out_str = ""
    prefix = ""
    if in_int < 0:
        prefix = "-"
        in_int = -in_int        
    while in_int / 10 != 0:
        out_str = chr(ord('0')+in_int % 10) + out_str
        in_int = in_int / 10
    out_str = chr(ord('0')+in_int % 10) + out_str
    return prefix + out_str

root=Tk()
hammurabi=Hammurabi(root)
root.mainloop()
