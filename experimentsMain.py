import math
import sys, pygame
from pygame.math import Vector2
import random
import cProfile as Profile

pygame.init()
pygame.display.set_caption('Luca Space Invaders')
size = width, height = 1000, 800
black = 0, 0, 0
# flags = FULLSCREEN | DOUBLEBUF
# screen = pygame.display.set_mode(size, flags, 16)
screen = pygame.display.set_mode(size)
imageFileList = ["static/player1.png", "static/player2.png", "static/player3.png",
                 "static/alien1.png", "static/alien2.png", "static/alien3.png",
                 "static/bullet1.png", "static/background.png", "static/heart.png",
                 "static/wall.png"]
imageList = [pygame.image.load(f).convert_alpha() for f in imageFileList]


class Game:
    def __init__(self, player, level):
        self.background = imageList[7]
        self.player = player
        self.level = level
        self.wall = Wall()
        self.score = 0
        self.playing = True
        self.playAgainVar = False
        self.screen = screen
        self.allsprites = pygame.sprite.LayeredDirty()
        self.timer = 0

    def main(self):
        self.playAgainVar = False
        clock = pygame.time.Clock()
        MAX_FRAMETIME = 0.25
        accumulator = 0
        frametime = clock.tick()
        playerInfo = self.player.main()
        enemysInfo = self.level.enemyDict
        wallInfo = self.wall.drawWord()

        self.allsprites.add(self.player)

        # for wall in list(wallInfo):
        #     self.allsprites.add(wallInfo[wall])

        for enemy in list(enemysInfo):
            self.allsprites.add(enemysInfo[enemy])

        self.allsprites.clear(self.screen, self.background)

        while self.playing:
            self.timer += 1
            frametime = clock.tick() / 1000
            if frametime > MAX_FRAMETIME:
                frametime = MAX_FRAMETIME

            # if self.timer == 700:
            #     for enemy in list(enemysInfo)[51:102]:
            #         self.allsprites.add(enemysInfo[enemy])

            accumulator += frametime
            self.drawObjects()

        self.playAgain()

    def drawObjects(self):
        playerInfo = self.player.main()
        enemysInfo = self.level.enemyDict
        enemysRectsDict = dict()
        wallInfo = self.wall.drawWord()
        heartInfo = self.player.heartDict
        scoreFunc = self.scoreText(self.score)
        # self.allsprites.add(self.player)
        for enemy in enemysInfo:
            enemysRectsDict[enemy] = enemysInfo[enemy].main()
        self.screen.blit(self.background, [0, 0])
        #self.screen.blit(playerInfo[0], playerInfo[1])
        for bullet in list(playerInfo[2]):
            bulletRect = playerInfo[2][bullet].main()
            self.allsprites.add(playerInfo[2][bullet])
            #self.screen.blit(playerInfo[2][bullet].bullet, bulletRect)

            if bulletRect.collidedict(enemysRectsDict, True) is not None:
                print(bulletRect.collidedict(enemysRectsDict, True)[0])
                self.score += 1
                enemysInfo[bulletRect.collidedict(enemysRectsDict, True)[0]].hitPoints -= 1
                playerInfo[2][bullet].image = pygame.Surface([35, 35])
                playerInfo[2][bullet].image.set_alpha(128)
                del playerInfo[2][bullet]
                if enemysInfo[bulletRect.collidedict(enemysRectsDict, True)[0]].hitPoints == 0:
                    enemysInfo[bulletRect.collidedict(enemysRectsDict, True)[0]].image = pygame.Surface([35, 35])
                    enemysInfo[bulletRect.collidedict(enemysRectsDict, True)[0]].image.set_alpha(128)
                    del enemysInfo[bulletRect.collidedict(enemysRectsDict, True)[0]]
                    del enemysRectsDict[bulletRect.collidedict(enemysRectsDict, True)[0]]
                else:
                    break

            if bulletRect.y <= 0:
                del playerInfo[2][bullet]

        for enemy in list(enemysInfo):
            enemyRect = enemysInfo[enemy].main()
            # self.allsprites.add(enemysInfo[enemy])
            #self.screen.blit(enemysInfo[enemy].enemy, enemyRect)
            if enemyRect.y > 555:
                self.score -= 1
                del enemysInfo[enemy]
                del enemysRectsDict[enemy]
                self.player.hP -= 1
                if self.player.hP > 0:
                    del heartInfo["heart" + str(self.player.hP + 1)]
                if self.player.hP == 0:
                    self.playing = False

        for heart in list(heartInfo):
            self.screen.blit(self.player.heart, heartInfo[heart])

        for wall in list(wallInfo):
            wallInfo[wall].dirty = 0

        self.screen.blit(scoreFunc[0], scoreFunc[1])



        self.allsprites.update()

        rects = self.allsprites.draw(self.screen)
        pygame.display.update(rects)

    def playAgain(self):
        white = (255, 255, 255)
        blue = (69, 88, 140)
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render("Play Again", True, white, blue)
        text2 = font.render("Close Game", True, white, blue)
        text2R = text2.get_rect()
        textR = text.get_rect()
        textR.center = (400, 300)
        text2R.center = (600, 300)
        while self.playAgainVar == False:
            self.screen.fill(black)
            self.screen.blit(text, textR)
            self.screen.blit(text2, text2R)
            x, y = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        if text2R.collidepoint(x, y):
                            self.playAgainVar = True
                        if textR.collidepoint(x, y):
                            # self.playing = True
                            # self.main()
                            Game(Player(), Level(rows=3, waves=3, type2=3, type3=4)).main()

            pygame.display.flip()

    def scoreText(self, score):
        white = (255, 255, 255)

        font = pygame.font.Font('freesansbold.ttf', 28)
        text = font.render(str(score), True, white)
        textRect = text.get_rect()
        textRect.center = (30, 30)
        return [text, textRect]


