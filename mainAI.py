import math
import pickle
import sys, pygame
import time
from pygame.math import Vector2
import random
import cProfile as Profile
import os
import neat
import visualize

pygame.init()
pygame.display.set_caption('Luca Space Invaders AI')
size = width, height = 1000, 800
black = 0, 0, 0
screen = pygame.display.set_mode(size)
imageFileList = ["static/player1.png", "static/player2.png", "static/player3.png",
                 "static/alien1.png", "static/alien2.png", "static/alien3.png",
                 "static/bullet1.png", "static/background.png", "static/heart.png",
                 "static/wall.png"]
imageList = [pygame.image.load(f).convert_alpha() for f in imageFileList]



gen = 0


class Game:

    def __init__(self, numRow=16, rows=1, waves=1, type2=0, type3=0, outputs=1, pop=50):
        self.background = imageList[7]
        self.player = ''
        self.level = ''
        self.score = 0
        self.outputs = outputs
        self.playing = True
        self.pop = pop
        self.playAgainVar = False
        self.screen = screen
        self.timer = 0
        self.counter = 0
        self.levelDetails = [numRow, rows, waves, type2, type3]

    def eval_genomes(self, genomes, config, oneGenome=False):
        global gen
        gen = 0
        bestGen = []
        ge = []
        nets = []
        for genome_id, genome in genomes:
            genome.fitness = 0
            if oneGenome == True:
                net = genome
            else:
                net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            ge.append(genome)

        reUseGenome = False
        if reUseGenome == True:
            nets.pop(0)
            ge.pop(0)
            local_dir = os.path.dirname(__file__)
            bestGenome_path = os.path.join(local_dir, 'pickles/' + 'best-f(M289.9)-d[16, 3, 3, 0, 0]-o[3]904666.pickle')
            with open(bestGenome_path, "rb") as f:
                genome = pickle.load(f)

            genome.fitness = 0
            #genomes = [(1, genome)]
            nets.insert(0, genome)
            ge.insert(0, genome)

        #Sacar el primr net y meter el favorito




        while self.pop > gen:
            self.player = Player()
            self.level = Level(numRow=self.levelDetails[0],
                               rows=self.levelDetails[1],
                               waves=self.levelDetails[2],
                               type2=self.levelDetails[3],
                               type3=self.levelDetails[4])
            self.score = 0
            self.timer = 0
            self.counter = 0

            gen += 1

            self.playAgainVar = False
            clock = pygame.time.Clock()
            MAX_FRAMETIME = 0.25
            accumulator = 0
            frametime = clock.tick(1000)
            run = True
            while run:
                frametime = clock.tick(1000) / 1000
                if frametime > MAX_FRAMETIME:
                    frametime = MAX_FRAMETIME
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
                        quit()
                        break
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            nets.pop(0)
                            ge.pop(0)
                            run = False

                self.timer += 1
                self.counter += 1
                accumulator += frametime
                playerInfo = self.player.main(0, False)
                enemysInfo = self.level.enemyDict
                enemysRectsDict = dict()
                heartInfo = self.player.heartDict
                scoreFunc = self.scoreText(self.score, 20, 30, "Score: ")
                posText = self.scoreText(playerInfo[1].x, 20, 60, "PosX: ")
                timeLKText = self.scoreText(self.timer, 20, 90, "TimeLK: ")
                genText = self.scoreText(gen, 20, 120, "Subject: ")
                timeText = self.scoreText(self.counter, 20, 150, "Time: ")

                for enemy in enemysInfo:
                    enemysRectsDict[enemy] = enemysInfo[enemy].main()

                for enemy in enemysInfo:
                    output = nets[0].activate((playerInfo[1].x + 50,
                                               playerInfo[1].x + 50 - enemysRectsDict[enemy].x,
                                               playerInfo[1].x + 50 - enemysRectsDict[enemy].x + 35))
                    #print(output)
                    if 950 >= playerInfo[1].x >= 0:
                        ge[0].fitness += 0.001
                        if output[0] > 0.5:
                            if output[2] > 0.5:
                                playerInfo = self.player.main(3, True)
                            else:
                                playerInfo = self.player.main(3, False)
                        if output[1] > 0.5:
                            if output[2] > 0.5:
                                playerInfo = self.player.main(-3, True)
                            else:
                                playerInfo = self.player.main(-3, False)

                        # if output[0] > 0.5:
                        #     playerInfo = self.player.main(3, True)
                        # elif output[0] < -0.5:
                        #     playerInfo = self.player.main(-3, True)
                        # elif 0 >= output[0] > -0.5:
                        #     playerInfo = self.player.main(3, False)
                        # elif 0 < output[0] < 0.5:
                        #     playerInfo = self.player.main(-3, False)
                    elif 950 < playerInfo[1].x:
                        # nets.pop(0)
                        # ge.pop(0)
                        # run = False
                        playerInfo = self.player.main(-3, False)
                        ge[0].fitness -= 0.6
                    elif 0 > playerInfo[1].x:
                        # nets.pop(0)
                        # ge.pop(0)
                        # run = False
                        playerInfo = self.player.main(3, False)
                        ge[0].fitness -= 0.6
                    break

                # ##################################################################################################
                #
                # output = nets[0].activate((playerInfo[1].x + 50,
                #                            playerInfo[1].x + 50 - enemysRectsDict[list(enemysInfo.keys())[-1]].x,
                #                            playerInfo[1].x + 50 - enemysRectsDict[list(enemysInfo.keys())[-1]].x + 35))
                # # print(output)
                # if 950 >= playerInfo[1].x >= 0:
                #     ge[0].fitness += 0.001
                #     if output[0] > 0.5:
                #         if output[2] > 0.5:
                #             playerInfo = self.player.main(3, True)
                #         else:
                #             playerInfo = self.player.main(3, False)
                #     if output[1] > 0.5:
                #         if output[2] > 0.5:
                #             playerInfo = self.player.main(-3, True)
                #         else:
                #             playerInfo = self.player.main(-3, False)
                #
                #     # if output[0] > 0.5:
                #     #     playerInfo = self.player.main(3, True)
                #     # elif output[0] < -0.5:
                #     #     playerInfo = self.player.main(-3, True)
                #     # elif 0 >= output[0] > -0.5:
                #     #     playerInfo = self.player.main(3, False)
                #     # elif 0 < output[0] < 0.5:
                #     #     playerInfo = self.player.main(-3, False)
                # elif 950 < playerInfo[1].x:
                #     # nets.pop(0)
                #     # ge.pop(0)
                #     # run = False
                #     playerInfo = self.player.main(-3, False)
                #     ge[0].fitness -= 0.2
                # elif 0 > playerInfo[1].x:
                #     # nets.pop(0)
                #     # ge.pop(0)
                #     # run = False
                #     playerInfo = self.player.main(3, False)
                #     ge[0].fitness -= 0.2
                #
                # ##################################################################################################

                if self.score == 0:
                    ge[0].fitness -= 0.01

                if (self.timer > 500 and self.counter<1500) or (self.timer>600 and self.counter>3200):
                    ge[0].fitness -= 0.2
                    if self.timer > 700:
                        ge[0].fitness -= 0.2
                    if self.score == 0:
                        ge[0].fitness -= 0.4

                if (self.timer > 1000 and self.levelDetails[2] == 1) or (self.timer > 500 and self.counter>3500):
                    nets.pop(0)
                    ge.pop(0)
                    run = False

                self.screen.blit(self.background, [0, 0])
                self.screen.blit(playerInfo[0], playerInfo[1])
                for bullet in list(playerInfo[2]):
                    bulletRect = playerInfo[2][bullet].main()
                    self.screen.blit(playerInfo[2][bullet].bullet, bulletRect)
                    bullDeleted = False
                    if bulletRect.y <= 0:  # era cero daba error
                        #ge[0].fitness -= 0.01
                        del playerInfo[2][bullet]
                        bullDeleted = True
                        for enemy in enemysInfo:
                            if enemysRectsDict[enemy].y >= 0:
                                ge[0].fitness -= 0.005
                                break

                    if bulletRect.collidedict(enemysRectsDict, True) is not None:
                        #print(bulletRect.collidedict(enemysRectsDict, True)[0])  # enemy killed
                        self.score += 1
                        self.timer = 0
                        ge[0].fitness += 2
                        enemysInfo[bulletRect.collidedict(enemysRectsDict, True)[0]].hitPoints -= 1
                        if bullDeleted == False:
                            del playerInfo[2][bullet]
                        if enemysInfo[bulletRect.collidedict(enemysRectsDict, True)[0]].hitPoints == 0:
                            del enemysInfo[bulletRect.collidedict(enemysRectsDict, True)[0]]
                            del enemysRectsDict[bulletRect.collidedict(enemysRectsDict, True)[0]]
                        else:
                            break



                for enemy in list(enemysInfo):
                    enemyRect = enemysInfo[enemy].main()
                    self.screen.blit(enemysInfo[enemy].enemy, enemyRect)
                    if enemyRect.y > 555:
                        self.score -= 1
                        del enemysInfo[enemy]
                        del enemysRectsDict[enemy]
                        self.player.hP -= 1
                        if self.player.hP > 0:
                            del heartInfo["heart" + str(self.player.hP + 1)]
                        if self.player.hP == 0:
                            self.playing = False
                            run = False

                if len(list(enemysInfo)) == 0 and self.player.hP == 10:
                    bestGen.append(ge[0].fitness)
                    print(bestGen)
                    nets.append(nets.pop(0))
                    ge.append(ge.pop(0))
                    run = False

                if self.player.hP < 10:
                    nets.pop(0)
                    ge.pop(0)
                    run = False

                for heart in list(heartInfo):
                    self.screen.blit(self.player.heart, heartInfo[heart])

                self.screen.blit(scoreFunc[0], scoreFunc[1])
                self.screen.blit(posText[0], posText[1])
                self.screen.blit(timeLKText[0], timeLKText[1])
                self.screen.blit(timeText[0], timeText[1])
                self.screen.blit(genText[0], genText[1])

                pygame.display.flip()

        bestFit = max(bestGen)
        print(bestFit)
        bestFitIndex = bestGen.index(bestFit)
        nets = [nets[bestFitIndex]]
        ge = [ge[bestFitIndex]]
        if oneGenome == False:
            t = time.time()
            f = "pickles/best-f(" + str(ge[0].fitness)[0:5] + ")" +\
                "-d" + str(self.levelDetails) +\
                "-o[" + str(self.outputs) + "]" +\
                str(t)[4:10] +\
                ".pickle"
            pickle.dump(nets[0], open(f, "wb"))


    def scoreText(self, score, x, y, txt):
        white = (255, 255, 255)

        font = pygame.font.Font('freesansbold.ttf', 28)
        text = font.render(txt + str(score), True, white)
        textRect = text.get_rect()
        textRect.center = (x, y)
        textRect.left = x
        return [text, textRect]


