#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------
# Importación de módulos
# ------------------------------

import pygame
from pygame.locals import *
import sys
import os
import random
import pickle

# ------------------------------
# Constantes
# ------------------------------

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
IMG_DIR = 'images'
SOUND_DIR = 'sounds'
FONTS_DIR = 'fonts'

escena = None


# ------------------------------
# Funciones y clases
# ------------------------------

# Creamos la función para cargar imágenes.
def load_image(name, dir, alpha=False):
    # Unimos la ruta de la imágen.
    ruta = os.path.join(dir, name)
    # Probamos a cargarla y si no devolvemos error.
    try:
        image = pygame.image.load(ruta)
        print 'Cargando imagen', ruta, '=> éxito'

    except:
        print 'No se pudo cargar la imagen', ruta
        sys.exit(1)

    # Comprobamos si hay alpha.
    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()

    return image


# Función para cargar sonidos.
def load_sound(name, dir_sound):
    ruta = os.path.join(dir_sound, name)
    try:
        sound = pygame.mixer.Sound(ruta)
        print 'Cargando sonido', ruta, '=> éxito'
    except:
        sound = None
        print 'No se pudo cargar el sonido', ruta

    return sound


# Función para cargar fuentes, devuelve el sprite y su rect.
def texto(texto, fuente, dir_fonts, posx, posy, size=25,
          color=(255, 255, 255)):
    ruta = os.path.join(dir_fonts, fuente)
    fuente = pygame.font.Font(ruta, size)
    salida = pygame.font.Font.render(fuente, texto, 1, color)
    salida_rect = salida.get_rect()
    salida_rect.centerx = posx
    salida_rect.centery = posy
    return salida, salida_rect


# Clase para el menú.
class Menu():
    def __init__(self, opciones):
        self.opciones = opciones
        self.seleccionado = 0
        self.total = len(self.opciones)
        self.mantiene_pulsado = False
        self.fondo_menu = load_image('fondo_menu.png', IMG_DIR)
        self.sprites = pygame.sprite.Group()

    def update(self):
        # Altera la opción seleccionada con las teclas cursor.
        key = pygame.key.get_pressed()

        if not self.mantiene_pulsado:
            if key[K_UP]:
                self.seleccionado -= 1
            elif key[K_DOWN]:
                self.seleccionado += 1
            elif key[K_RETURN]:
                # Invoca a la función asociada a la opción-
                titulo, funcion = self.opciones[self.seleccionado]
                print 'Selecionando función:', repr(titulo)
                funcion()
        # Procura que el cursor esté entre las opciones permitidas.
        if self.seleccionado < 0:
            self.seleccionado = 0
        elif self.seleccionado > self.total - 1:
            self.seleccionado = self.total - 1

        # Indica si el usuario mantiene pulsada alguna tecla.
        self.mantiene_pulsado = key[K_UP] or key[K_DOWN] or key[K_RETURN]

        for event in pygame.event.get():
            if event.type == QUIT:
                print 'Cerrando juego...'
                sys.exit()

        self.sprites.update()

    def imprimir(self, screen):
        screen.blit(self.fondo_menu, (0, 0))

        # Imprime sobre screen el texto de cada opción del menú.
        indice = 0
        altura_de_opcion = 50
        x = SCREEN_WIDTH / 2
        y = 250

        for (titulo, funcion) in self.opciones:
            if indice == self.seleccionado:
                color = (255, 255, 255)
            else:
                color = (255, 255, 0)

            posx = x
            posy = y + altura_de_opcion * indice
            opcion = texto(titulo, 'STARWARS.ttf', FONTS_DIR, posx, \
                           posy, size=altura_de_opcion, color=color)
            indice += 1
            screen.blit(opcion[0], opcion[1])

        self.sprites.draw(screen)

        pygame.display.flip()


# Función para comenzar el nuevo juego.
def nuevo_juego():
    # Pasamos la variable global escena.
    global escena
    escena = Game()


# Función para los créditos.
def creditos():
    # Pasamos la variable global escena.
    global escena
    escena = Creditos()


