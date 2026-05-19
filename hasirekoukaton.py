import pygame as pg
import random
import sys
import os

# --- 初期設定 ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pg.init()

# 画面サイズ
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("こうかとんランゲーム")

# カラー定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  #無敵UI用の赤
CYAN = (0, 255, 255)  #無敵エフェクト・ゲージ用の水色

# フレームレート管理
clock = pg.time.Clock()
FPS = 60

# --- 画像の読み込み ---
try:
    player_run = pg.image.load("./fig/run.png").convert_alpha()
    
    # 障害物と背景
    obstacle_img = pg.image.load("./fig/alien.png").convert_alpha()
    bg_img = pg.image.load("./fig/pg_bg.jpg").convert()
    
    # 背景画像を画面サイズにフィットさせる
    bg_img = pg.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
except pg.error as e:
    print(f"画像が見つかりません。フォルダ構成を確認してください: {e}")
    pg.quit()
    sys.exit()

# --- クラス定義 ---

class Player:
    """プレイヤー（こうかとん）のクラス"""
    def __init__(self):
        # 縦長の画像(約3:4)に合わせてサイズを横60px、高さ80pxに最適化
        self.width = 60
        self.height = 80
        
        # 画像をリサイズして保持
        self.img_run = pg.transform.scale(player_run, (self.width, self.height))
        
        self.x = 100
        self.y_floor = SCREEN_HEIGHT - 80 - self.height  # 地面の上のY座標
        self.y = self.y_floor
        
        # ジャンプ関連の物理パラメータ
        self.is_jumping = False
        self.jump_velocity = 15  # 初速度
        self.velocity_y = 0
        self.gravity = 0.75       # 重力
        # 無敵関係
        self.invincible_count = 3  #無敵の回数
        self.invincible_timer = 0  #無敵の効果時間
        self.is_invincible = False #無敵時間かどうか
        self.blink_timer = 0 #点滅エフェクト

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = -self.jump_velocity
    
    def activate_invincible(self):
        #無敵発動メゾット
        if not self.is_invincible and self.invincible_count > 0:
            self.is_invincible = True
            self.invincible_count -= 1
            self.invincible_timer = 180

    def update(self):
        if self.is_jumping:
            self.y += self.velocity_y
            self.velocity_y += self.gravity  # 重力を加算
            
            # 着地判定
            if self.y >= self.y_floor:
                self.y = self.y_floor
                self.is_jumping = False
                self.velocity_y = 0

        #無敵タイマーの更新
        if self.is_invincible:
            self.invincible_timer -= 1
            self.blink_timer += 1
            if self.invincible_timer <= 0:
                self.is_invincible = False
                self.invincible_timer = 0

    def draw(self):
        #無敵状態なら点滅
        if self.is_invincible and (self.blink_timer // 4) % 2 == 0:
            pass
        else:
            current_image = self.img_run
            screen.blit(current_image, (self.x, self.y))
        # 正しい縦横比に修正された run.png を表示
        current_image = self.img_run
        screen.blit(current_image, (self.x, self.y))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.width, self.height)


class Obstacle:
    """障害物（エイリアン）のクラス"""
    def __init__(self, speed):
        # 画像サイズをゲーム用に調整
        self.width = 50
        self.height = 50
        self.image = pg.transform.scale(obstacle_img, (self.width, self.height))
        
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - 80 - self.height
        self.speed = speed

    def update(self):
        self.x -= self.speed  # 左へ自動移動

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.width, self.height)


# --- メインゲームループ ---
def main():
    player = Player()
    obstacles = []
    
    # スコア機能
    score = 0
    game_speed = 7
    
    spawn_timer = 0
    next_spawn_time = random.randint(60, 120)
    
    game_over = False
    font = pg.font.Font(None, 40)
    small_font = pg.font.SysFont("msgothic", 30)  #無敵表示用のフォント


    while True:
        # --- イベント処理 ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    if game_over:
                        main()  # リスタート
                        return
                    else:
                        player.jump()
                #左シフトキーで無敵発動
                if event.key == pg.K_LSHIFT and not game_over:
                    player.activate_invincible()

        if not game_over:
            # --- 更新処理 ---
            player.update()
            score += 1
            
            # 障害物の生成管理
            spawn_timer += 1
            if spawn_timer >= next_spawn_time:
                obstacles.append(Obstacle(game_speed))
                spawn_timer = 0
                next_spawn_time = random.randint(50, 100)

            # 障害物の移動と衝突判定
            for obstacle in obstacles[:]:
                obstacle.update()
                if obstacle.x + obstacle.width < 0:
                    obstacles.remove(obstacle)
                #プレイヤーが無敵の時は衝突判定をスルー
                if player.get_rect().colliderect(obstacle.get_rect()):
                    if not player.is_invincible:
                        game_over = True
                    

        # --- 描画処理 ---
        # 背景画像（pg_bg.jpg）を描画
        screen.blit(bg_img, (0, 0))

        # キャラクター・障害物の描画
        player.draw()
        for obstacle in obstacles:
            obstacle.draw()

        # スコア表示
        try:
            score_text = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (10, 10))
            #無敵回数の表示
            inv_text = small_font.render(f"無敵 (LShift): {player.invincible_count}", True, RED if player.invincible_count == 0 else BLACK)
            screen.blit(inv_text, (10, 45))
            #無敵発動中の残り時間ゲージ表示
            gauge_width = int((player.invincible_timer / 180) * 100)
            pg.draw.rect(screen, BLACK, (10, 75, 100, 10), 1) # 枠線
            pg.draw.rect(screen, CYAN, (11, 76, gauge_width - 2, 8)) # 中身
        except:
            pass

        # ゲームオーバー画面
        if game_over:
            try:
                over_text = font.render("GAME OVER - Press SPACE to Restart", True, BLACK)
                text_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(over_text, text_rect)
            except:
                pass

        pg.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()