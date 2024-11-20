import random
import pygame
import sys
import time
import neat
import os
import math
import matplotlib.pyplot as plt
import csv

pygame.init()
results_file = 'results.csv'

# Open results file and write header
with open(results_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Genome ID', 'Fitness', 'Distance'])

# Screen and font settings
screen = pygame.display.set_mode((1400, 600))
pygame.display.set_caption("HONDA")
WIDTH, HEIGHT = screen.get_size()
font = pygame.font.Font(None, 36)

# Loading images
map_image = pygame.image.load("map_image.jpg")
map_image = pygame.transform.scale(map_image, (1400, 600))

honda_image = pygame.image.load("honda_image.png")
honda_image = pygame.transform.scale(honda_image, (90, 30))

object_image = pygame.image.load("object_image.png")
object_image = pygame.transform.scale(object_image, (100, 40))

# Honda class definition
class Honda:
    def __init__(self, x, y, speed_y):
        self.x = x
        self.y = y
        self.speed_y = speed_y

    def move(self, output, index):
        # Interpret network output
        if output[0] > 0.5 and self.y > 180:  # Move up
            self.y -= self.speed_y
            genomes[index].fitness += 0.08
        if output[1] > 0.5 and self.y < 420:  # Move down
            self.y += self.speed_y
            genomes[index].fitness += 0.08
        if output[2] > 0.5 and self.x < WIDTH - 60:  # Move right
            self.x += self.speed_y
            genomes[index].fitness += 0.03
        if output[3] > 0.5 and self.x > 0:  # Move left
            self.x -= self.speed_y
            genomes[index].fitness += 0.05

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 90, 30)

    def draw(self, screen):
        screen.blit(honda_image, (self.x, self.y))


# Object class
class GameObject:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self):
        self.x -= self.speed

    def is_offscreen(self):
        return self.x < -100

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 100, 40)

    def draw(self, screen):
        screen.blit(object_image, (self.x, self.y))


# Game functions
def create_object_if_needed(objects, global_speed):
    spawn_prob = global_speed / 200
    if random.random() < spawn_prob:
        new_x = WIDTH
        new_y = random.choice([HEIGHT // 2 + 120, HEIGHT // 2 - 120, HEIGHT // 2 + 60, HEIGHT // 2, HEIGHT // 2 - 60])

        object_speed = random.triangular(global_speed - 1, global_speed + 2)
        objects.append(GameObject(new_x, new_y, object_speed))


def check_collision(honda, objects, index, genomes):
    honda_rect = honda.get_rect()
    for obj in objects:
        if honda_rect.colliderect(obj.get_rect()):
            return True
    return False


def get_all_objects(honda, objects, max_objects=20):
    # Sort objects by distance to the Honda
    objects_distances = sorted(objects, key=lambda obj: math.dist((honda.x, honda.y), (obj.x, obj.y)))

    # Create a list with object positions and speeds
    inputs = []
    for obj in objects_distances[:max_objects]:
        inputs.append(obj.x)  # Object's x
        inputs.append(obj.y)  # Object's y
        inputs.append(obj.speed)  # Object's speed

    # Fill data to ensure max_objects limit is met
    while len(inputs) < max_objects * 3:
        inputs.append(WIDTH)  # x off-screen
        inputs.append(HEIGHT)  # y off-screen
        inputs.append(0)  # speed 0

    return inputs


def check_proximity(objects):
    for i in range(len(objects) - 1):
        if abs(objects[i].y - objects[i + 1].y) < 10 and 0 < (objects[i + 1].x - objects[i].x) < 150:
            if objects[i].speed > objects[i + 1].speed:
                objects[i].speed = objects[i + 1].speed


def eval_genomes(genomes, config):
    global global_speed, hondas, objects, nets
    objects = []
    global_speed = 0.5
    hondas = []
    nets = []

    # Initialize the population and neural networks
    for genome_id, genome in genomes:
        honda = Honda(100, HEIGHT // 2, 5)
        hondas.append(honda)
        genomes.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0  # Initial fitness

    clock = pygame.time.Clock()
    speed_increase_time = time.time()

    while hondas:  # Loop as long as there are Hondas in the game
        current_time = time.time()
        if current_time - speed_increase_time > 2:
            global_speed += 0.1
            speed_increase_time = current_time
        distance_traveled = global_speed

        create_object_if_needed(objects, global_speed)
        objects = [obj for obj in objects if not obj.is_offscreen()]
        for obj in objects:
            obj.move()

        for i in range(len(hondas) - 1, -1, -1):  # Reverse loop over hondas
            honda = hondas[i]
            all_object_positions_and_speeds = get_all_objects(honda, objects)
            inputs = [honda.x, honda.y] + all_object_positions_and_speeds
            output = nets[i].activate(inputs)
            honda.move(output, i)  # Pass the index i to the move method
            genomes[i].fitness += 0.1  # Reward for survival

            # Check for collision
            if check_collision(honda, objects, i, genomes):
                genomes[i].fitness -= 10  # Penalty for collision
                hondas.pop(i)
                nets.pop(i)
                genomes.pop(i)

        screen.blit(map_image, (0, 0))
        for honda in hondas:
            honda.draw(screen)
        for obj in objects:
            obj.draw(screen)

        distance_text = font.render(f"Distance: {distance_traveled:.2f}", True, (255, 255, 255))
        screen.blit(distance_text, (10, 50))
        pygame.display.flip()
        clock.tick(144)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Write only for active genomes
        with open(results_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            for j, genome in enumerate(genomes):
                writer.writerow([genome.key, genome.fitness, global_speed])


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    pop = neat.Population(config)
    pop.run(eval_genomes, 200)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)
