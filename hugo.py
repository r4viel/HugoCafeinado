import pygame
import random
import csv
import sys
import os 
import math
import pygame as pg

largura, altura = 800, 400
gravidade = 0.8

pygame.init()
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Hugo Cafeinado")
imagem_fundo = pygame.image.load('FundoJogo.webp')
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 28)
big_fonte = pygame.font.SysFont(None, 48)
RomeritoDeitado = pygame.image.load('romero.png').convert_alpha()

class MeuSprite(pygame.sprite.Sprite):
    def __init__(self, imagem_original):
        super().__init__()
        self.image = imagem_original
        self.rect = self.image.get_rect()
        self.rect.topleft = (50, 200)

todas_as_sprites = pygame.sprite.Group()
meu_jogador = MeuSprite(RomeritoDeitado)
todas_as_sprites.add(meu_jogador)
        
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
    tela.blit(imagem_fundo, (0, 0))
    
    todas_as_sprites.update() 
    todas_as_sprites.draw(tela)

    pygame.display.flip()