# Función para la pantalla de cómo jugar.
def como_jugar():
    global escena
    escena = Ayuda()


def salir_juego():
    print 'Cerrando Galactic Wars'
    sys.exit()


# Clase para la nave.
class Nave(pygame.sprite.Sprite):
    def __init__(self, sprites, misiles):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('nave.png', IMG_DIR, alpha=True)
        self.life = load_image('vida.png', IMG_DIR, alpha=True)
        self.life_lost = load_image('vida_perdida.png', IMG_DIR, alpha=True)
        self.rect = self.image.get_rect()
        self.counter = 0
        self.super_counter = 0
        self.super_misiles = 15
        self.laser_counter = 0
        self.laser_counter_recarga = 50
        self.laser_restante = 150
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.centery = SCREEN_HEIGHT - 60
        self.speed = [0, 0]
        self.vidas = 3
        # Grupos de sprites necesarios para añadir misiles.
        self.sprites = sprites
        self.misiles = misiles
        # Cargamos las imágenes y sonidos
        self.misil_img = load_image('disparo_jugador.png', IMG_DIR, alpha=True)
        self.super_misil_img = load_image('super_disparo_jugador.png', IMG_DIR, alpha=True)
        self.laser_img = load_image('laser.png', IMG_DIR, alpha=True)
        self.misil_sound = load_sound('misil.ogg', SOUND_DIR)
        self.laser_sound = load_sound('laser.ogg', SOUND_DIR)

    def update(self):
        # Hacemos que no salga de la pantalla.
        if self.rect.top < 0:
            self.rect.top = 0
            self.speed[1] = 0
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.speed[1] = 0
        elif self.rect.left < 0:
            self.rect.left = 0
            self.speed[0] = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.speed[0] = 0

        # Actualiza la posición de la nave en función de las teclas
        # pulsadas en el momento.
        key = pygame.key.get_pressed()

        if key[K_UP]:
            self.speed[1] -= 0.2
        if key[K_DOWN]:
            self.speed[1] += 0.2
        if key[K_LEFT]:
            self.speed[0] -= 0.2
        if key[K_RIGHT]:
            self.speed[0] += 0.2

        # Comprobamos si estamos disparando.
        if key[K_SPACE]:
            self.shoot()
        if key[K_c]:
            self.shoot_super()
        if key[K_x]:
            self.shoot_laser()

        # Hace que la nave se vaya frenando poco a poco.
        if self.speed[1] < 0:
            self.speed[1] += 0.03
        if self.speed[1] > 0:
            self.speed[1] -= 0.03
        if self.speed[0] < 0:
            self.speed[0] += 0.03
        if self.speed[0] > 0:
            self.speed[0] -= 0.03

        # Actualiza el contador para simular la recarga de munición.
        if self.counter > 0:
            self.counter -= 1
        if self.super_counter > 0:
            self.super_counter -= 1
        if self.laser_counter > 0:
            self.laser_counter -= 1

        if self.laser_counter_recarga > 0:
            self.laser_counter_recarga -= 1
        if self.laser_counter_recarga == 0 and self.laser_restante < 150:
            self.laser_restante += 1
            self.laser_counter_recarga = 50

        self.rect.move_ip(self.speed)

    # Indica si podemos disparar Misiles.
    def can_shoot(self):
        return self.counter == 0

    # Indica si podemos disparar Super Misiles.
    def can_shoot_super(self):
        if self.super_counter == 0 and self.super_misiles > 0:
            return True
        else:
            return False

    # Indica si podemos disparar laser.
    def can_shoot_laser(self):
        if self.laser_counter == 0 and self.laser_restante > 0:
            return True
        else:
            return False

    # Dispara los misiles.
    def shoot(self):
        if self.can_shoot():
            misil = Misil(self.rect.midtop, self.sprites, self.misiles, \
                          self.misil_img, self.misil_sound)
            # Actualiza el tiempo de recarga.
            self.counter = 40

    # Dispara los Super misiles.
    def shoot_super(self):
        if self.can_shoot_super():
            misil = Misil(self.rect.midtop, self.sprites, self.misiles, \
                          self.super_misil_img, self.misil_sound, destruccion=3)
            # Actualiza el tiempo de recarga.
            self.super_counter = 100
            self.super_misiles -= 1

    # Dispara los laseres.
    def shoot_laser(self):
        if self.can_shoot_laser():
            misil = Misil(self.rect.midtop, self.sprites, self.misiles, \
                          self.laser_img, self.laser_sound, destruccion=0.25)
            # Actualiza el tiempo de recarga.
            self.laser_counter = 10
            self.laser_counter_recarga = 50
            self.laser_restante -= 1

    # Muestra el número de vidas en pantalla.
    def generar_vidas(self, posx, posy, sprites, lifes_group, indice):
        life = Life(self.life, self.life_lost, posx, posy, indice)
        sprites.add(life)
        lifes_group.add(life)


