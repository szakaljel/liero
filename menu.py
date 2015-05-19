import pygame, sys
from pygame.locals import *

#klasa reprezentujaca element menu
class menu_item(object):
	def __init__(self,text,x,y):
		object.__init__(self)
		self.text=text
		self.x=x
		self.y=y

	def draw(self,screen,selected,font):
		myfont=font
		if selected!=None and selected is self:
			label = myfont.render(self.text, 1, (255,0,0))
		else:
			label = myfont.render(self.text, 1, (255,255,0))
		(w,h)=myfont.size(self.text)
		screen.blit(label,(self.x-w/2,self.y))
		

#klasa reprezentujaca menu
class menu(object):

	#konstruktor
	def __init__(self,list,rect,background=None):
		
		object.__init__(self)
		#potrzebne do wyswietlenia tla
		self.screen_w=800
		self.screen_h=600
		
		#lista elementow menu
		self.elements=[]
		
		#prostokat zawierajacy menu (menu wysrodkowane w nim horyzontalnie)
		self.rect=rect
		
		#element zaznaczony 
		self.selected=None
		
		#czcionka 
		self.font=pygame.font.SysFont("monospace",30,bold=True)
		
		#tlo menu
		if background==None:
			self.background=pygame.image.load("images/background.jpg")
			self.background=pygame.transform.scale(self.background,(self.screen_w,self.screen_h))
		else:	
			self.background=background
			self.background=pygame.transform.scale(self.background,(self.screen_w,self.screen_h))

		length=len(list)
		height=rect.height
		width=rect.width
		skok=height/length

		tmp_y=0+rect.top
		tmp_x=width/2+rect.left
		
		#inicjalizacja listy elementow menu 
		for i in list:
			self.elements.append(menu_item(i,tmp_x,tmp_y))
			tmp_y+=skok

	#funkcja rysuje menu
	def draw(self,screen):
		#wstawianie tla
		screen.blit(self.background,(0,0))

		#wyswietlanie wszystkich elementow
		for i in self.elements:
			i.draw(screen,self.selected,self.font)

	#ustawia rozmiary tla
	def set_screen_size(self,width,height):
		self.screen_w=width
		self.screen_h=height

	#ustawia czcionke
	def set_font(self,font):
		self.font=font

	#funkcja obsloguje klawisze (sterowanie)
	#zwraca -1 gdy nie enter
	#zwraca index zaznaczonrgo elementu gdy enter
	def key(self,k):
		l=len(self.elements)
		ret=-1
		if k == pygame.K_UP:
			if self.selected==None:
				self.selected=self.elements[-1]
			else:
				index = self.elements.index(self.selected)
				if index!=-1:
					self.selected=self.elements[(index-1)%l]

		elif k == pygame.K_DOWN:
			if self.selected==None:
				self.selected=self.elements[0]
			else:
				index = self.elements.index(self.selected)
				if index!=-1:
					self.selected=self.elements[(index+1)%l]
		elif k == pygame.K_RETURN:
			if self.selected!=None:
				ret=self.elements.index(self.selected)
		return ret

	def loop(self,screen):
		FPS = 30 # frames per second setting
		fpsClock = pygame.time.Clock()

		while True:
			self.draw(screen)
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					odp=self.key(event.key)
					if odp!=-1:
						return odp
				elif event.type == QUIT:
					pygame.quit()
					sys.exit()
    
			pygame.display.update()
			fpsClock.tick(FPS)

