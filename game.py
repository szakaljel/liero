#!/usr/bin/python
# -*- coding: utf-8-*-

import pygame, sys
from pygame.locals import *
import random
import client
import server
import math
from sprite import ImageInfo, Sprite
from map import map

XY_SEND=0
ANGLE_SEND=1
CREATE_BULLET=2

X=0
Y=1

up=0
down=1
left=2
right=3
space=4
k_x=5

missile_info = ImageInfo([5,5], [10, 10], 3, 400)
missile_image = pygame.image.load("images/shot3.png")
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = pygame.image.load("images/explosion_orange.png")

colours = ((0,255,255),(255,0,0),(255,0,255),(0,255,0))

random.seed()

class worm(object):
	def __init__(self):
		object.__init__(self)
		
		self.ident=0;
		self.x=0
		self.y=0
		self.speed_x=0.0
		self.speed_y=0.0
		self.target_angle=0
		self.target_speed=2
		self.reload=15
		
		original_image = pygame.image.load("images/Catz-BlackCat3.png").convert_alpha()
		
		# konstrukcja obrazków
		rect_norm = pygame.Rect( 680, 249, 40, 50)
		self.img_norm = pygame.Surface((40,50),flags=pygame.SRCALPHA)
		self.img_norm.blit(original_image, (0,0),rect_norm)
		self.img_norm = pygame.transform.scale(self.img_norm, (40, 40)) # lewy
		self.img_norm_r = pygame.transform.flip(self.img_norm, True, False) # prawy

		rect_down = pygame.Rect( 224, 405, 40, 50)
		self.img_down = pygame.Surface((40,50),flags=pygame.SRCALPHA)
		self.img_down.blit(original_image, (0,0),rect_down)
		self.img_down = pygame.transform.scale(self.img_down, (40, 40))
		self.img_down_r = pygame.transform.flip(self.img_down, True, False)	

		rect_up = pygame.Rect( 245, 456, 30, 45)
		self.img_up = pygame.Surface((40,50),flags=pygame.SRCALPHA)
		self.img_up.blit(original_image, (0,0),rect_up)
		self.img_up = pygame.transform.scale(self.img_up, (40, 40))		
		self.img_up_r = pygame.transform.flip(self.img_up, True, False)

		rect_top = pygame.Rect( 370, 456, 30, 45)
		self.img_top = pygame.Surface((40,50),flags=pygame.SRCALPHA)
		self.img_top.blit(original_image, (0,0),rect_top)
		self.img_top = pygame.transform.scale(self.img_top, (40, 40))		
		self.img_top_r = pygame.transform.flip(self.img_top, True, False)

		self.img = self.img_norm_r
		self.direction = right # zwrot, przybiera wartości left lub right
		width=self.img.get_width()
		height=self.img.get_height()
		self.info=ImageInfo([width/2,height/2],[width,height],width/2)
		self.max_x=800
		self.max_y=600
		self.colour = colours[0]
		self.score = 0
		
	def get_position(self):
		return (self.x,self.y)
		
	def get_radius(self):
		return self.info.radius
		
	def get_missle_start(self):
		return (self.x + 25*math.cos(self.target_angle*math.pi/180), self.y + 25*math.sin(self.target_angle*math.pi/180))
		
	def get_missle_velocity(self):
		return (math.cos(self.target_angle*math.pi/180)*14.22,math.sin(self.target_angle*math.pi/180)*14.22)

	def draw(self,screen,tr_x,tr_y):
		screen.blit(self.img,(self.x-tr_x-self.info.center[X],self.y-tr_y-self.info.center[Y]))
		pos_x=self.x+math.cos(self.target_angle*math.pi/180.0)*self.info.radius*1.5;
		pos_y=self.y+math.sin(self.target_angle*math.pi/180.0)*self.info.radius*1.5;
		pygame.draw.circle(screen,self.colour,(int(pos_x-tr_x),int(pos_y-tr_y)),5,1)
		
	def respawn(self,map):
		while True:
			x = random.randrange(map.xlen)
			y = random.randrange(map.ylen)
			if map.tab[y][x] == ' ':
				self.x = x * map.x
				self.y = y * map.y
				return

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
			
		target_angle_changed = False
		# jezeli wcisnieta jest tylko jedna strzalka w bok, ustawiamy kierunek i zmieniamy kąt 
		if direct[left] + direct[right] == 1:
			old_direction = self.direction
			self.direction = left if direct[left] else right
			if self.direction != old_direction:
				target_angle_changed = True
				if self.target_angle <= 180:
					self.target_angle = 179 - self.target_angle # 179 --> patrz poniżej
				else:
					self.target_angle = 539 - self.target_angle # 179 i 539 zamiast 180 i 540 mam dlatego,
																# że 89 przynależy na prawo a 90 na lewo
																# a 269 przynależy na lewo, a 270 na prawo
		

		# zmianna kąta na strzałki góra-dół zależy od zwrotu kota
		if direct[up]:
			target_angle_changed = True
			if self.direction == left:
				self.target_angle+=self.target_speed
				if self.target_angle >= 270:
					self.target_angle = 269
			else:
				self.target_angle -= self.target_speed
				if self.target_angle < 0:
					self.target_angle += 360
				elif self.target_angle < 270 and self.target_angle > 180:
					self.target_angle = 270
				
		if direct[down]:
			target_angle_changed = True
			if self.direction == left:
				self.target_angle -= self.target_speed
				if self.target_angle<90:
					self.target_angle=90
			else:
				self.target_angle += self.target_speed
				if self.target_angle >= 90 and self.target_angle < 180:
					self.target_angle = 89	
				elif self.target_angle >=360:
					self.target_angle -= 360
				
		# ustawienie aktualnego obrazka (jeżeli trzeba)
		if target_angle_changed:
			if self.target_angle >= 330 or self.target_angle < 30:
				self.img = self.img_norm_r
			elif self.target_angle < 90:
				self.img = self.img_down_r
			elif self.target_angle < 150:
				self.img = self.img_down
			elif self.target_angle < 210:
				self.img = self.img_norm
			elif self.target_angle < 240:
				self.img = self.img_up
			elif self.target_angle < 270:
				self.img = self.img_top
			elif self.target_angle < 300:
				self.img = self.img_top_r
			else:
				self.img = self.img_up_r
			

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
					#doldef group_collide(sprite_set,other_object):
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
				
	def update_image(self):
		if self.target_angle >= 330 or self.target_angle < 30:
			self.img = self.img_norm_r
		elif self.target_angle < 90:
			self.img = self.img_down_r
		elif self.target_angle < 150:
			self.img = self.img_down
		elif self.target_angle < 210:
			self.img = self.img_norm
		elif self.target_angle < 240:
			self.img = self.img_up
		elif self.target_angle < 270:
			self.img = self.img_top
		elif self.target_angle < 300:
			self.img = self.img_top_r
		else:
			self.img = self.img_up_r

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
		elif k==pygame.K_x:
			direct[k_x]=1
					
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
		elif k==pygame.K_x:
			direct[k_x]=0

	return direct