# Clase para las vidas de la nave.
class Life(pygame.sprite.Sprite):
    def __init__(self, image, image_lost, posx, posy, indice):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image_lost = image_lost
        self.rect = self.image.get_rect()
        self.rect.centerx = posx
        self.rect.centery = posy
        self.indice = indice

    def comprobar_existencia(self, vidas):
        if vidas < self.indice:
            self.image = self.image_lost


# Muestra los Super misiles restantes.
class Marcador_super_misiles(pygame.sprite.Sprite):
    def __init__(self, misiles_restantes):
        pygame.sprite.Sprite.__init__(self)
        self.restantes = misiles_restantes
        self.color = self.comprobar_color()
        self.text = texto(str(self.restantes), 'STARWARS.ttf', FONTS_DIR, \
                          40, 50, size=20, color=self.color)
        self.image = self.text[0]
        self.rect = self.text[1]

    def comprobar_color(self):
        if self.restantes > 5:
            color = (0, 255, 0)
        elif self.restantes <= 5 and self.restantes > 3:
            color = (255, 125, 0)
        elif self.restantes >= 0:
            color = (255, 0, 0)

        return color

    def actualizar_misiles(self, misiles_restantes):
        self.restantes = misiles_restantes

    def update(self):
        self.color = self.comprobar_color()
        self.text = texto(str(self.restantes), 'STARWARS.ttf', FONTS_DIR, \
                          40, 50, size=20, color=self.color)
        self.image = self.text[0]
        self.rect = self.text[1]


# Muestra los laseres restantes.
class Marcador_laser(pygame.sprite.Sprite):
    def __init__(self, misiles_restantes):
        pygame.sprite.Sprite.__init__(self)
        self.restantes = misiles_restantes
        self.color = self.comprobar_color()
        self.text = texto(str(self.restantes), 'STARWARS.ttf', FONTS_DIR, \
                          90, 50, size=20, color=self.color)
        self.image = self.text[0]
        self.rect = self.text[1]

    def comprobar_color(self):
        if self.restantes > 50:
            color = (0, 255, 0)
        elif self.restantes <= 50 and self.restantes > 15:
            color = (255, 125, 0)
        elif self.restantes >= 0:
            color = (255, 0, 0)

        return color

    def actualizar_misiles(self, misiles_restantes):
        self.restantes = misiles_restantes

    def update(self):
        self.color = self.comprobar_color()
        self.text = texto(str(self.restantes), 'STARWARS.ttf', FONTS_DIR, \
                          90, 50, size=20, color=self.color)
        self.image = self.text[0]
        self.rect = self.text[1]


# Marcador de puntos.
class Marcador(pygame.sprite.Sprite):
    def __init__(self, puntos):
        pygame.sprite.Sprite.__init__(self)
        self.puntos = puntos
        self.color = (255, 0, 0)
        self.text = texto(str(self.puntos), 'STARWARS.ttf', FONTS_DIR, 0, 0, size=20, color=self.color)
        self.image = self.text[0]
        self.rect = self.text[1]
        self.rect.right = SCREEN_WIDTH - 5
        self.rect.top = 10

    def actualizar_puntos(self, puntos):
        self.puntos = puntos

    def update(self):
        self.text = texto(str(self.puntos), 'STARWARS.ttf', FONTS_DIR, 0, 0, size=20, color=self.color)
        self.image = self.text[0]
        self.rect = self.text[1]
        self.rect.right = SCREEN_WIDTH - 5
        self.rect.top = 10


