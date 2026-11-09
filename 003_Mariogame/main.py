import pygame
from enum import Enum, auto
import time
from pathlib import Path # ディレクトリ参照標準ライブラリ

pygame.init()
pygame.mixer.init()

# main.py が存在するディレクトリを取得
BASE_DIR = Path(__file__).resolve().parent # これで開いているフォルダによらず実行できる


# ファイルパス
BGM_PATH = BASE_DIR / "assets" / "sounds" / "titerman.mp3"
BLOCK_PATH = BASE_DIR / "assets" / "images" / "block.png"
KURIBO_PATH = BASE_DIR / "assets" / "images" / "kuribo.png"
KURIBO_D_PATH = BASE_DIR / "assets" / "images" / "kuribo_d.png"
MARIO_01_PATH = BASE_DIR / "assets" / "images" / "mario_01.png"
MARIO_02_PATH = BASE_DIR / "assets" / "images" / "mario_02.png"
MARIO_D_PATH = BASE_DIR / "assets" / "images" / "mario_d.png"
WALL_PATH = BASE_DIR / "assets" / "images" / "wall.png"

# BGM流す
pygame.mixer.music.load(str(BGM_PATH))
pygame.mixer.music.play(-1)

# 状態の定義
class Status(Enum):
    NORMAL = auto()
    DEADING = auto()
    DEAD = auto()
    TREADING = auto()

# 画面サイズを定義
W, H = 320, 270

# タイル数
TILE_X = 16
TILE_Y = 14

class Map():
    NOMOVE_X = 120 # スクロール処理

    def __init__(self):
        # マップを定義
        self.__data = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

        self.__imgs = {
            1: pygame.image.load(str(WALL_PATH)),
            2: pygame.image.load(str(BLOCK_PATH))
        }

        self.__drawmargin = 0
    
    def draw(self, win, rect):
        margin = 0
        if rect.x <= self.NOMOVE_X:
            startx = 0

        else:
            startx = rect.x // 20 - self.NOMOVE_X // 20
            margin = rect.x % 20

        self.__drawmargin = -startx * 20 - margin

        for y in range(TILE_Y):
            for x in range(startx, startx + TILE_X + 1):
                mapno = self.__data[y][x]
                if mapno > 0:
                    win.blit(self.__imgs[mapno], ((x - startx) * 20 - margin, y * 20))

    def chk_collision(self, rect):
        xidx = rect.x // 20
        yidx = rect.y // 20

        for y in range(2):
            for x in range(2):
                if self.__data[yidx + y][xidx + x] and rect.colliderect(pygame.Rect((xidx + x) * 20, (yidx + y) * 20, 20, 20)):
                    return True
        
        return False
    
    def get_drawx(self, rect):
        if rect.x < self.NOMOVE_X:
            x = rect.x
        else:
            x = self.NOMOVE_X
        return x
    
    def get_drawenemyx(self, rect):
        return rect.x + self.__drawmargin