class Player(pygame.sprite.DirtySprite):
    def __init__(self):
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 1
        self.speed = [0, 0]
        self.speedNum = 3
        self.img = imageList[0]
        self.image = pygame.transform.scale(self.img, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.center = (500, 650)
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

        print(self.heartDict)

    def main(self):
        self.dirty = 1

        self.rect = self.rect.move(self.speed)
        if self.counter > 0:
            self.counter -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.counter == 0:
                    self.bullets += 1
                    self.counter += 20
                    self.bulletsList.append("bullet" + str(self.bullets))
                    self.bulletsDict[self.bulletsList[-1]] = Bullet(self.rect.x, self.rect.y,
                                                                    self.image.get_width())

        keys = pygame.key.get_pressed()

        if (pygame.K_RIGHT and pygame.K_LEFT) not in keys:
            self.speed[0] = 0

        if keys[pygame.K_LEFT] and (self.rect.x > -(self.image.get_width() / 2)):
            self.speed[0] = -self.speedNum

        if keys[pygame.K_RIGHT] and (self.rect.x < width - (self.image.get_width() / 2)):
            self.speed[0] = self.speedNum

        return [self.image, self.rect, self.bulletsDict]


class Bullet(pygame.sprite.DirtySprite):
    def __init__(self, x, y, w):
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 1
        self.speed = [0, -2]
        self.img = imageList[6]
        self.image = pygame.transform.scale(self.img, (5, 10))
        self.rect = self.image.get_rect()
        self.rect.center = (x + (w / 2), y)

    def main(self):
        self.dirty = 1
        self.rect = self.rect.move(self.speed)

        return self.rect


class WallPiece(pygame.sprite.DirtySprite):
    def __init__(self, x, y):
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 1
        self.image = pygame.Surface([2, 50])
        self.image.fill((255, 255, 0))
        # self.wallPiece = pygame.transform.scale(self.image, (2, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Wall(pygame.sprite.DirtySprite):
    def __init__(self):
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 1
        self.wallList = []
        self.wallDict = dict()

    # 100 x 300

    def drawLine(self, x):

        for i in range(5):
            self.wallList.append("wall" + str(len(self.wallList)))
            self.wallDict[self.wallList[-1]] = WallPiece(x, (450+(25*i)))

    def drawLetter(self, x):

        for i in range(20):
            self.drawLine(x+(i*6))

    def drawWord(self):
        self.dirty = 1
        self.drawLetter(100)
        # self.drawLetter(250)
        # self.drawLetter(400)
        # self.drawLetter(550)
        # self.drawLetter(700)

        return self.wallDict


class Enemy(pygame.sprite.DirtySprite):
    def __init__(self, x, y, w=35, h=35, type=1):
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 0
        self.speed = [0.19, 0.08]
        self.hitPoints = type
        self.img = imageList[type + 2]
        self.image = pygame.transform.scale(self.img, (w, h))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = Vector2(x, y)
        self.velocity = Vector2(self.speed[0], self.speed[1])
        self.counter = 0
        self.maxCount = 200

    def main(self):
        self.dirty = 1
        if self.velocity == Vector2(self.speed[0], self.speed[1]):
            self.counter += 1
        if self.counter == self.maxCount:
            self.velocity = Vector2(-self.speed[0], self.speed[1])
        if self.velocity == Vector2(-self.speed[0], self.speed[1]):
            self.counter -= 1
        if self.counter == -self.maxCount:
            self.velocity = Vector2(self.speed[0], self.speed[1])

        self.pos += self.velocity
        self.rect.center = self.pos

        return self.rect


class Level:
    def __init__(self, rows, type2=0, type3=0, waves=1):
        self.rows = rows
        self.type2 = type2
        self.type3 = type3
        self.numPerRow = 17
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
                    print(i)
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


player1 = Player()

level1 = Level(rows=3, waves=3, type2=3, type3=4)

game1 = Game(player1, level1)


Profile.run('game1.main()')

#game1.main()
