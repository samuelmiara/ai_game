import random
import pygame
import sys
import time
import neat
import os
import math
import matplotlib.pyplot as plt
import csv
import colorsys


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
    def __init__(self, x, y, speed_y, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.speed_y = speed_y
        self.color = color
        self.colored_image = self.apply_color_to_image(honda_image, color)

    def apply_color_to_image(self, image, color):

        colored_image = image.copy()

        color_mask = pygame.Surface(colored_image.get_size()).convert_alpha()
        color_mask.fill(color)

        colored_image.blit(color_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return colored_image
    def move(self, output, index):
        # Interpret network output
        if output[0] > 0.5 and self.y > 180:  # Move up
            self.y -= self.speed_y
            # ge[index].fitness += 0.09
        if output[1] > 0.5 and self.y < 420:  # Move down
            self.y += self.speed_y
            # ge[index].fitness += 0.09
        if output[2] > 0.5 and self.x < WIDTH - 60:  # Move right
            self.x += self.speed_y
            # ge[index].fitness += 0.01
        if output[3] > 0.5 and self.x > 0:  # Move left
            self.x -= self.speed_y
            # ge[index].fitness += 0.05

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 90, 30)

    def draw(self, screen):

        screen.blit(self.colored_image, (self.x, self.y))


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

def generate_colors(num_colors):

    colors = []
    for i in range(num_colors):

        hue = i / num_colors
        lightness = 0.6
        saturation = 0.8


        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)

        rgb = tuple(int(255 * x) for x in rgb)
        colors.append(rgb)
    return colors