# Marcador de Hi-Score
class Marcador_Hi(pygame.sprite.Sprite):
    def __init__(self, puntos):
        pygame.sprite.Sprite.__init__(self)
        self.puntos = puntos
        self.color = (255, 0, 0)
        self.text = texto(str(self.puntos), 'STARWARS.ttf', FONTS_DIR, 0, 0, size=20, color=self.color)
        self.image = self.text[0]
        self.rect = self.text[1]
        self.rect.right = SCREEN_WIDTH - 5
        self.rect.top = 30

    def update(self):
        self.text = texto(str(self.puntos), 'STARWARS.ttf', FONTS_DIR, 0, 0, size=20, color=self.color)
        self.image = self.text[0]
        self.rect = self.text[1]
        self.rect.right = SCREEN_WIDTH - 5
        self.rect.top = 30


# Clase para los enemigos.
class Enemigo(pygame.sprite.Sprite):
    def __init__(self, image, vel_max_x=5, vel_min_x=-5, \
                 vel_max_y=3, vel_min_y=1, vidas=1):
        pygame.sprite.Sprite.__init__(self)
        self.vel_max_x = vel_max_x
        self.vel_min_x = vel_min_x
        self.vel_max_y = vel_max_y
        self.vel_min_y = vel_min_y
        self.image = image
        self.rect = self.image.get_rect()
        self.generar_pos()
        self.generar_vel()
        self.vida = vidas
        self.vida_inicial = self.vida

    def update(self):
        if self.rect.left < 0:
            self.speed[0] = -self.speed[0]
        if self.rect.right > SCREEN_WIDTH:
            self.speed[0] = -self.speed[0]

        # Si se queda sin vida o si sale de pantalla lo matamos.
        if self.vida <= 0:
            self.kill()
        if self.rect.top == SCREEN_HEIGHT:
            self.kill()

        self.rect.move_ip(self.speed)

    # Esta función da puntos si la nave muere.
    def comprobar_puntos(self):
        if self.vida <= 0:
            return [True, self.vida_inicial]
        else:
            return [False]

    def generar_pos(self):
        # Genera uns posición de x aleatoria.
        pos = random.randrange(50, SCREEN_WIDTH - 50)
        self.rect.centerx = pos
        self.rect.centery = 25

    def generar_vel(self):
        # Genera una velocidad aleatoria.
        x = random.randrange(self.vel_min_x, self.vel_max_x)
        y = random.randrange(self.vel_min_y, self.vel_max_y)
        self.speed = [x, y]

    def choque_nave(self, nave):
        if self.rect.colliderect(nave.rect):
            nave.vidas -= 1
            self.kill()


# Clase para el misil.
class Misil(pygame.sprite.Sprite):
    def __init__(self, initial_pos, sprites, misiles, image, sound, \
                 destruccion=1.5):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.sound = sound
        self.rect = self.image.get_rect()
        self.rect.midbottom = initial_pos
        self.speed = [0, -4]
        self.poder_destruccion = destruccion
        sprites.add(self)
        misiles.add(self)
        self.sound.play()

    # Si se sale de pantalla lo matamos, si no lo movemos.
    def update(self):
        if self.rect.bottom < 0:
            self.kill()
        if self.poder_destruccion <= 0:
            self.kill()
        else:
            self.rect.move_ip(self.speed)

    # Comprobamos las colisiones con enemigos.
    def colisiones(self, objetivos):  # Objetivos debe ser una lista.
        for objetivo in objetivos:
            if self.rect.colliderect(objetivo):
                objetivo.vida_temp = objetivo.vida
                objetivo.vida -= self.poder_destruccion
                self.poder_destruccion -= objetivo.vida_temp


