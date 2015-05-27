#!/usr/bin/python
# -*- coding: utf-8-*-

import pygame, sys
from pygame.locals import *
import client
import server
import math
from sprite import ImageInfo, Sprite
from map import map

X=0
Y=1
up=0
down=1
left=2
right=3
space=4

class worm(object):
	def __init__(self):
		object.__init__(self)
		
		self.ident=0;
		self.x=0
		self.y=0
		self.speed_x=0.0
		self.speed_y=0.0
		self.target_angle=0.0
		self.target_speed=2.0
		self.img=self.background=pygame.image.load("images/cat.png")
		self.img=pygame.transform.scale(self.img, (40, 40))
		self.img.fill((0,255,0))
		width=self.img.get_width()
		height=self.img.get_height()
		self.info=ImageInfo([width/2,height/2],[width,height],width/2)
		self.max_x=800
		self.max_y=600


	def draw(self,screen,tr_x,tr_y):
		screen.blit(self.img,(self.x-tr_x-self.info.center[X],self.y-tr_y-self.info.center[Y]))
		pos_x=self.x+math.cos(self.target_angle*math.pi/180.0)*self.info.radius*1.5;
		pos_y=self.y+math.sin(self.target_angle*math.pi/180.0)*self.info.radius*1.5;
		pygame.draw.circle(screen,(255,0,0),(int(pos_x-tr_x),int(pos_y-tr_y)),5,1)

	def key_fun(self,direct,map):
		
		#tlumienie w osi x
		sup_x=0.2
		#grawitacja
		sup_y=0.5

		

		self.speed_y+=sup_y
		if self.speed_y>5.0:
			self.speed_y=5.0

		#dolna krawedz
		i=self.x
		j=self.y
		edge=[ [i-self.info.center[X],j+self.info.center[Y]] , [i,j+self.info.center[Y]] , [i+self.info.center[X],j+self.info.center[Y]] ]

		touch=False
		#mozliwe blendy indekow
		for point in edge:
			seg_x=int(round(point[X]/float(map.x)))
			seg_y=int(round(point[Y]/float(map.y)))
			if map.tab[seg_y][seg_x]!=' ':
				#print abs(seg_y*map.y-point[Y])
				if abs(seg_y*map.y-point[Y])<map.y/2:
					touch=True
		if touch:
			wsp_x=0.5
			if direct[space]:
				self.speed_y=-10
			
		else:
			sup_x=0.05
			wsp_x=0.1

		if direct[left]:
			self.speed_x-=wsp_x
			if self.speed_x<-5.0:
				self.speed_x=-5.0
		if direct[right]:
			self.speed_x+=wsp_x
			if self.speed_x>5.0:
				self.speed_x=5.0
		

		if self.speed_x>0:
			if self.speed_x>sup_x:
				self.speed_x-=sup_x
			else:
				self.speed_x=0.0
		else:
			if self.speed_x<-sup_x:
				self.speed_x+=sup_x
			else:
				self.speed_x=0.0

		if direct[up]:
			self.target_angle+=self.target_speed
			if self.target_angle>360.0:
				self.target_angle=0.0
		if direct[down]:
			self.target_angle-=self.target_speed
			if self.target_angle<0.0:
				self.target_angle=360.0

		self.move(int(round(self.speed_x)),int(round(self.speed_y)),map)

	def move(self,x,y,map):
		
		#segmenty
		temp_x=self.x+x
		temp_y=self.y+y

		accept_x=self.x
		accept_y=self.y

		#skok wartosci posrednich x
		a=map.x/4

		if temp_x>=self.x:
			a=a
		else:
			a=-a

		#skok wartosci posrednich y
		b=map.y/4

		if temp_y>=self.y:
			b=b
		else:
			b=-b

		wsp=0.5
		for i in range(self.x,temp_x+a,a):
			for j in range(self.y,temp_y+b,b):
				if a<0 :
					#lewa	
					edge=[ [i-self.info.center[X],j-int(wsp*self.info.center[Y])] , [i-self.info.center[X],j] , [i-self.info.center[X],j+int(wsp*self.info.center[Y])] ]
					git=True
					for point in edge:
						seg_x=int(round(point[X]/float(map.x)))
						seg_y=int(round(point[Y]/float(map.y)))
						if seg_x>=0 and seg_y>=0 and seg_x<map.xlen and seg_y<map.ylen:
							
							if map.tab[seg_y][seg_x]!=' ':
								if point[X]-(seg_x+1)*map.x<=-map.x/4:
									git=False
					if git:
						accept_x=i
				else:
					#prawa
					edge=[ [i+self.info.center[X],j-int(wsp*self.info.center[Y])] , [i+self.info.center[X],j] , [i+self.info.center[X],j+int(wsp*self.info.center[Y])] ]
					git=True
					for point in edge:
						seg_x=int(round(point[X]/float(map.x)))
						seg_y=int(round(point[Y]/float(map.y)))

						if seg_x>=0 and seg_y>=0 and seg_x<map.xlen and seg_y<map.ylen:
							
							if map.tab[seg_y][seg_x-1]!=' ':
								if point[X]-(seg_x+1)*map.x<=-map.x/4:
									git=False
					if git:
						accept_x=i
				if b<0 :
					#gora
					edge=[ [i-int(wsp*self.info.center[X]),j-self.info.center[Y]] , [i,j-self.info.center[Y]] , [i+int(wsp*self.info.center[X]),j-self.info.center[Y]] ]
					git=True
					for point in edge:
						seg_x=int(round(point[X]/float(map.x)))
						seg_y=int(round(point[Y]/float(map.y)))
						if seg_x>=0 and seg_y>=0 and seg_x<map.xlen and seg_y<map.ylen:
							
							if map.tab[seg_y][seg_x]!=' ':
								if point[Y]-(seg_y+1)*map.y<=-map.y/4:
									git=False
					if git:
						accept_y=j
					else:
						self.speed_y/=1.2;
				else:
					#dol
					edge=[ [i-int(wsp*self.info.center[X]),j+self.info.center[Y]] , [i,j+self.info.center[Y]] ,[i+int(wsp*self.info.center[X]),j+self.info.center[Y]]]
					git=True
					for point in edge:
						seg_x=int(round(point[X]/float(map.x)))
						seg_y=int(round(point[Y]/float(map.y)))
						if seg_x>=0 and seg_y>=0 and seg_x<map.xlen and seg_y<map.ylen:
							
							if map.tab[seg_y-1][seg_x]!=' ':
								if point[Y]-(seg_y+1)*map.y<=-map.y/4:
									git=False
					if git:
						accept_y=j


		self.x=accept_x
		self.y=accept_y
		#krance mapy
		if self.y<0:
				self.y=0
		if self.y>self.max_y:
				self.y=self.max_y
		if self.x<0:
				self.x=0
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
		elif k==pygame.K_SPACE:
			direct[space]=1
					
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
		elif k==pygame.K_SPACE:
			direct[space]=0

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

		direct=[0,0,0,0,0]
		

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


			self.worm[self.ident].key_fun(direct,map1)
			
			
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

		direct=[0,0,0,0,0]

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
			
			self.worm[self.ident].key_fun(direct,map1)
			

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

