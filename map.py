import math
import pygame, sys
from pygame.locals import *

class map(object):

	def __init__(self):
		object.__init__(self)
		self.tab=[]
		#rozmiar komorki
		self.x=10
		self.y=10
		#rozmiar mapy w segmentach
		self.xlen=0
		self.ylen=0


	def loadMap(self,path):
		self.tab=[]
		#odwzorowanie mapy jeden znak w pliku to 4x4 komorka na mapie
		re_size=4
		file=open(path,"rb")

		#wczytanie pozycji graczy
		ret=[]
		for i in range(4):
			tmp=file.readline()
			tab=tmp.split()
			ret.append((int(tab[0])*self.x*re_size,int(tab[1])*self.y*re_size))

		#petla wczytuje mape po lini przeksztalca 1 znak na re_size x re_size
		while True:
			tmp=file.readline()
			if tmp!='':
				tmp=tmp[0:-2]
				for i in range(re_size):
					self.tab.append([])
				for znak in tmp:
					for j in range(re_size):
						for k in range(re_size):
							self.tab[-(j+1)].append(znak)
			else:
				break

		#rozmiar mapy segmenty
		self.ylen=len(self.tab)
		self.xlen=len(self.tab[0])
		
		return ret
		

	def drawMap(self,screen,x,y):
		
		#wektor transformacji
		trans_x=0
		trans_y=0

		#wektor przesuniecia mapy
		v_x=0
		v_y=0

		pos_x=0
		pos_y=0
		
		#rozmiar ekranu
		width=screen.get_width()
		height=screen.get_height()

		#ilosc segmentow na ekranie
		segment_x=math.ceil(width/float(self.x))
		segment_y=math.ceil(height/float(self.y))

		sr_segment=[x/self.x,y/self.y]

		#x<width/2
		if x-(segment_x/2)*self.x<0:
			sr_segment[0]=math.ceil(segment_x/2)
			trans_x=0
		#x>xlen-width/2
		elif x+(segment_x/2)*self.x >= self.xlen*self.x:
			sr_segment[0]=self.xlen-math.floor(segment_x/2)
			trans_x=(self.xlen-segment_x)*self.x	
		else:
			trans_x=x-width/2
			v_x=sr_segment[0]*self.x-trans_x-width/2
			#normalizacja nie wypada na lini srodek
			v_x-=int(((width/2)/float(self.x)-int((width/2)/float(self.x)))*self.x)

		if y-segment_y/2*self.y<0:
			sr_segment[1]=math.ceil(segment_y/2)
			trans_y=0
		elif y+(segment_y/2)*self.y >= self.ylen*self.y:
			sr_segment[1]=self.ylen-math.floor(segment_y/2)
			trans_y=(self.ylen-segment_y)*self.y
		else:
			trans_y=y-height/2
			v_y=sr_segment[1]*self.y-trans_y-height/2
			#normalizacja nie wypada na lini srodek
			v_y-=int(((height/2)/float(self.y)-int((height/2)/float(self.y)))*self.y)

		

		sr_segment[0]-=int(math.ceil(segment_x/2))
		sr_segment[1]-=int(math.ceil(segment_y/2))


		sr_segment[0]=int(sr_segment[0])
		sr_segment[1]=int(sr_segment[1])

		
		pos_x=v_x
		pos_y=v_y

		for r in range(sr_segment[1],self.ylen):
			for s in range(sr_segment[0],self.xlen):
				if self.tab[r][s]==' ':
					pygame.draw.rect(screen,(0,0,0),Rect(pos_x,pos_y,self.x,self.y))
				if pos_x >width:
					break	
				pos_x+=self.x
			pos_x = v_x
			pos_y+=self.y 
			if pos_y>height:
				break
		return (trans_x,trans_y)

