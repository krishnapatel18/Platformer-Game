from settings import *  
from sprites import * 
from groups import AllSprites 
from support import * 
from reminder import Timer
from random import randint 

class Game: 
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((2000, 1000)) 
        pygame.display.set_caption('Platformer')
        self.clock = pygame.time.Clock()
        self.running = True 

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group() 
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # load game 
        self.load_assets() 
        self.setup() 

        # timer 
        self.bee_timer = Timer(1500, func = self.create_bee, autostart = True, repeat = True) 
        # self.bee_timer.activate()

    def create_bee(self): 
        Bee(frames = self.bee_frames, 
            pos = ((self.level_width + WINDOW_WIDTH), (randint(0, self.level_height))), 
            groups = (self.all_sprites, self.enemy_sprites), 
            speed = randint(300, 500))

    def create_bullet(self, pos, direction): 
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player) 
        self.audio['shoot'].play()

    def load_assets(self): 
        # graphics 
        self.player_frames = import_folder('images', 'player') 
        # print(self.player_frames)
        self.bullet_surf = import_image('images', 'gun', 'bullet') 
        # print(self.bullet_surf) 
        self.fire_surf = import_image('images', 'gun', 'fire') 
        self.bee_frames = import_folder('images', 'enemies', 'bee')
        self.worm_frames = import_folder('images', 'enemies', 'worm')

        # sounds 
        self.audio = audio_importer('audio') 
        self.audio['music'].play() 
        # print(self.audio) 

    def setup(self):
        tmx_map = load_pygame(join('data', 'maps', 'world.tmx')) 
        # print(tmx_map.width) 
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites)) 

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player': 
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.player_frames, self.create_bullet) 
        
        # Bee(self.bee_frames, (500, 600), self.all_sprites)
            if obj.name == 'Worm': 
                Worm(self.worm_frames, pygame.Rect(obj.x, obj.y, obj.width, obj.height), (self.all_sprites, self.enemy_sprites))

        self.audio['music'].play(loops = -1)

    def collision(self): 
        # bullets -> enimes 
        for bullet in self.bullet_sprites: 
            sprite_collision = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if sprite_collision: 
                self.audio['impact'].play()
                bullet.kill()
                for sprite in sprite_collision: 
                    sprite.destroy() 

        # enemies -> player 
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask): 
            self.running = False 

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 

            # update 
            self.bee_timer.update()
            self.all_sprites.update(dt) 
            self.collision()

            # draw 
            self.display_surface.fill(BG_COLOR)
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__': 
    game = Game()
    game.run() 