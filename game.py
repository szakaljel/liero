import pygame, sys
from pygame.locals import *
import client
import server



class worm(object):
	def __init__(self):
		object.__init__(self)
		
		self.ident=0;
		self.x=0
		self.y=0
		self.img=self.background=pygame.image.load("images/cat.png")
		self.max_x=800
		self.max_y=600

	def draw(self,screen):
		screen.blit(self.img,(self.x,self.y))

	def key_fun(self,key,map=None):
		
		if key==pygame.K_UP:
			self.y-=10
			if self.y<0:
				self.y=0
		elif key==pygame.K_DOWN:
			self.y+=10
			if self.y>self.max_y:
				self.y=self.max_y
		elif key==pygame.K_LEFT:
			self.x-=10
			if self.x<0:
				self.x=0
		elif key==pygame.K_RIGHT:
			self.x+=10
			if self.x>self.max_x:
				self.x=self.max_x


def set_direct(event,up,down,left,right):

	if event.type == pygame.KEYDOWN:
		k=event.key
		if k==pygame.K_UP:
			up=1
		elif k==pygame.K_DOWN:
			down=1
		elif k==pygame.K_LEFT:
			left=1
		elif k==pygame.K_RIGHT:
			right=1
					
	if event.type == pygame.KEYUP:
		k=event.key
		if k==pygame.K_UP:
			up=0
		elif k==pygame.K_DOWN:
			down=0
		elif k==pygame.K_LEFT:
			left=0
		elif k==pygame.K_RIGHT:
			right=0

	return (up,down,left,right)



class controller(object):
	def __init__(self,screen):
		object.__init__(self)
		
		self.ident=0
		#self.worm=worm()
		self.worm=[]
		for i in range(4):
			self.worm.append(worm())
			self.worm[i].ident=i
		self.screen=screen

	def loop(self,port_ip):
		FPS = 30 # frames per second setting
		fpsClock = pygame.time.Clock()

		up=0
		down=0
		left=0
		right=0

		client.init(port_ip)
		val=None
		while val==None:
			val=client.recv();
		self.ident=val[0];
		print"trlalala"
		while True:
			for event in pygame.event.get():

				(up,down,left,right)=set_direct(event,up,down,left,right)

				if event.type == QUIT:
					client.close()
					pygame.quit()
					sys.exit()


			if up==1:
				self.worm[self.ident].key_fun(pygame.K_UP)
			if down==1:
				self.worm[self.ident].key_fun(pygame.K_DOWN)
			if left==1:
				self.worm[self.ident].key_fun(pygame.K_LEFT)
			if right==1:
				self.worm[self.ident].key_fun(pygame.K_RIGHT)
			
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
			for w in self.worm:
				w.draw(self.screen)

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

	def loop(self,port_ip):
		FPS = 30 # frames per second setting
		fpsClock = pygame.time.Clock()

		up=0
		down=0
		left=0
		right=0

		server.init(port_ip)

		while True:
			for event in pygame.event.get():
				
				(up,down,left,right)=set_direct(event,up,down,left,right)


				if event.type == QUIT:
					server.close()
					pygame.quit()
					sys.exit()

			if up==1:
				self.worm[self.ident].key_fun(pygame.K_UP)
			if down==1:
				self.worm[self.ident].key_fun(pygame.K_DOWN)
			if left==1:
				self.worm[self.ident].key_fun(pygame.K_LEFT)
			if right==1:
				self.worm[self.ident].key_fun(pygame.K_RIGHT)

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
			for w in self.worm:
				w.draw(self.screen)

			pygame.display.update()
			fpsClock.tick(FPS)

def game(screen,port_ip,SorC):
	if SorC==1:
		cont=controller(screen)
		cont.loop(port_ip)
	else:
		cont=controller_server(screen)
		cont.loop(port_ip)