# Clase para la escena del juego.
class Game():
    def __init__(self):

        # Cargamos el fondo.
        self.fondo = load_image('Fondo1.png', IMG_DIR)
        # Esta variable hará que la priemra vez que llamemos a esta
        # escena se imprima el fondo. Esto es así porque init no recibe
        # screen y por tanto no puede imprimir.
        self.primera_vez = True

        # Cargamos las imágenes para los marcadores y para los enemigos.
        self.super_misil_img_marcador = load_image('super_disparo_jugador.png', IMG_DIR, alpha=True)
        self.laser_img = load_image('laser.png', IMG_DIR, alpha=True)
        self.enemigo_img = load_image('enemigo.png', IMG_DIR, alpha=True)
        self.enemigo_medium_img = load_image('enemigo_mediano.png', IMG_DIR, alpha=True)
        self.enemigo_big_img = load_image('enemigo_grande.png', IMG_DIR, alpha=True)

        # Creamos el grupo de sprites general
        self.sprites = pygame.sprite.Group()
        self.misiles = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()
        self.lifes = pygame.sprite.Group()

        # Creamos un contador para los enemigos aleatorios.
        self.contador = 0
        # Creamos una variable que contenerá los puntos que llevemos.
        self.puntos = 0
        # Vamos a otener el Hi-score.
        self.records = open('records', 'r')
        self.record = pickle.load(self.records)
        self.records.close()
        print 'Cargando Record:', self.record

        # Creamos la nave y la añadimos al grupo sprites.
        self.nave = Nave(self.sprites, self.misiles)
        self.sprites.add(self.nave)

        # Creamos los marcadores.
        posx_life = 20
        posy_life = 20
        indice = 1
        for life in range(self.nave.vidas):
            self.nave.generar_vidas(posx_life, posy_life, self.sprites, self.lifes, indice)
            posx_life += 35
            indice += 1

        self.marcador_super_misiles = Marcador_super_misiles(self.nave.super_misiles)
        self.marcador_laser = Marcador_laser(self.nave.laser_restante)
        self.marcador = Marcador(self.puntos)
        self.marcador_hi_score = Marcador_Hi(self.record)
        self.sprites.add(self.marcador_super_misiles, self.marcador_laser, self.marcador, self.marcador_hi_score)

        self.score = texto('Puntos:', 'bin.ttf', FONTS_DIR, 680, 18, color=(255, 0, 0))
        self.hi_score = texto('Record:', 'bin.ttf', FONTS_DIR, 680, 38, color=(255, 0, 0))

        # Definimos las opciones que mostrará el menú.
        self.menu_opciones = [
            ('Jugar', nuevo_juego),
            (u'Créditos', creditos),
            ('Ayuda', como_jugar),
            ('Salir', salir_juego)
        ]

    def update(self):
        # Pasamos la variable global escena.
        global escena

        # Comprobamos los eventos.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print 'Cerrando Galactic Wars'
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    escena = Menu(self.menu_opciones)

        # Actualizamos el contador de enemigos aleatorios.
        if self.contador > 0:
            self.contador -= 1

        # Generamos los enemigos aleatorios.
        if self.contador == 0:
            self.enemigo = Enemigo(self.enemigo_img)
            self.sprites.add(self.enemigo)
            self.enemigos.add(self.enemigo)
            self.contador = 100

        # Generamos aleatoriamente un enemigo mediano. Ponemos un rango
        # alto para que se genere pocas ocasiones.
        num_aleatorio_1 = random.randrange(0, 600)
        if num_aleatorio_1 == 50:
            self.enemigo = Enemigo(self.enemigo_medium_img, vel_max_x=4, \
                                   vel_min_x=-4, vel_max_y=3, vel_min_y=1, vidas=2)
            self.sprites.add(self.enemigo)
            self.enemigos.add(self.enemigo)

        # Generamos aleatoriamente un enemigo muy fuerte. Ponemos un rango
        # alto para que se genere pocas ocasiones.
        num_aleatorio_2 = random.randrange(0, 1200)
        if num_aleatorio_2 == 50:
            self.enemigo = Enemigo(self.enemigo_big_img, vel_max_x=2, \
                                   vel_min_x=-2, vel_max_y=2, vel_min_y=1, vidas=3)
            self.sprites.add(self.enemigo)
            self.enemigos.add(self.enemigo)

        # Comprobamos las colisiones.
        for misil in self.misiles:
            misil.colisiones(self.enemigos)
        for enemigo in self.enemigos:
            enemigo.choque_nave(self.nave)

        # Comprobamos los puntos.
        for enemigo in self.enemigos:
            comprobacion_puntos = enemigo.comprobar_puntos()
            if comprobacion_puntos[0]:
                self.puntos += comprobacion_puntos[1]
        self.marcador.actualizar_puntos(self.puntos)

        # Comprobamos el número de vidas.
        for life in self.lifes:
            life.comprobar_existencia(self.nave.vidas)
        # Si hemos muerto ponemos la escena de Game Over.
        if self.nave.vidas < 0:
            print 'Entrando a escena de Game Over...'
            escena = Game_Over(self.puntos)
        # Comprobamos el numero de misiles.
        self.marcador_super_misiles.actualizar_misiles(self.nave.super_misiles)
        self.marcador_laser.actualizar_misiles(self.nave.laser_restante)

        # Actualizamos los sprites.
        self.sprites.update()

    def imprimir(self, screen):
        if self.primera_vez:
            screen.blit(self.fondo, (0, 0))
            self.primera_vez = False

        # Actualizamos la pantalla.
        self.sprites.clear(screen, self.fondo)
        
        screen.blit(self.super_misil_img_marcador, (10, 43))
        screen.blit(pygame.transform.scale(self.laser_img, (8, 17)), (60, 43))
        screen.blit(self.score[0], self.score[1])
        screen.blit(self.hi_score[0], self.hi_score[1])
        self.sprites.draw(screen)
        pygame.display.flip()