class Player:
    def __init__(self):
        self.speed = [0, 0]
        self.speedNum = 3
        self.image = imageList[0]
        self.player = pygame.transform.scale(self.image, (100, 100))
        self.playerRect = self.player.get_rect()
        self.playerRect.center = (500, 650)
        self.bulletsList = []
        self.bullets = 0
        self.hP = 10
        self.heart = pygame.transform.scale(imageList[8], (40, 40))
        self.heartRect = self.heart.get_rect()
        self.heartList = []
        self.heartDict = dict()
        self.bulletsDict = dict()
        self.counter = 0
        for i in range(self.hP):
            self.heartList.append("heart" + str(i + 1))

        for i in range(len(self.heartList)):
            self.heartDict[self.heartList[i]] = pygame.Rect(500 + (50 * i), 10, 40, 40)

    def main(self, speed, shoot):

        self.playerRect = self.playerRect.move([speed, 0])
        if self.counter > 0:
            self.counter -= 1

        if shoot == True and self.counter == 0:
            self.bullets += 1
            self.counter += 20
            self.bulletsList.append("bullet" + str(self.bullets))
            self.bulletsDict[self.bulletsList[-1]] = Bullet(self.playerRect.x, self.playerRect.y,
                                                            self.player.get_width())


        return [self.player, self.playerRect, self.bulletsDict]


