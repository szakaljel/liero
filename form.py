import pygame, sys
from pygame.locals import *
import eztext

class form(object):

	def __init__(self):
		object.__init__(self)

		#inputboxy
		self.inputs=[]

		#aktualnie zaznaczony
		self.focus=None

		#wymiary ekranu
		self.screen_w=800
		self.screen_h=600

		self.font=pygame.font.SysFont("monospace",15,bold=True)

		#tlo
		self.background=pygame.image.load("images/background.jpg")
		self.background=pygame.transform.scale(self.background,(self.screen_w,self.screen_h))
		#trzeba przeskalowac przy zmianie

	def set_screen_size(self,w,h):
		self.screen_w=w
		self.screen_h=h

	def set_inputs(self,list):
		
		x=self.screen_w/2
		y=self.screen_h/4
		for i in list:
			inp=eztext.Input(maxlength=20, color=(255,0,0), prompt=i)
			inp.set_pos(x-inp.font.size("w"*inp.maxlength)[0]/2,y)
			inp.colorRect=(150,150,150)
			self.inputs.append(inp)
			y+=100
	
	def set_background(self,back):
		self.background=back 

	
	def draw(self,screen):
		screen.blit(self.background,(0,0))

		r=Rect(100,self.screen_h-100,self.screen_w-200,80)
		pygame.draw.rect(screen,self.inputs[0].colorRect,r)
		
		label1 = self.font.render("Tab --> change inputbox", 1, (255,0,0))
		label2 = self.font.render("Enter --> Confirm", 1, (255,0,0))
		
		screen.blit(label1,((self.screen_w-label1.get_width())/2,self.screen_h-80))
		screen.blit(label2,((self.screen_w-label2.get_width())/2,self.screen_h-50))

		for i in self.inputs:
			i.draw(screen)
	
	#funkcja obsluhujaca inputboxy
	def loop(self,screen):
		tick=0
		FPS = 30 # frames per second setting
		fpsClock = pygame.time.Clock()
		while True:
			l=len(self.inputs)
			events=pygame.event.get()
			for event in events:
				if event.type == pygame.KEYDOWN:
					#Tab zmienia focus miedzy inputboxami 
					if event.key==pygame.K_TAB:
						if self.focus==None:
							self.focus=self.inputs[0]
						else:
							index=self.inputs.index(self.focus)
							self.focus.rest=""
							self.focus=self.inputs[(index+1)%l]
					#enter powoduje zwrucenie zwartosci inputboxow
					elif event.key==pygame.K_RETURN:
						ret=[]
						for el in self.inputs:
							ret.append(el.value)
						return ret 
				elif event.type == QUIT:
					pygame.quit()
					sys.exit()
			#update zaznaczonego inputboxa
			if self.focus!=None:
				self.focus.update(events)
			self.draw(screen)
			pygame.display.update()

			tick+=1
			tick=tick%15
			#wyswietlenie migajacego _ w inputboxie 
			if tick==0 and self.focus!=None:
				if self.focus.rest=="":
					self.focus.rest="_"
				else:
					self.focus.rest=""

			fpsClock.tick(FPS)