# Escena de los créditos.
class Creditos():
    def __init__(self):
        self.menu_opciones = [
            ('Jugar', nuevo_juego),
            (u'Créditos', creditos),
            ('Ayuda', como_jugar),
            ('Salir', salir_juego)
        ]
        self.fondo = load_image('fondo_creditos.jpg', IMG_DIR)

    def update(self):
        # Pasamos la variable global escena.
        global escena

        for event in pygame.event.get():
            if event.type == QUIT:
                print 'Cerrando Galactic Wars'
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    escena = Menu(self.menu_opciones)

    def imprimir(self, screen):
        screen.blit(self.fondo, (0, 0))
        self.titulo = texto('Autores:', 'STARWARS.ttf', \
                            FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3, size=30, \
                            color=(255, 255, 255))

        self.autor = texto('Bustos Rocio', 'STARWARS.ttf', \
                           FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 + 50, size=30, \
                           color=(255, 255, 0))

        self.autor2 = texto(u'Echagüe Milton', 'STARWARS.ttf', \
                            FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 + 100, size=30, \
                            color=(255, 255, 0))
        
        self.autor3 = texto(u'Gianni Nicolás', 'STARWARS.ttf', \
                            FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 + 150, size=30, \
                            color=(255, 255, 0))
        
        self.autor4 = texto(u'Giannico Lucas', 'STARWARS.ttf', \
                            FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 + 200, size=30, \
                            color=(255, 255, 0))
        
        self.autor5 = texto(u'Ledesma Ignacio', 'STARWARS.ttf', \
                            FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3 + 250, size=30, \
                            color=(255, 255, 0))

        self.retornar = texto(u'Pulsa Esc para volver al menú', \
                              'STARWARS.ttf', FONTS_DIR, SCREEN_WIDTH / 2, \
                              SCREEN_HEIGHT - 20, size=20, \
                              color=(255, 255, 0))

        screen.blit(self.titulo[0], self.titulo[1])
        screen.blit(self.autor[0], self.autor[1])
        screen.blit(self.autor2[0], self.autor2[1])
        screen.blit(self.autor3[0], self.autor3[1])
        screen.blit(self.autor4[0], self.autor4[1])
        screen.blit(self.autor5[0], self.autor5[1])
        screen.blit(self.retornar[0], self.retornar[1])

        pygame.display.flip()