class Bullet:
    def __init__(self, x, y, w):
        self.speed = [0, -2]
        self.image = imageList[6]
        self.bullet = pygame.transform.scale(self.image, (5, 10))
        self.bulletRect = self.bullet.get_rect()
        self.bulletRect.center = (x + (w / 2), y)

    def main(self):
        self.bulletRect = self.bulletRect.move(self.speed)

        return self.bulletRect


class Enemy:
    def __init__(self, x, y, w=35, h=35, type=1):
        self.speed = [0.19, 0.08]
        self.hitPoints = type
        self.image = imageList[type + 2]
        self.enemy = pygame.transform.scale(self.image, (w, h))
        self.enemyRect = self.enemy.get_rect()
        self.enemyRect.center = (x, y)
        self.pos = Vector2(x, y)
        self.velocity = Vector2(self.speed[0], self.speed[1])
        self.counter = 0
        self.maxCount = 200

    def main(self):
        if self.velocity == Vector2(self.speed[0], self.speed[1]):
            self.counter += 1
        if self.counter == self.maxCount:
            self.velocity = Vector2(-self.speed[0], self.speed[1])
        if self.velocity == Vector2(-self.speed[0], self.speed[1]):
            self.counter -= 1
        if self.counter == -self.maxCount:
            self.velocity = Vector2(self.speed[0], self.speed[1])

        self.pos += self.velocity
        self.enemyRect.center = self.pos

        return self.enemyRect


