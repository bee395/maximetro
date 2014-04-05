#!/usr/bin/python

import pygame
from pygame.locals import *
import Vec2D
from Vec2D import *
import random

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
MAGENTA = (255,0,255)
CYAN = (0,255,255)
YELLOW = (255,255,0)

MAXSTATIONS = 8

MAX_X = MAX_Y = 500

LINES = [YELLOW,MAGENTA,CYAN,GREEN,BLUE,RED]

CARWITH = 10     # actually half of it
CARLENGTH = 20   # actually half of it
CARSPEED = 3

STATIONSIZE = 17
STATIONTHICKNESS = 5
STATIONDISTANCE = CARLENGTH * 4

FPS = 30

screen = pygame.display.set_mode((MAX_X, MAX_Y))


class Car():
	"""A railcar. Each track holds at least one"""
	
	def __init__(self,track):
		self.track = track
		self.pos = track.startpos
		self.direction = 1
		self.counter = 0
		self.poly = ((-CARWITH,-CARLENGTH),(-CARWITH,CARLENGTH),
		   			 (CARWITH,CARLENGTH),(CARWITH,-CARLENGTH))
			
	def move(self):
		"""returns the moved polygon to self.pos with angle of self.track"""

		ret = []
		pol = self.poly

		# determine angle of track 
		start = self.track.startpos
		end = self.track.endpos
		v = Vec2d(start[0]-end[0],start[1]-end[1])
		angle = v.get_angle() + 90
		
		# turn around
		turnedpol = []
		for p in pol:
			v = Vec2d(p)
			turnedpol.append(v.rotated(angle))
		
		# move to self.pos
		for p in turnedpol:
			ret.append([p[0] + self.pos[0], p[1] + self.pos[1]])
		
		return ret
			
	
	def draw(self):
		"""draw the car."""

		moved = self.move()
		pygame.draw.polygon(screen,self.track.color,moved,0)
		# pygame.draw.aalines(screen,BLUE,False,moved,5)


class Track():
	"""A railtrack between stations. Holds at minimum one Car"""
	
	def __init__(self,start,end,color,line,withcar=1):
		"""constructor should only be called, if LINES[] is not empty"""
		# self.pos_in_line = pil
		self.line = line
		self.color = color
		self.startpos = start
		self.endpos = end
		self.cars = []
		if withcar:
			self.cars.append(Car(self))
			
		
	def draw(self):
		pygame.draw.line(screen,self.color,self.startpos,self.endpos,5)
		for c in self.cars:
			c.draw()
			
	def update(self):
		for c in self.cars:
			c.update()

	def length(self):
		"""returns the length of the track"""
		
		#TODO: calculate only once if track changes
		start = self.startpos
		end = self.endpos
		return ( (start[0]-end[0])**2 + (start[1]-end[1])**2 ) ** .5
		
	def get_newpos(self,pos,count,direction=1):
		""" calculates new position of a car in direction. 
		direction should be 1 or -1"""
		
		start = self.startpos
		end = self.endpos
		ret = [0,0]
		length = self.length()
		xdiff = (start[0] - end[0]) / length * CARSPEED * -1
		ydiff = (start[1] - end[1]) / length * CARSPEED * -1
		if direction > 0:
			ret[0] = int(xdiff * count) + start[0]
			ret[1] = int(ydiff * count) + start[1]
		else:
			ret[0] = end[0] - int(xdiff * count)
			ret[1] = end[1] - int(ydiff * count)
		return ret
		
	def is_end(self,pos):
		"""returns True if pos is not on track"""
	
		start = self.startpos
		end = self.endpos
		x_range = [start[0],end[0]]
		y_range = [start[1],end[1]]
		x_range.sort()
		y_range.sort()
		if (x_range[0] <= pos[0] <= x_range[1] and 
		   y_range[0] <= pos[1] <= y_range[1]):
			return False
		return True
		
#	def remove_car(self,car):
#		for c in self.cars:
#			if c == car:
#				
#				print "REMOVE!"
		
		
	def add_car(self,car):
		car.track = self
		self.cars.append(car)
	
		