# Escena del Game Over.
class Game_Over():
    def __init__(self, puntos):
        self.nave = Nave_Game_Over()
        self.puntos = puntos
        nuevo_record = False

        # Guardado de récords.
        self.records = open('records', 'r')
        self.record_a_comparar = pickle.load(self.records)
        self.records.close()
        if self.puntos > self.record_a_comparar:
            self.records = open('records', 'w')
            pickle.dump(self.puntos, self.records)
            self.records.close()
            self.nuevo_record = True
            print 'Guardando nuevo récord:', self.puntos

        self.size = 300
        self.game_over = texto('Game Over', 'STARWARS.ttf', FONTS_DIR, \
                               SCREEN_WIDTH / 2, 100, size=self.size, color=(255, 255, 0))
        self.retornar = texto(u'Pulsa Esc para volver al menú', \
                              'STARWARS.ttf', FONTS_DIR, SCREEN_WIDTH / 2, \
                              SCREEN_HEIGHT - 20, size=20, color=(255, 255, 255))
        self.cadena_muerte = u'Tu nave ha sufrido demasiados daños,'
        self.cadena_muerte_2 = 'ha terminado por explotar.'
        self.cadena_muerte_3 = 'Las esperanzas de este universo se'
        self.cadena_muerte_4 = 'desvanecen junto con los restos'
        self.cadena_muerte_5 = 'de tu nave...'
        self.cadena_muerte_6 = u'Que la fuerza te acompañe'
        self.muerte = texto(self.cadena_muerte, 'STARWARS.ttf', \
                            FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, \
                            size=18, color=(255, 255, 255))
        self.muerte_2 = texto(self.cadena_muerte_2, 'STARWARS.ttf', \
                              FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20, \
                              size=18, color=(255, 255, 255))
        self.muerte_3 = texto(self.cadena_muerte_3, 'STARWARS.ttf', \
                              FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, \
                              size=18, color=(255, 255, 255))
        self.muerte_4 = texto(self.cadena_muerte_4, 'STARWARS.ttf', \
                              FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 70, \
                              size=18, color=(255, 255, 255))
        self.muerte_5 = texto(self.cadena_muerte_5, 'STARWARS.ttf', \
                              FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 90, \
                              size=18, color=(255, 255, 255))
        self.muerte_6 = texto(self.cadena_muerte_6, 'STARWARS.ttf', \
                              FONTS_DIR, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 115, \
                              size=18, color=(255, 255, 255))
        self.puntos_imprimir = texto(str(self.puntos), 'STARWARS.ttf', \
                                     FONTS_DIR, SCREEN_WIDTH / 2 + 160, SCREEN_HEIGHT - 120, \
                                     size=70, color=(255, 255, 0))
        self.puntos_imprimir[1].right = SCREEN_WIDTH - 10
        self.puntos_intro = texto('Puntos', 'STARWARS.ttf', \
                                  FONTS_DIR, SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT - 120, \
                                  size=50, color=(255, 255, 0))
        self.opciones = [
            ('Jugar', nuevo_juego),
            (u'Créditos', creditos),
            ('Ayuda', como_jugar),
            ('Salir', salir_juego)
        ]

    def update(self):
        global escena

        self.game_over = texto('Game Over', 'STARWARS.ttf', FONTS_DIR, \
                               SCREEN_WIDTH / 2, 100, size=self.size, color=(255, 255, 0))
        self.retornar = texto(u'Pulsa Esc para volver al menú', \
                              'STARWARS.ttf', FONTS_DIR, SCREEN_WIDTH / 2, \
                              SCREEN_HEIGHT - 20, size=20, color=(255, 255, 255))
        if self.size > 64:
            self.size -= 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print 'Cerrando juego...'
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    print 'Volviendo al menú...'
                    escena = Menu(self.opciones)

        self.nave.update()

    def imprimir(self, screen):
        screen.fill((0, 0, 0))
        screen.blit(self.game_over[0], self.game_over[1])
        screen.blit(self.retornar[0], self.retornar[1])
        screen.blit(self.muerte[0], self.muerte[1])
        screen.blit(self.muerte_2[0], self.muerte_2[1])
        screen.blit(self.muerte_3[0], self.muerte_3[1])
        screen.blit(self.muerte_4[0], self.muerte_4[1])
        screen.blit(self.muerte_5[0], self.muerte_5[1])
        screen.blit(self.muerte_6[0], self.muerte_6[1])
        screen.blit(self.puntos_imprimir[0], self.puntos_imprimir[1])
        screen.blit(self.puntos_intro[0], self.puntos_intro[1])
        screen.blit(self.nave.image, self.nave.rect)

        pygame.display.flip()


