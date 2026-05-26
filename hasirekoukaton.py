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
GRAY = (180, 180, 180)
GREEN = (50, 220, 50)
RED = (255, 80, 80)

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
        self.double_jump_ready = False  # 2段ジャンプ可能回数
        self.jump_gauge = 0
        self.jump_gauge_max = 500

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = -self.jump_velocity
        elif self.double_jump_ready == True:
            self.double_jump_ready = False
            self.jump_gauge = 0
            self.velocity_y = -self.jump_velocity * 0.9

    def draw_jump_gauge(self, screen):
        """2段ジャンプのゲージを描画する関数"""
        # ゲージ背景
        jump_gauge_x = 5
        jump_gauge_y = 250
        jump_gauge_width = 90
        jump_gauge_height = 20

        pg.draw.rect(
            screen,
            GRAY,
            (jump_gauge_x, jump_gauge_y, jump_gauge_width, jump_gauge_height)
        )

        # ゲージ本体
        current_width = (
            jump_gauge_width * self.jump_gauge / self.jump_gauge_max
        )

        color = GREEN

        # MAX時は赤色
        if self.double_jump_ready:
            color = RED

        pg.draw.rect(
            screen,
            color,
            (jump_gauge_x, jump_gauge_y, current_width, jump_gauge_height)
        )

        # 枠線
        pg.draw.rect(
            screen,
            BLACK,
            (jump_gauge_x, jump_gauge_y, jump_gauge_width, jump_gauge_height),
            3
        )

    def update(self):
        if self.is_jumping:
            self.y += self.velocity_y
            self.velocity_y += self.gravity  # 重力を加算
            
            # 着地判定
            if self.y >= self.y_floor:
                self.y = self.y_floor
                self.is_jumping = False
                self.velocity_y = 0

        # 2段ジャンプゲージ蓄積
        if self.velocity_y == 0:
            if self.jump_gauge < self.jump_gauge_max:
                self.jump_gauge += 1
            
            if self.jump_gauge >= self.jump_gauge_max:
                    self.double_jump_ready = True

    def draw(self):
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

        self.passed = False

    def update(self):
        self.x -= self.speed  # 左へ自動移動

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.width, self.height)

class ScorePopup:
    """スコア加算時に一時的に表示されるテキストのエフェクト"""
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.timer = 30
    
    def update(self):
        self.timer -= 1
        self.y -= 0.5
    def is_dead(self):
        return self.timer <= 0


# --- メインゲームループ ---
def main():
    player = Player()
    obstacles = []
    popups = []

    # スコア機能
    score = 0
    game_speed = 7
    
    spawn_timer = 0
    next_spawn_time = random.randint(60, 120)
    
    game_over = False
    font = pg.font.Font(None, 40)

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

            # 障害物の移動と衝突判定・スコア判定
            for obstacle in obstacles[:]:
                obstacle.update()
                
                # 障害物がプレイヤーを通り過ぎた瞬間の判定
                if not obstacle.passed and (obstacle.x + obstacle.width < player.x):
                    score += 100
                    obstacle.passed = True
                    
                    # スコア表示の右側に "+100" ポップアップを生成
                    popups.append(ScorePopup(160, 10, "+100"))
                
                if obstacle.x + obstacle.width < 0:
                    obstacles.remove(obstacle)
                
                if player.get_rect().colliderect(obstacle.get_rect()):
                    game_over = True

            # ポップアップの更新と寿命が尽きたものの削除
            for popup in popups[:]:
                popup.update()
                if popup.is_dead():
                    popups.remove(popup)

        # --- 描画処理 ---
        # 背景画像（pg_bg.jpg）を描画
        screen.blit(bg_img, (0, 0))

        # キャラクター・障害物の描画
        player.draw()
        for obstacle in obstacles:
            obstacle.draw()
        player.draw_jump_gauge(screen)

        # スコア表示
        try:
            score_text = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (10, 10))
        except:
            pass

        # ポップアップの描画
        for popup in popups:
            try:
                popup_text = font.render(popup.text, True, (255,255,0))
                screen.blit(popup_text, (popup.x, popup.y))
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