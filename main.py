#!/usr/bin/python
# -*- coding: utf-8-*-

from menu import menu
from form import form
from game import game
import pygame, sys
from pygame.locals import *


def menu_main(screen,screen_width,screen_height):
	
	list=["Serwer","Client","Exit"]
	rect=Rect(200,100,400,400)
	myMenu=menu(list,rect)
	myMenu.set_screen_size(screen_width,screen_height)
	ret=myMenu.loop(screen)
	return ret

	

def serwer_main(screen,screen_width,screen_height):

	list=["Port: "]
	f=form()
	f.set_screen_size(screen_width,screen_height)
	f.set_inputs(list)
	f.inputs[0].value = '12000'	
	ret=f.loop(screen)
	return ret[0]

def client_main(screen,screen_width,screen_height):

	list=["Port: ","IP: "]
	f=form()
	f.set_screen_size(screen_width,screen_height)
	f.set_inputs(list)
	# do usunięcia w wersji RELASE
	f.inputs[0].value = '12000'	
	f.inputs[1].value = 'localhost'	
	ret=f.loop(screen)
	return (ret[0],ret[1])


def main():


	screen_width=800
	screen_height=600

	screen = pygame.display.set_mode((screen_width,screen_height), 0, 32)
	pygame.display.set_caption('Fucking Liero')
	pygame.init()
	while True:
		ret=menu_main(screen,screen_width,screen_height)	
		if ret==2:
			pygame.quit()
			sys.exit()
		elif ret==0:
			port_ip=serwer_main(screen,screen_width,screen_height)
			game(screen,port_ip,0)	
		else:
			port_ip=client_main(screen,screen_width,screen_height)
			game(screen,port_ip,1)	



if __name__=="__main__":
	main()
	