class Level:
    def __init__(self, numRow=16, rows=1, waves=1, type2=0, type3=0):
        self.rows = rows
        self.type2 = type2
        self.type3 = type3
        self.numPerRow = numRow
        self.spaceBetweenX = 50
        self.offsetX = 100
        self.enemyList = []
        self.waves = waves
        self.enemys = self.rows * self.numPerRow * self.waves
        self.enemysTotalScore = self.enemys + self.type2 + (self.type3 * 2)
        self.enemyDict = dict()

        for i in range(self.enemys):
            self.enemyList.append("enemy" + str(i))

        self.specialEnemyList = random.sample(self.enemyList, self.type2 + self.type3)
        self.type2List = self.specialEnemyList[:self.type2]
        self.type3List = self.specialEnemyList[self.type2:]

        for w in range(self.waves):
            for z in range(self.rows):
                for i in range(0 + (self.numPerRow * z) + (self.numPerRow * self.rows * w),
                               self.numPerRow + (self.numPerRow * z) + (self.numPerRow * self.rows * w)):
                    if len(self.enemyList) - 1 < i:
                        break

                    if self.enemyList[i] in self.type3List:
                        self.enemyDict[self.enemyList[i]] = Enemy((self.offsetX + (i * self.spaceBetweenX)) -
                                                                  (self.numPerRow * self.spaceBetweenX * z) -
                                                                  (self.numPerRow * self.spaceBetweenX * self.rows * w),
                                                                  100 - (z * 70) - (w * 500), type=3)
                    elif self.enemyList[i] in self.type2List:
                        self.enemyDict[self.enemyList[i]] = Enemy((self.offsetX + (i * self.spaceBetweenX)) -
                                                                  (self.numPerRow * self.spaceBetweenX * z) -
                                                                  (self.numPerRow * self.spaceBetweenX * self.rows * w),
                                                                  100 - (z * 70) - (w * 500), type=2)
                    else:
                        self.enemyDict[self.enemyList[i]] = Enemy((self.offsetX + (i * self.spaceBetweenX)) -
                                                                  (self.numPerRow * self.spaceBetweenX * z) -
                                                                  (self.numPerRow * self.spaceBetweenX * self.rows * w),
                                                                  100 - (z * 70) - (w * 500), type=1)


def run(config_file, game):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(game.eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


def reRun(config_file, game):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(game.eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


def runBest(config_file, game, genome_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    genomes = [(1, genome)]

    game.eval_genomes(genomes, config, oneGenome=True)


local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward.txt')
bestGenome_path = os.path.join(local_dir, 'pickles/' + 'best-f(M294.7)-d[16, 3, 3, 0, 0]-o[3]019240.pickle')


game1 = Game(numRow=16, rows=3, waves=3, type2=0, type3=0, outputs=3, pop=50)
#run(config_path, game1) # Train from 0
#reRun(config_path, game1)
runBest(config_path, game1, bestGenome_path)