class Line():
	"""A line contains multiple tracks between stations"""
	
	def __init__(self,start,end):
		self.color = LINES[-1]
		self.tracks = []
		self.tracks.append(Track(start,end,self.color,self))
		
	def is_circle(self):
		if self.tracks[0].startpos == self.tracks[-1].endpos:
			return True
		return False
		
	def update(self):
		for t in self.tracks:
			if t.cars:
				for c in t.cars:
					self.update_car(t,c)

	def update_car(self,track,car):
		"""calculate new position of cars"""
	
		car.pos = track.get_newpos(car.pos,car.counter,car.direction)

		if track.is_end(car.pos):
			pil = self.tracks.index(track)
			line = track.line
			
			next_pil = pil + car.direction
			if next_pil < 0 or next_pil > len(self.tracks)-1:
				if self.is_circle():
					next_pil = (car.direction -1) / 2
				else:
					car.direction *= -1
					next_pil = pil
					print "NEW DIRECTION: ", car.direction
				
			next_track = self.tracks[next_pil]
							
			track.cars.remove(car)
			next_track.add_car(car)
			car.counter = 0

		car.counter += 1
		
		
	def draw(self):
		for t in self.tracks:
			t.draw()


class Station():
	"""a station"""

	def __init__(self,pos,shape='circle'):
		self.shape = shape
		self.pos = pos
		
	def draw(self):
		size = 20
		pos = self.pos

		if self.shape == 'circle':
			pygame.draw.circle(screen,BLACK,pos,STATIONSIZE)
			pygame.draw.circle(screen,WHITE,pos,STATIONSIZE-STATIONTHICKNESS)


stations = []
lines = []

def init_city():
	"""we set some Stations in place."""
	
	print "Setting stations..."
	for i in range(0,MAXSTATIONS):
		foundpos = False
		while not foundpos:
			newstationpos = (random.randint(0 + 2 * STATIONSIZE, 
								   MAX_X - 2 * STATIONSIZE),
			        random.randint(0 + 2 * STATIONSIZE, 
								   MAX_Y - 2 * STATIONSIZE))
			print "trying position ", newstationpos
			foundpos = True
			for s in stations:
				if is_in_range(newstationpos,s.pos,STATIONDISTANCE):
					foundpos = False
					print "... is to near to ", s.pos
					
			if foundpos:
				print "position ok!"
				s = Station(newstationpos)
				stations.append(s)

def is_in_range(pos1,pos2,dist=STATIONSIZE):
	"""returns true if pos1 and pos2 are not more than dist pixels apart"""
	
	if pos1[0] < pos2[0] - dist:
		return False
	if pos1[0] > pos2[0] + dist:
		return False 		
	if pos1[1] < pos2[1] - dist:
		return False 
	if pos1[1] > pos2[1] + dist:
		return False 
	return True

def is_station_pos(pos):
	"""returns center of station if at pos is a station."""
	
	for s in stations:
		if is_in_range(pos,s.pos):
			return s.pos
	return False


def update():
	"""updates (position of) all user independent objects"""
	
	for l in lines:
		l.update()

def main():

	# this status is True if the user is drawing a track
	draw_status = False
	
	init_city()
	
	# Initialise screen
	pygame.init()
	clock = pygame.time.Clock()
	pygame.display.set_caption('Maxi Metro')
	pygame.display.update()

	pos = (0,0);
	startpos = (0,0)
	have_line = False
	line = ""
	# Event loop
	while 1:

		screen.fill(WHITE)
			
		# TODO: the whole handling of track-creation should be 
		#       in the Line-class
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == MOUSEBUTTONDOWN:
				draw_status = False
				if have_line:
					LINES.pop()
				have_line = False
				if LINES:
					pos = event.pos
					spos = is_station_pos(pos)
					if spos and not draw_status:
						#track = Track(spos)
						startpos = spos
						print "start drawing from " ,pos, " moving to ", startpos
						draw_status = True
				else:
					print "NO MORE LINES AVAIABLE!"
			elif event.type == MOUSEMOTION:
				pos = event.pos
				spos = is_station_pos(pos)
				# TODO: there should be no station in the way 
				#       (plus a little extrasize)
				# TODO: should not cross other tracks
				if draw_status and spos and not is_in_range(pos,startpos):
					print "stop drawing at " , pos , " moving to " , spos
					if have_line:
						print "appending track to line..."
						# startpos = spos

						line.tracks.append(Track(startpos,spos,line.color,line,0))
					else:
						print "creating new line..."
						line = Line(startpos, spos)
						lines.append(line)
						have_line = True
					startpos = spos
						# draw_status = False
			# elif event.type == MOUSEBUTTONUP:
		
		if draw_status:
			pygame.draw.line(screen,LINES[-1],startpos,pos,5)

		update()

		# display all stations and tracks
		for l in lines:
			l.draw()		
		for s in stations:
			s.draw()

		pygame.display.update()
		msElapsed = clock.tick(FPS) # TODO: Gamespeed should be FPS-independent
		
		
if __name__ == '__main__': main()