class controller(object):
	def __init__(self,screen):
		object.__init__(self)
		self.ident=0
		self.worm=[]
		for i in range(4):
			self.worm.append(worm())
			self.worm[i].ident = i
			self.worm[i].colour = colours[i]
		self.screen = screen
		self.sprites = set()
		self.explosions = set()
		self.FPS = 30
		self.map = map()
		location=self.map.loadMap("map")
		#ustawienie pozycji wormow z pliku 
		for i in range(4):
			(self.worm[i].x,self.worm[i].y)=location[i]		
		self.did_shoot = False
		self.font = pygame.font.SysFont("monospace", 20)

	def print_scores(self):
		label = None
		for index, worm in enumerate(self.worm):
			label = self.font.render("worm " + str(index) + " : " + str(worm.score), 1, colours[index])
			self.screen.blit(label, (20, 400 + 30*index))
		
	def sprites_collide(self,other_object):
		collision=False
		for sprite in set(self.sprites):
			if sprite.collide(other_object):
				self.explosions.add(Sprite(sprite.get_position(), (0,0), 0, 0, 0, explosion_image, explosion_info))
				self.sprites.remove(sprite)
				self.worm[sprite.owner].score += 1
				collision=True
		return collision
		
	def loop(self,port_ip):
		self.loop_init(port_ip)
		fpsClock = pygame.time.Clock()

		direct=[0,0,0,0,0,0]
				
		#modyfikacja granic poruszania worma
		self.worm[self.ident].max_x=self.map.xlen*self.map.x
		self.worm[self.ident].max_y=self.map.ylen*self.map.y
		
		while True:
			for event in pygame.event.get():
				
				direct = set_direct(event,direct)

				if event.type == QUIT:
					server.close()
					pygame.quit()
					sys.exit()
			
			self.worm[self.ident].key_fun(direct,self.map)
					
			if direct[k_x] and self.worm[self.ident].reload<=0:
				self.did_shoot = True
				self.worm[self.ident].reload=15
				missile_position = self.worm[self.ident].get_missle_start()
				missile_velocity = self.worm[self.ident].get_missle_velocity()
				self.sprites.add(Sprite(missile_position, missile_velocity, self.ident, self.worm[self.ident].target_angle, 0, missile_image, missile_info))		
				
			self.communicate_keyboard()
			self.did_shoot = False
			
			#otrzymywanie wiadomosci			
			val = self.receiver_function()
			ident = None
			action = None
			while val != None:
				ident = val[0] % 4
				action = val[0] / 4
				w = self.worm[ident]
				if action == XY_SEND:
					w.x = val[1]
					w.y = val[2]
				elif action == ANGLE_SEND:
					w.target_angle=float(val[1])
					w.update_image()
				elif action == CREATE_BULLET:
					missile_position = w.get_missle_start()
					missile_velocity = w.get_missle_velocity()
					self.sprites.add(Sprite(missile_position, missile_velocity, ident, w.target_angle, 0, missile_image, missile_info))
				
				self.communicate_received(val,ident)
					
				val = self.receiver_function()
				
			lst = set(self.sprites)
			for sprite in lst:
			    if sprite.update(self.map):
			    	self.sprites.remove(sprite)
			    	self.explosions.add(Sprite(sprite.get_position(), (0,0), 0, 0, 0, explosion_image, explosion_info))
			    				    	
			lst = set(self.explosions)
			for expl in lst:
			    if expl.update(self.map):
			    	self.explosions.remove(expl)
			    	
			self.worm[self.ident].reload -= 1
			
			self.screen.fill((255,255,255))
			(tr_x,tr_y) = self.map.drawMap(self.screen,self.worm[self.ident].x,self.worm[self.ident].y)
			for w in self.worm:
				if self.sprites_collide(w): # kolizja update'uje wynik tego, co wystrzelił pocisk
					if w.ident == self.ident:
						w.respawn(self.map)
						self.communicate_keyboard() # wyślij informacje o nowej pozycji
				w.draw(self.screen,tr_x,tr_y)
				
			for sprite in self.sprites:
			    sprite.draw(self.screen,tr_x,tr_y)
			    
			for expl in self.explosions:
				expl.draw(self.screen,tr_x,tr_y)
				
			self.print_scores()	
				
			pygame.display.update()
			fpsClock.tick(self.FPS)		
			
		
