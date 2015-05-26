#!/usr/bin/python
# -*- coding: utf-8-*-

import pygame, sys
from pygame.locals import *
import client
import server
import math
from sprite import ImageInfo, Sprite
from map import map


up=0
down=1
left=2
right=3

class worm(object):
	def __init__(self):
		object.__init__(self)
		
		self.ident=0;
		self.x=0
		self.y=0
		self.img=self.background=pygame.image.load("images/cat.png")
		self.img=pygame.transform.scale(self.img, (40, 40))
		self.max_x=800
		self.max_y=600


	def draw(self,screen,tr_x,tr_y):
		screen.blit(self.img,(self.x-tr_x,self.y-tr_y))

	def key_fun(self,direct,map=None):
		
		if direct[up]:
			self.y-=10
			if self.y<0:
				self.y=0
		if direct[down]:
			self.y+=10
			if self.y>self.max_y:
				self.y=self.max_y
		if direct[left]:
			self.x-=10
			if self.x<0:
				self.x=0
		if direct[right]:
			self.x+=10
			if self.x>self.max_x:
				self.x=self.max_x


def set_direct(event,direct):

	if event.type == pygame.KEYDOWN:
		k=event.key
		if k==pygame.K_UP:
			direct[up]=1
		elif k==pygame.K_DOWN:
			direct[down]=1
		elif k==pygame.K_LEFT:
			direct[left]=1
		elif k==pygame.K_RIGHT:
			direct[right]=1
					
	if event.type == pygame.KEYUP:
		k=event.key
		if k==pygame.K_UP:
			direct[up]=0
		elif k==pygame.K_DOWN:
			direct[down]=0
		elif k==pygame.K_LEFT:
			direct[left]=0
		elif k==pygame.K_RIGHT:
			direct[right]=0

	return direct



class controller(object):
	def __init__(self,screen):
		object.__init__(self)
		
		self.ident=0
		self.worm=[]
		for i in range(4):
			self.worm.append(worm())
			self.worm[i].ident=i
		self.screen=screen

	def loop(self,port_ip):
		FPS = 30 # frames per second setting
		fpsClock = pygame.time.Clock()

		#incjalizacja i wczytanie mapy
		map1=map()
		location=map1.loadMap("map")

		#ustawienie pozycji wormow z pliku 
		for i in range(4):
			(self.worm[i].x,self.worm[i].y)=location[i]

		direct=[0,0,0,0]
		

		client.init(port_ip)
		val=None
		while val==None:
			val=client.recv();
		self.ident=val[0];
		
		#modyfikacja granic poruszania worma
		self.worm[self.ident].max_x=map1.xlen*map1.x
		self.worm[self.ident].max_y=map1.ylen*map1.y

		while True:
			for event in pygame.event.get():

				direct=set_direct(event,direct)

				if event.type == QUIT:
					client.close()
					pygame.quit()
					sys.exit()


			self.worm[self.ident].key_fun(direct)
			
			
			if up+down+left+right>0:
				client.send((self.worm[self.ident].ident,self.worm[self.ident].x,self.worm[self.ident].y))

			val=client.recv()
			while val!=None:
				for w in self.worm:
					if val[0]==w.ident:
						w.x=val[1]
						w.y=val[2]
				val=client.recv()


			self.screen.fill((255,255,255))
			#odrysowanie mapy zwrocono wektor translacji
			(tr_x,tr_y) = map1.drawMap(self.screen,self.worm[self.ident].x,self.worm[self.ident].y)
			
			for w in self.worm:
				w.draw(self.screen,tr_x,tr_y)

			pygame.display.update()
			fpsClock.tick(FPS)

class controller_server(object):
	
	def __init__(self,screen):
		object.__init__(self)
		self.ident=0
		self.worm=[]
		for i in range(4):
			self.worm.append(worm())
			self.worm[i].ident=i
		self.screen=screen
		
		self.sprites = set()
		# sprite, przykład pierwszy: pociski o prędkościach (1,2) i (2,1) i czasie życia 400 wykonań pętli
		missile_info = ImageInfo([5,5], [10, 10], 3, 400)
		missile_image = pygame.image.load("images/shot3.png")
		
		missile_position = (0,79)
		missile_velocity = (1,2)
		self.sprites.add(Sprite(missile_position, missile_velocity, 0, 0, missile_image, missile_info))
		
		missile_position = (0,100)
		missile_velocity = (2,1)
		self.sprites.add(Sprite(missile_position, missile_velocity, 0, 0, missile_image, missile_info))

		# sprite, przykład drugi: animacja eksplozji (animated = True) o czasie życia 24 wykonań pętli
		explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
		explosion_image = pygame.image.load("images/explosion_orange.png")
		explosion_position = (125,0)
		explosion_velocity = (0,0)
		self.sprites.add(Sprite(explosion_position, explosion_velocity, 0, 0, explosion_image, explosion_info))

	def loop(self,port_ip):
		FPS = 30 # frames per second setting
		fpsClock = pygame.time.Clock()

		#incjalizacja i wczytanie mapy
		map1=map()
		location=map1.loadMap("map")

		#ustawienie pozycji wormow z pliku 
		for i in range(4):
			(self.worm[i].x,self.worm[i].y)=location[i]

		direct=[0,0,0,0]

		server.init(port_ip)
		
		#modyfikacja granic poruszania worma
		self.worm[self.ident].max_x=map1.xlen*map1.x
		self.worm[self.ident].max_y=map1.ylen*map1.y

		while True:
			for event in pygame.event.get():
				
				direct=set_direct(event,direct)


				if event.type == QUIT:
					server.close()
					pygame.quit()
					sys.exit()
			
			self.worm[self.ident].key_fun(direct)
			

			if up+down+left+right>0:
				for i in self.worm:
					if i.ident!=0:
						server.send((i.ident,(self.worm[self.ident].ident,self.worm[self.ident].x,self.worm[self.ident].y)))

			val=server.recv()
			while val!=None:
				for w in self.worm:
					if val[0]==w.ident:
						w.x=val[1]
						w.y=val[2]
						for w2 in self.worm:
							if w2.ident!=w.ident:
								server.send((w2.ident,val))

				val=server.recv()

			self.screen.fill((255,255,255))
			#odrysowanie mapy zwrocono wektor translacji
			(tr_x,tr_y) = map1.drawMap(self.screen,self.worm[self.ident].x,self.worm[self.ident].y)
			for w in self.worm:
				w.draw(self.screen,tr_x,tr_y)
				
				
			# rysuję sprite'y
			for sprite in self.sprites:
			    sprite.draw(self.screen)
			    
			# robię update sprite'om. Trzeba pracować na kopii zbioru, 
			# ponieważ usuwamy obiekty, których żywot dobiegł końca,
			# a usuwanie z czegoś po czym iterujemy to zło.
			lst = set(self.sprites)
			for sprite in lst:
			    if sprite.update():
			    	# upadate zwraca True, jeżeli obiekt jest do usunięcia
			    	self.sprites.remove(sprite)
			    	

			pygame.display.update()
			fpsClock.tick(FPS)

def game(screen,port_ip,SorC):
	if SorC==1:
		cont=controller(screen)
		cont.loop(port_ip)
	else:
		cont=controller_server(screen)
		cont.loop(port_ip)