# Example reward for staying close to lane center
def reward_lane_centering(honda, ge, index, target_center_x=WIDTH // 2):
    distance_to_center = abs(honda.x - target_center_x)
    # Reward inversely proportional to distance to center
    ge[index].fitness += max(0, 5 - (distance_to_center / 40))  # Adjust values as needed

# Penalize rapid up-down movements
def penalize_rapid_movement(honda, ge, index, prev_y):
    movement_delta = abs(honda.y - prev_y)
    if movement_delta > 120:  # Adjust threshold value as needed
        ge[index].fitness -= 0.1 * (movement_delta / 15)  # Adjust penalty multiplier
# Example of scaling collision penalty with time/speed

# Reward avoiding objects within a close distance but without collision
def reward_object_avoidance(honda, objects, ge, index):
    for obj in objects:
        distance = math.dist((honda.x, honda.y), (obj.x, obj.y))
        if 36 < distance < 115:  # Reward being "close" but avoiding collision
            ge[index].fitness += 0.2  # Adjust reward value

def check_collision(honda, objects, index, ge, time_elapsed):
    honda_rect = honda.get_rect()
    for obj in objects:
        if honda_rect.colliderect(obj.get_rect()):
            penalty = 10 + (time_elapsed / 5)  # Increase penalty as time progresses  not sure
            ge[index].fitness -= penalty  # Apply collision penalty
            return True
    return False

# Reward for survival that scales with global speed
def reward_survival(honda, ge, index, global_speed):
    ge[index].fitness += 0.2 + (global_speed / 10)  # Adjust values as needed

# Increase survival reward based on the number of objects on screen
def reward_based_on_object_density(honda, ge, index, objects):
    object_count = len(objects)
    if object_count > 7:  # Only if there are many objects on screen
        ge[index].fitness += 0.05 * object_count  # Reward based on number of objects


# Game functions
def create_object_if_needed(objects, global_speed):
    spawn_prob = global_speed / 200
    if random.random() < spawn_prob:
        new_x = WIDTH
        new_y = random.choice([HEIGHT // 2 + 120, HEIGHT // 2 - 120, HEIGHT // 2 + 60, HEIGHT // 2, HEIGHT // 2 - 60])

        object_speed = random.triangular(global_speed - 1, global_speed + 2)
        objects.append(GameObject(new_x, new_y, object_speed))





def get_all_objects(honda, objects, max_objects=20):
    # Filtrowanie obiektów, które są poza ekranem
    objects = [obj for obj in objects if not obj.is_offscreen()]

    # Sortowanie obiektów według odległości od Hondy (opcjonalnie)
    # objects_distances = sorted(objects, key=lambda obj: math.dist((honda.x, honda.y), (obj.x, obj.y)))

    # Tworzenie listy z pozycjami i prędkościami obiektów
    inputs = []
    for obj in objects[:max_objects]:
        inputs.append(obj.x)  # Współrzędna x obiektu
        inputs.append(obj.y)  # Współrzędna y obiektu
        inputs.append(obj.speed)  # Prędkość obiektu

    # Wypełnianie danych, aby spełnić limit max_objects
    while len(inputs) < max_objects * 3:
        inputs.append(WIDTH)  # Współrzędna x poza ekranem
        inputs.append(HEIGHT)  # Współrzędna y poza ekranem
        inputs.append(0)  # Prędkość 0

    return inputs



def check_proximity(objects):
    for i in range(len(objects) - 1):
        if abs(objects[i].y - objects[i + 1].y) < 10 and 0 < (objects[i + 1].x - objects[i].x) < 150:
            if objects[i].speed > objects[i + 1].speed:
                objects[i].speed = objects[i + 1].speed


def eval_genomes(genomes, config):
    global global_speed, hondas, ge, objects, nets
    objects = []
    global_speed = 0.5
    hondas = []
    ge = []
    nets = []

    num_genomes = len(genomes)
    available_colors = generate_colors(num_genomes)

    for index, (genome_id, genome) in enumerate(genomes):
        color = available_colors[index % len(available_colors)]

        honda = Honda(100, HEIGHT // 2, 5, color=color)
        hondas.append(honda)
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0


    clock = pygame.time.Clock()
    speed_increase_time = time.time()
    prev_time = time.time()

    while hondas:
        current_time = time.time()
        if current_time - speed_increase_time > 2:
            global_speed += 0.1
            speed_increase_time = current_time

        distance_traveled = global_speed
        time_elapsed = current_time - prev_time

        create_object_if_needed(objects, global_speed)
        objects = [obj for obj in objects if not obj.is_offscreen()]
        for obj in objects:
            obj.move()

        for i in range(len(hondas) - 1, -1, -1):
            honda = hondas[i]
            previous_x = honda.x  # Track previous position
            all_object_positions_and_speeds = get_all_objects(honda, objects)
            inputs = [honda.x, honda.y] + all_object_positions_and_speeds
            output = nets[i].activate(inputs)
            honda.move(output, i)

            # Apply various fitness adjustments
            reward_survival(honda, ge, i, global_speed)

            reward_lane_centering(honda, ge, i)
            reward_object_avoidance(honda, objects, ge, i)

            # Penalize if needed
            if check_collision(honda, objects, i, ge, time_elapsed):
                hondas.pop(i)
                nets.pop(i)
                ge.pop(i)

        prev_time = current_time
        screen.blit(map_image, (0, 0))
        for honda in hondas:
            honda.draw(screen)
        for obj in objects:
            obj.draw(screen)

        distance_text = font.render(f"Distance: {distance_traveled:.2f}", True, (255, 255, 255))
        screen.blit(distance_text, (10, 50))
        pygame.display.flip()
        clock.tick(150)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Write only for active genomes
        with open(results_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            for j, genome in enumerate(ge):
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
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, 200)
    pop = neat.Population(config)

    # Add a StatisticsReporter to collect statistics during the run
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    log_generation_data(stats, filename='generation_stats.csv')


# def run_experiments(config_path, experiment_params):
#     """
#     Runs multiple experiments with different NEAT configurations.
#
#     :param config_path: Path to the NEAT config file.
#     :param experiment_params: A list of dictionaries with NEAT parameters to vary.
#     """
#     for idx, params in enumerate(experiment_params):
#         # Modify config file with given parameters
#         modified_config_path = f"config_experiment_{idx}.txt"
#         modify_neat_config(config_path, modified_config_path, params)
#
#         # Run experiment
#         print(f"\nRunning Experiment {idx + 1} with parameters: {params}")
#         run(modified_config_path)


# def modify_neat_config(original_path, modified_path, params):
#     """
#     Modifies a NEAT config file with new parameters and saves it.
#
#     :param original_path: The path of the original NEAT config file.
#     :param modified_path: The path to save the modified config file.
#     :param params: A dictionary with parameters to update in the config.
#     """
#     with open(original_path, 'r') as file:
#         lines = file.readlines()
#
#     with open(modified_path, 'w') as file:
#         for line in lines:
#             # Replace parameters if they exist in the params dictionary
#             key = line.split('=')[0].strip()
#             if key in params:
#                 new_line = f"{key} = {params[key]}\n"
#                 file.write(new_line)
#             else:
#                 file.write(line)


# def plot_fitness_progress(stats):
#     """
#     Plots the best and average fitness scores over generations.
#
#     :param stats: neat.statistics.StatisticsReporter object with fitness stats
#     """
#     generation = range(len(stats.most_fit_genomes))
#     best_fitness = [genome.fitness for genome in stats.most_fit_genomes]
#     avg_fitness = stats.get_fitness_mean()  # Corrected line to get average fitness
#
#     plt.figure(figsize=(10, 5))
#     plt.plot(generation, best_fitness, label='Best Fitness', color='blue')
#     plt.plot(generation, avg_fitness, label='Average Fitness', color='green')
#     plt.title('Fitness Progress Over Generations')
#     plt.xlabel('Generations')
#     plt.ylabel('Fitness')
#     plt.legend()
#     plt.grid()
#     # plt.show()


def log_generation_data(stats, filename='generation_stats.csv'):
    """
    Logs generation-level fitness data to a CSV file.

    :param stats: neat.statistics.StatisticsReporter object with fitness stats
    :param filename: The filename for the CSV file (default: generation_stats.csv)
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Generation', 'Best Fitness', 'Average Fitness'])

        avg_fitness_data = stats.get_fitness_mean()  # Retrieve average fitness data

        for gen in range(len(stats.most_fit_genomes)):
            best_fitness = stats.most_fit_genomes[gen].fitness
            avg_fitness = avg_fitness_data[gen]  # Use correct data for average fitness
            writer.writerow([gen, best_fitness, avg_fitness])


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    while True:  # Run continuously
        run(config_path)

