
import pygame
from scenery import *
from player import Player
from network import Network
from settings import *
import time  # Import time module
import random


questions = [
    {"question": "What is the capital of France?", "answer": "Paris"},
    {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"},
    {"question": "What year did the Titanic sink?", "answer": "1912"},
    {"question": "Who wrote 'Macbeth'?", "answer": "William Shakespeare"},
    {"question": "What is the hardest natural substance on Earth?", "answer": "Diamond"}
]


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
LIGHT_GREY = (200, 200, 200)

def fps(font, clock):
	txt = "FPS: " + str(int(clock.get_fps()))
	txt += " | You: Knight, P2: Green Knight, P3: Red Knight, P4: Blue Knight"
	txt_render = font.render(txt, 1, pygame.Color("black"))
	return txt_render

def set_color_mask(player, color):
	color_image = pygame.Surface(player.image.get_size())
	color_image.fill(color)
	masked_image = player.image.convert_alpha()
	masked_image.set_colorkey((0,0,0))
	masked_image.blit(color_image, (0,0), None, pygame.BLEND_RGBA_MULT)
	player.image.blit(masked_image,(0,0), None)

def redrawWindow(window, background, map_tiles, font, clock, player, player2, player3, player4, current_question=None, current_answer=""):
	window.blit(background, (0,0))
	for tile in map_tiles:
		tile.draw(window)
	set_color_mask(player4, BLUE)
	player4.draw(window)
	set_color_mask(player3, RED)
	player3.draw(window)
	set_color_mask(player2, GREEN)
	player2.draw(window)
	player.draw(window)
	window.blit(fps(font, clock), (5, HEIGHT - 73))

	if current_question:
		pygame.draw.rect(window, LIGHT_GREY, (0, HEIGHT, WIDTH, 100))
		question_surface = font.render("Q: " + current_question, True, BLACK)
		answer_surface = font.render("A: " + current_answer, True, BLACK)
		window.blit(question_surface, (10, HEIGHT + 10))
		window.blit(answer_surface, (10, HEIGHT + 40))
	pygame.display.update()

def display_congratulations(window, font, question_text):
    light_grey = (211, 211, 211)  
    white = (255, 255, 255)       
    green = (0, 0, 0)           

    bottom_area_height = 60  
    bottom_area_y = window.get_height() - bottom_area_height  
    congrats_text = font.render("Correct answer!", True, green)
    congrats_rect = congrats_text.get_rect(center=(window.get_width() / 2, bottom_area_y + bottom_area_height / 2))
    pygame.draw.rect(window, light_grey, (0, bottom_area_y, window.get_width(), bottom_area_height))
    window.blit(congrats_text, congrats_rect.topleft)
    pygame.display.update()


def main():
	pygame.init()
	current_question = random.choice(questions)
	current_answer = ""  
	font = pygame.font.SysFont(None, 25, True)
	window = pygame.display.set_mode((WIDTH, HEIGHT + 100))
	game_map = Map()
	background = pygame.image.load("assets/background/background_1.png")
	background = pygame.transform.scale(background, (3840//4,2160//4))
	pygame.display.set_caption(TITLE)
	icon = pygame.image.load("assets/icon.png")
	pygame.display.set_icon(icon)
	network = Network()
	start_position = network.get_position()
	start_time = pygame.time.get_ticks()
	question_interval = 35000
	last_question_time = start_time
	player = Player(start_position[0],start_position[1],PLAYER_WIDTH,PLAYER_HEIGHT)
	player2 = Player(100,0,PLAYER_WIDTH,PLAYER_HEIGHT)
	player3 = Player(200,0,PLAYER_WIDTH,PLAYER_HEIGHT)
	player4 = Player(300,0,PLAYER_WIDTH,PLAYER_HEIGHT)
	clock = pygame.time.Clock()
	final_tiles = pygame.sprite.Group()
	map_tiles = pygame.sprite.Group()
	for row, tiles in enumerate(game_map.data):
		for col, tile in enumerate(tiles):
			if tile == '0':
				map_tiles.add(Limit(col, row))
			elif tile == '1':
				map_tiles.add(Stone(col, row))
			elif tile == 'G':
				map_tiles.add(Greenery(col, row))
			elif tile == 'P':
				map_tiles.add(Plaque(col, row))
			elif tile == 'B':
				map_tiles.add(Barrel(col, row))
			elif tile == 'S':
				map_tiles.add(Statue(col, row))
			elif tile == 'E':
				map_tiles.add(Goblin(col, row))
			elif tile == 'F':
				final_tiles.add(Final(col, row))
	
	run = True
	while run:
		current_time = pygame.time.get_ticks()
		time_elapsed = current_time - last_question_time
		if time_elapsed >= question_interval:
            
			pause_game(window, font, background, map_tiles, clock, player, player2, player3, player4)
			last_question_time = current_time
		clock.tick(FPS)
		players_data = network.send((player.x, player.y))
		player2.x , player2.y = players_data[0]
		player2.update()
		player3.x , player3.y = players_data[1]
		player3.update()
		player4.x , player4.y = players_data[2]
		player4.update()
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
		player.move(map_tiles)
		
		for tile in final_tiles:
			if player.rect.colliderect(tile):
				win_or_lose = pygame.font.SysFont(None, 60, True)
				game_over_message = "Congratulations, you win!"
				while True:
					window.blit(background, (0,0))
					window.blit(win_or_lose.render(game_over_message, 1, pygame.Color("white")), (160, 250))
					pygame.display.update()
		
		redrawWindow(window, background, map_tiles, font, clock, player, player2, player3, player4)
	pygame.quit()

def pause_game(window, font, background, map_tiles, clock, player, player2, player3, player4):
	selected_qa = random.choice(questions)
	question_text = selected_qa["question"]
	answer = selected_qa["answer"]  
	user_answer = ""
	running = True
	congratulations_displayed = False
	
	while running:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					if user_answer.strip().lower() == answer.lower():
						congratulations_displayed = True
						display_congratulations(window, font, question_text)
						pygame.time.wait(2000)
						running = False
					else:
						print("Wrong answer! Try again.")
						user_answer = ""
				elif event.key == pygame.K_BACKSPACE:
					user_answer = user_answer[:-1]
				else:
					user_answer += event.unicode
					
		redrawWindow(window, background, map_tiles, font, clock, player, player2, player3, player4, question_text, user_answer)
		
	return user_answer


if __name__ == "__main__":
    main()


    last_question_time = pygame.time.get_ticks()
    question_interval = 5000  

    while running:
        current_time = pygame.time.get_ticks()
        if current_time - last_question_time > question_interval:
            selected_question = random.choice(questions)  
            print(selected_question)  
            last_question_time = current_time