class controller_client(controller):
	def __init__(self,screen):
		super(controller_client,self).__init__(screen)
		self.receiver_function = client.recv

	def loop_init(self,port_ip):
		client.init(port_ip)
		val=None
		while val==None:
			val=client.recv()
		self.ident=val[0]
	
	def communicate_keyboard(self):
			#wysylam pozycje i kat
		client.send((4*XY_SEND+self.worm[self.ident].ident,self.worm[self.ident].x,self.worm[self.ident].y))
		client.send((4*ANGLE_SEND+self.worm[self.ident].ident,int(self.worm[self.ident].target_angle),0))
		
		if self.did_shoot:
			client.send((4*CREATE_BULLET+self.worm[self.ident].ident,1,0))
			
	def communicate_received(self, val, ident):
		pass # klient nie rozsyla

class controller_server(controller):
	def __init__(self,screen):
		super(controller_server,self).__init__(screen)
		self.receiver_function = server.recv

	def loop_init(self,port_ip):
		server.init(port_ip)
		
	def communicate_keyboard(self):
		for i in self.worm[1:]:
			server.send((i.ident,(4*XY_SEND+self.worm[self.ident].ident,self.worm[self.ident].x,self.worm[self.ident].y)))
			server.send((i.ident,(4*ANGLE_SEND+self.worm[self.ident].ident,int(self.worm[self.ident].target_angle),0)))
			
		if self.did_shoot:
			for i in self.worm[1:]:
				server.send((i.ident,(4*CREATE_BULLET+self.worm[self.ident].ident,1,0)))
				
	def communicate_received(self, val, ident):
		for w in self.worm:
			if w.ident != ident:
				server.send((w.ident,val))		

def game(screen,port_ip,SorC):
	if SorC==1:
		cont=controller_client(screen)
		cont.loop(port_ip)
	else:
		cont=controller_server(screen)
		cont.loop(port_ip)