# Clase para la nave del Game Over.
class Nave_Game_Over(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('nave.png', IMG_DIR, alpha=True)
        self.rect = self.image.get_rect()
        self.rect.right = 0
        self.rect.centery = 200
        self.speed = [2, 0]

    def update(self):
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        self.rect.move_ip(self.speed[0], self.speed[1])


# Clase para la nave del Game Over.
"""class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.cargar_images()
        self.step = 0
        self.delay = 2
        image = pygame.image.load('images/explosion/1.png')
        self.image = image.convert_alpha()
        if image.get_alpha is None:
            self.image = image.convert()
        else:
            self.image = image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def cargar_images(self):
        self.frames = []
        for n in range(1, 8):
            path = 'images/explosion/%d.png'
            nueva_imagen = pygame.image.load(path % n)
            self.nueva_imagen = nueva_imagen.convert_alpha()
            if nueva_imagen.get_alpha is None:
                self.nueva_imagen = nueva_imagen.convert()
            else:
                self.nueva_imagen = nueva_imagen.convert_alpha()
            self.rect = self.nueva_imagen.get_rect()
            self.frames.append(nueva_imagen)

    def update(self):
        self.image = self.frames[self.step]

        if self.delay < 0:
            self.delay = 2
            self.step += 1

            if self.step > 6:
                self.kill()
        else:
            self.delay -= 1"""


# Clase para la pantalla de cómo jugar.
class Ayuda():
    def __init__(self):
        self.background_1 = load_image('fondo_ayuda1.png', IMG_DIR)
        self.background_2 = load_image('fondo_ayuda2.png', IMG_DIR)
        self.indice = 1
        self.background = self.comprobar_background()
        self.opciones = [
            ('Jugar', nuevo_juego),
            (u'Créditos', creditos),
            ('Ayuda', como_jugar),
            ('Salir', salir_juego)
        ]

    def comprobar_background(self):
        if self.indice == 1:
            return self.background_1
        elif self.indice == 2:
            return self.background_2

    def update(self):
        global escena

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print 'Cerrando Galactic Wars'
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    escena = Menu(self.opciones)
                if event.key == K_RETURN:
                    if self.indice == 1:
                        self.indice = 2
                    elif self.indice == 2:
                        self.indice = 1

        self.background = self.comprobar_background()

    def imprimir(self, screen):
        screen.blit(self.background, (0, 0))

        pygame.display.flip()


# ------------------------------
# Función principal
# ------------------------------

def main():
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()
    #load_sound("marcha.mp3", SOUND_DIR)
    print 'Iniciando Galactic Wars'

    # Pasamos la variable global escena.
    global escena

    # Creamos la ventana e indicamos nombre e icono.
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Galactic Wars')
    icon = pygame.image.load('images/nave.png').convert_alpha()
    pygame.display.set_icon(icon)

    # Creamos el reloj.
    clock = pygame.time.Clock()
    # Hacemos el ratón visible.
    pygame.mouse.set_visible(True)

    # Lanzamos el menú.
    opciones = [
        ('Jugar', nuevo_juego),
        (u'Créditos', creditos),
        ('Ayuda', como_jugar),
        ('Salir', salir_juego)
    ]

    escena = Menu(opciones)

    # Bucle principal.
    while True:
        # Actualizamos la escena.
        escena.update()
        escena.imprimir(screen)
        clock.tick(60)


if __name__ == "__main__":
    main()

