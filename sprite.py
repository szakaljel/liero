#!/usr/bin/python
# -*- coding: utf-8-*-

import pygame

WIDTH = 800
HEIGHT = 600

class ImageInfo:
	"""
	Klasa: dane o typie obrazka.
	Jedna instancja jest do wielokrotnego wykorzystania dla wszyskich Sprite'ów tego samego typu.
	"""
	def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
		self.center = center
		self.size = size
		self.radius = radius
		if lifespan:
			self.lifespan = lifespan
		else:
			self.lifespan = float('inf')
		self.animated = animated
		
	def get_center(self):
		return self.center

	def get_size(self):
		return self.size

	def get_radius(self):
		return self.radius

	def get_lifespan(self):
		return self.lifespan

	def get_animated(self):
		return self.animated

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


class Sprite:
	"""
	Klasa: obiekt gry z prostokątnym rysunkiem.
	
	- fizyka: wykrywanie zderzeń zakłada, że obiekty mają swój "promień", 
	        : obiekty poruszają się prostoliniowo, można dodać grawitację
	- obroty można zaimplementować jak będę wiedział jak w Pygame obraca się prostokąt.
	  Na razie kąt i prędkość kątowa nie są wykorzystywane
	- czas życia: służy do usuwania starych obiektów i do taktowania animacji (patrz metoda draw)
	"""
	def __init__(self, pos, vel, ang, ang_vel, image, info):
		self.pos = [pos[0],pos[1]]
		self.vel = [vel[0],vel[1]]
		self.angle = ang
		self.angle_vel = ang_vel
		self.image = image
		self.image_center = info.get_center()
		self.image_size = info.get_size()
		self.radius = info.get_radius()
		self.lifespan = info.get_lifespan()
		self.animated = info.get_animated()
		self.age = 0
               
	def draw(self, screen):
		if self.animated:
			# wskazujemy który segment rysunku trzeba narysować wskazując prostokąt:
			# new_rect  =     Rect (left, top, width, height)
			new_rect = pygame.Rect( self.age*self.image_size[0], 0, self.image_size[0], self.image_size[1])
			# u nas width i height to rozmiary pojedynczego segmentu, przesuwamy więc left w zależności od age
			screen.blit(self.image, self.pos,new_rect)
		else:
			screen.blit(self.image, self.pos)

	def collide(self,other_object):
		return dist(other_object.get_position(),self.pos)<(self.radius+other_object.get_radius())
		
	def update(self):
		self.angle += self.angle_vel
		self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
		self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
		self.age+=1
		return self.age>=self.lifespan
		
	def get_position(self):
		return self.pos

	def get_radius(self):
		return self.radius