class Mario(pygame.sprite.Sprite):
    ''' マリオのクラス
    '''
    WALK_ANIME_IDX = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    MAX_SPEED_X = 5    # x最高速度
    ACC_SPEED_X = 0.25 # x加速度

    def __init__(self, map):
        pygame.sprite.Sprite.__init__(self)

        # マップを保持
        self.__map = map
        # 左右どちら向きかのフラグを定義
        self.__isleft = False
        # 歩くインデックス
        self.__walkidx = 0
        # Y軸方向移動距離
        self.__vy = 0
        # X軸方向移動距離
        self.__vx = 0
        # マリオが地面にいるかどうか
        self.__on_ground = False
        # マリオの状態
        self.__status = Status.NORMAL
        # アニメ用カウンター
        self.__animecounter = 0

        # マリオの画像をよみこんでおく
        self.__imgs = [
            pygame.image.load(str(MARIO_01_PATH)),
            pygame.image.load(str(MARIO_02_PATH)),
            pygame.image.load(str(MARIO_D_PATH))
        ]

        self.image = self.__imgs[0]
        self.__rawrect = pygame.Rect(150, 180, 20, 20)
        self.rect = self.__rawrect
    
    @property
    def vy(self):
        return self.__vy
    
    @vy.setter
    def vy(self, value):
        self.__vy = value

    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, value):
        self.__status = value
    
    @property
    def rawrect(self):
        return self.__rawrect
    
    def __move(self):
        self.__walkidx += 1
        if self.__map.chk_collision(self.__rawrect):
            self.__rawrect.x = (self.__rawrect.x // 20 + (1 if self.__isleft else 0)) * 20

    def __right(self):
        self.__vx = (self.__vx + self.ACC_SPEED_X) if self.__vx < self.MAX_SPEED_X else self.MAX_SPEED_X

        if self.__isleft:
            self.__vx = 0

        self.__rawrect.x += self.__vx
        self.__isleft = False
        self.__walkidx += 1
        self.__move()
            
        
    def __left(self):
        self.__vx = (self.__vx - self.ACC_SPEED_X) if self.__vx > -1 * self.MAX_SPEED_X else -1 * self.MAX_SPEED_X

        if not self.__isleft:
            self.__vx = 0

        self.__rawrect.x += self.__vx
        self.__isleft = True
        self.__walkidx += 1
        self.__move()
            
    
    def __jump(self):
        if self.__on_ground:
            self.__vy = -12 # ジャンプ入力時、上方向の速度
            self.__on_ground = False # 地面についてない判定
    
    def __stop(self):
        self.__vx = self.__vx + self.ACC_SPEED_X * (1 if self.__isleft else -1)
        self.__rawrect.x += self.__vx
        self.__walkidx += 1
        self.__move()
    
    def __deading(self):
        if self.__animecounter == 0:
            self.__vy = -12
        
        if self.__animecounter > 10:
            self.__vy += 1
            self.__rawrect.y += self.__vy

        if self.__rawrect.y > H + 20:
            self.__status = Status.DEAD
            return
        
        self.__animecounter += 1

    def update(self):
        if self.__status == Status.DEAD:
            return
        
        if self.__status == Status.DEADING:
            self.image = self.__imgs[2]
            self.__deading()
            self.rect = pygame.Rect(self.__map.get_drawx(self.__rawrect), self.__rawrect.y, self.__rawrect.width, self.__rawrect.height)
            return
        
        # キーボードの状態を取得
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.__right()
        if keys[pygame.K_LEFT]:
            self.__left()

        if keys[pygame.K_SPACE]:
            self.__jump()
        else:
            if self.__vy >= 0:
                self.__status = Status.NORMAL
        
        if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT] and self.__vx != 0:
            self.__stop()
        
        # Y軸方向に移動
        #if not self.__on_ground:
        self.__vy += 1
        self.__rawrect.y += self.__vy

        if self.__map.chk_collision(self.__rawrect):
            self.__rawrect.y = (self.__rawrect.y // 20 + (1 if self.__vy < 0 else 0)) * 20
            if self.__vy > 0:
                self.__on_ground = True
                self.__vy = 0
            else:
                self.__vy = 1
            #if self.__rawrect.y >= 180:
            #    self.__rawrect.y = 180
            #    self.__on_ground = True
            #    self.__vy = 0

        self.image = pygame.transform.flip(self.__imgs[self.WALK_ANIME_IDX[self.__walkidx % 18]], self.__isleft, False)
        self.rect = pygame.Rect(self.__map.get_drawx(self.__rawrect), self.__rawrect.y, self.__rawrect.width, self.__rawrect.height)

class Kuribo(pygame.sprite.Sprite):
    WALK_SPEED = 10

    def __init__(self, x, y, mario, map):
        pygame.sprite.Sprite.__init__(self)

        # クリボーのX軸方向移動距離
        self.__map = map
        self.__dir = -2
        self.__vy = 0
        self.__walkidx = 0
        self.__imgs = [
            pygame.image.load(str(KURIBO_PATH)),
            pygame.image.load(str(KURIBO_D_PATH))
        ]
        self.__mario = mario
        # 状態
        self.__status = Status.NORMAL
        # 潰れたカウンター
        self.__collapsecount = 0

        self.image = self.__imgs[0]
        self.__rawrect = pygame.Rect(x, y, 20, 20)
        self.rect = self.__rawrect
    
    @property
    def status(self):
        return self.__status
    
    def update(self):
        if self.__mario.status == Status.DEADING:
            return
        
        if self.__status == Status.DEADING:
            self.image = self.__imgs[1]
            self.rect = pygame.Rect(self.__map.get_drawenemyx(self.__rawrect), self.__rawrect.y, self.__rawrect.width, self.__rawrect.height)
            self.__collapsecount += 1
            if self.__collapsecount == 30:
                self.__status = Status.DEAD
            return
        
        if self.__status == Status.DEAD:
            return

        self.__rawrect.x += self.__dir

        if self.__map.chk_collision(self.__rawrect):
            self.__rawrect.x = (self.__rawrect.x // 20 + (1 if self.__dir < 0 else 0)) * 20
            self.__dir *= -1

        if self.__rawrect.x <= 0 or self.__rawrect.x >= 1280 - self.__rawrect.width:
            self.__dir *= -1
        

        # Y軸方向移動
        self.__vy += 1
        self.__rawrect.y += self.__vy

        if self.__map.chk_collision(self.__rawrect):
            self.__rawrect.y = (self.__rawrect.y // 20 + (1 if self.__vy < 0 else 0)) * 20
            if self.__vy > 0:
                self.__vy = 0
            else:
                self.__vy = 1
        
        self.__walkidx += 1
        if self.__walkidx == self.WALK_SPEED:
            self.__walkidx = 0
        self.image = pygame.transform.flip(self.__imgs[0], self.__walkidx < self.WALK_SPEED // 2, False)

        if self.__rawrect.colliderect(self.__mario.rawrect):
            # 当たった時の処理をする
            if self.__mario.vy > 0: # 下方向の速度があれば敵がしぬ
                # 踏みつぶす
                self.__status = Status.DEADING
                self.__mario.status = Status.TREADING
                self.__mario.vy = -10
            else: # そうでなければマリオがしぬ
                if self.__mario.status != Status.TREADING:
                    self.__mario.status = Status.DEADING
        self.rect = pygame.Rect(self.__map.get_drawenemyx(self.__rawrect), self.__rawrect.y, self.__rawrect.width, self.__rawrect.height)

def init():
    # スプライトグループを定義
    group = pygame.sprite.RenderUpdates()
    # マップを構築
    map = Map()
    # マリオクラスを構築
    mario = Mario(map)
    # マリオをグループに追加
    group.add(mario)
    # クリボークラスを構築
    kuribos = [
        Kuribo(200, 120, mario, map),
        Kuribo(260, 150, mario, map),
        Kuribo(300, 150, mario, map),
    ]
    # クリボーをグループに追加
    for kuribo in kuribos:
        group.add(kuribo)
    
    return map, group, mario, kuribos

def main():
    ''' メイン関数
    '''

    # pygame初期化
    pygame.init()
    # 画面を作成
    win = pygame.display.set_mode((W, H))
    # クロックを生成
    clock = pygame.time.Clock()

    map, group, mario, kuribos = init()

    # イベントループ
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        
        # 背景を塗りつぶす
        win.fill((135, 206, 235))
        
        # グループを更新
        group.update()

        # マリオが死んだかのチェック
        if mario.status == Status.DEAD:
            
            time.sleep(2) # ゲーム処理を2sとめる
            map, group, mario, kuribos = init() # それぞれ初期値にもどす？
            continue

        # 死んでる敵をグループから削除
        for kuribo in kuribos:
            if kuribo.status == Status.DEAD:
                group.remove(kuribo)
        
        # マップを描画
        map.draw(win, mario.rawrect)

        # グループを描画
        group.draw(win)

        # 画面全体を更新
        pygame.display.flip()

        # フレームレートを設定
        clock.tick(30)

    # Pygameの終了処理
    pygame.quit()

if __name__ == '__main__':
    main()

