import pygame
import random
import sys
import math
import json
import os

# Pygame başlat
pygame.init()
pygame.mixer.init()

# Renkler
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)
BLUE = (0, 120, 215)
RED = (231, 76, 60)
GREEN = (46, 204, 113)
YELLOW = (241, 196, 15)
PURPLE = (155, 89, 182)
ORANGE = (230, 126, 34)
CYAN = (52, 152, 219)

COLORS = [BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, CYAN]

# Oyun sabitleri
CELL_SIZE = 40
GRID_SIZE = 8
MARGIN = 2
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
GRID_X = 50
GRID_Y = 50

# Zorluk seviyeleri
DIFFICULTIES = {
    'KOLAY': {
        'grid_size': 8,
        'target_score': 500,
        'color': GREEN,
        'multiplier': 1.0
    },
    'NORMAL': {
        'grid_size': 8,
        'target_score': 1000,
        'color': YELLOW,
        'multiplier': 1.5
    },
    'ZOR': {
        'grid_size': 8,
        'target_score': 2000,
        'color': RED,
        'multiplier': 2.0
    }
}

# Blok şekilleri
SHAPES = [
    [[1]],
    [[1, 1]],
    [[1], [1]],
    [[1, 1, 1]],
    [[1], [1], [1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 1], [0, 1, 0]],
]

class Particle:
    """Parçacık efekti için sınıf"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = 60
        self.size = random.randint(3, 8)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Yerçekimi
        self.life -= 1
        self.size = max(1, self.size - 0.1)
        
    def draw(self, screen):
        alpha = int(255 * (self.life / 60))
        surf = pygame.Surface((int(self.size * 2), int(self.size * 2)))
        surf.set_alpha(alpha)
        surf.fill(self.color)
        screen.blit(surf, (int(self.x), int(self.y)))
        
    def is_alive(self):
        return self.life > 0

class AnimatedCell:
    """Animasyonlu hücre sınıfı"""
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.scale = 1.0
        self.alpha = 255
        self.animation_type = 'clear'
        
    def update(self):
        if self.animation_type == 'clear':
            self.scale += 0.05
            self.alpha -= 15
        elif self.animation_type == 'place':
            if self.scale < 1.0:
                self.scale += 0.1
            else:
                self.scale = 1.0
                
    def draw(self, screen):
        x = GRID_X + self.col * (CELL_SIZE + MARGIN)
        y = GRID_Y + self.row * (CELL_SIZE + MARGIN)
        
        size = int(CELL_SIZE * self.scale)
        offset = (CELL_SIZE - size) // 2
        
        surf = pygame.Surface((size, size))
        surf.set_alpha(max(0, int(self.alpha)))
        surf.fill(self.color)
        screen.blit(surf, (x + offset, y + offset))
        
    def is_done(self):
        if self.animation_type == 'clear':
            return self.alpha <= 0
        elif self.animation_type == 'place':
            return self.scale >= 1.0
        return True

class SoundManager:
    """Ses yöneticisi"""
    def __init__(self):
        self.sounds = {}
        self.music_channel = None
        self.music_enabled = True
        self.sfx_enabled = True
        self.master_volume = 1.0
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.create_sounds()
        self.create_background_music()
        
    def create_sounds(self):
        """Basit ses efektleri oluştur"""
        self.create_tone('place', 440, 0.1)
        self.create_tone('clear', 880, 0.15)
        self.create_tone('gameover', 220, 0.3)
        self.create_tone('success', 660, 0.2)
        
    def create_tone(self, name, frequency, duration):
        """Basit ton oluştur"""
        try:
            import numpy as np
            sample_rate = 22050
            n_samples = int(round(duration * sample_rate))
            
            t = np.linspace(0, duration, n_samples, False)
            wave = np.sin(frequency * t * 2 * np.pi)
            
            fade = np.linspace(1, 0, n_samples)
            wave = wave * fade
            
            wave = (wave * 32767).astype(np.int16)
            
            stereo_wave = np.column_stack((wave, wave))
            
            sound = pygame.sndarray.make_sound(stereo_wave)
            self.sounds[name] = sound
        except:
            self.sounds[name] = None
    
    def create_background_music(self):
        """Arkada çalışacak melodi oluştur"""
        try:
            import numpy as np
            
            # Melodi notu frekansları (Do Major Skalası)
            notes = {
                'C': 262,   # Do
                'D': 294,   # Re
                'E': 330,   # Mi
                'F': 349,   # Fa
                'G': 392,   # Sol
                'A': 440,   # La
                'B': 494,   # Si
            }
            
            # Melodi: Do-Mi-Sol-La-Sol-Mi-Do (Block Blast teması)
            melody = ['C', 'E', 'G', 'A', 'G', 'E', 'C', 'D', 'E', 'F', 'G']
            durations = [0.4, 0.4, 0.4, 0.8, 0.4, 0.4, 0.4, 0.2, 0.2, 0.2, 0.8]
            
            sample_rate = 22050
            total_samples = 0
            wave_parts = []
            
            # Her nota için dalga oluştur
            for note, duration in zip(melody, durations):
                frequency = notes[note]
                n_samples = int(round(duration * sample_rate))
                
                t = np.linspace(0, duration, n_samples, False)
                # Daha zengin ses için birleşik dalga
                wave = (np.sin(frequency * t * 2 * np.pi) + 
                       0.3 * np.sin(frequency * 2 * t * 2 * np.pi))
                
                # Fade in/out
                fade_len = int(n_samples * 0.1)
                if fade_len > 0:
                    fade_in = np.linspace(0, 1, fade_len)
                    fade_out = np.linspace(1, 0, fade_len)
                    wave[:fade_len] *= fade_in
                    wave[-fade_len:] *= fade_out
                
                wave_parts.append(wave)
            
            # Tüm notaları birleştir
            full_wave = np.concatenate(wave_parts)
            full_wave = (full_wave * 32767).astype(np.int16)
            
            stereo_wave = np.column_stack((full_wave, full_wave))
            self.sounds['music'] = pygame.sndarray.make_sound(stereo_wave)
        except:
            self.sounds['music'] = None
    
    def play_music(self):
        """Müziği sürekli çal"""
        if 'music' in self.sounds and self.sounds['music'] is not None and self.music_enabled:
            try:
                # -1 = sonsuz döngü
                self.sounds['music'].play(-1)
                self.sounds['music'].set_volume(self.master_volume * self.music_volume)
            except:
                pass
    
    def stop_music(self):
        """Müziği durdur"""
        if 'music' in self.sounds and self.sounds['music'] is not None:
            try:
                self.sounds['music'].stop()
            except:
                pass
    
    def set_master_volume(self, volume):
        """Master ses seviyesini ayarla (0.0 - 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        self.update_all_volumes()
    
    def set_music_volume(self, volume):
        """Müzik ses seviyesini ayarla (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        self.update_music_volume()
    
    def set_sfx_volume(self, volume):
        """Efekt ses seviyesini ayarla (0.0 - 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def update_all_volumes(self):
        """Tüm ses seviyelerini güncelle"""
        self.update_music_volume()
    
    def update_music_volume(self):
        """Müzik ses seviyesini güncelle"""
        if 'music' in self.sounds and self.sounds['music'] is not None:
            try:
                vol = self.master_volume * self.music_volume if self.music_enabled else 0
                self.sounds['music'].set_volume(vol)
            except:
                pass
    
    def toggle_music(self):
        """Müziği aç/kapat"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.play_music()
        else:
            self.stop_music()
    
    def toggle_sfx(self):
        """Ses efektlerini aç/kapat"""
        self.sfx_enabled = not self.sfx_enabled
        
    def play(self, sound_name):
        """Ses çal"""
        if not self.sfx_enabled:
            return
        
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            try:
                self.sounds[sound_name].set_volume(self.master_volume * self.sfx_volume)
                self.sounds[sound_name].play()
            except:
                pass

class Block:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.dragging = False
        self.x = 0
        self.y = 0
        self.scale = 0.0
        
    def update_scale(self):
        """Spawn animasyonu"""
        if self.scale < 1.0:
            self.scale += 0.05
        else:
            self.scale = 1.0

class FloatingText:
    """Yüzen skor metni"""
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.life = 60
        self.font_size = 36
        
    def update(self):
        self.y -= 2
        self.life -= 1
        self.alpha = int(255 * (self.life / 60))
        self.font_size += 0.5
        
    def draw(self, screen):
        font = pygame.font.Font(None, int(self.font_size))
        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(self.alpha)
        rect = text_surface.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text_surface, rect)
        
    def is_alive(self):
        return self.life > 0

class PowerUp:
    """Güç-up sınıfı"""
    def __init__(self, power_type, x, y):
        self.type = power_type  # 'bomb', 'lightning', 'rainbow'
        self.x = x
        self.y = y
        self.size = 60
        self.active = True
        self.pulse = 0
        
    def update(self):
        self.pulse += 0.05
        
    def draw(self, screen):
        """Güç-up ikonunu çiz"""
        pulse_scale = 1.0 + math.sin(self.pulse) * 0.1
        size = int(self.size * pulse_scale)
        offset = (self.size - size) // 2
        
        # Arka plan
        if self.type == 'bomb':
            color = RED
            icon = "💣"
        elif self.type == 'lightning':
            color = YELLOW
            icon = "⚡"
        else:  # rainbow
            color = PURPLE
            icon = "🌈"
        
        surf = pygame.Surface((size, size))
        surf.fill(color)
        screen.blit(surf, (self.x + offset, self.y + offset))
        
        # İkon
        font = pygame.font.Font(None, int(size - 10))
        try:
            text = font.render(icon, True, WHITE)
            text_rect = text.get_rect(center=(self.x + self.size//2, self.y + self.size//2))
            screen.blit(text, text_rect)
        except:
            pass
    
    def is_clicked(self, mouse_x, mouse_y):
        """Güç-up tıklandı mı?"""
        return (self.x <= mouse_x <= self.x + self.size and
                self.y <= mouse_y <= self.y + self.size)

class ScoreManager:
    """Skor ve istatistikleri yönet"""
    def __init__(self):
        self.stats_file = "block_blast_stats.json"
        self.stats = self.load_stats()
        
    def load_stats(self):
        """İstatistikleri yükle ve doğrula"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
                # Verileri doğrula
                return self.validate_stats(stats)
            except:
                return self.get_default_stats()
        return self.get_default_stats()
    
    def validate_stats(self, stats):
        """İstatistikleri doğrula - hileli veriler tespit et"""
        # Geçerli alanlar
        valid_difficulties = {'KOLAY', 'NORMAL', 'ZOR'}
        
        # Eksik zorluk seviyeleri varsa ekle
        for difficulty in valid_difficulties:
            if difficulty not in stats:
                stats[difficulty] = {'high_score': 0, 'games_played': 0}
            else:
                # Veri tipleri doğru mu?
                if not isinstance(stats[difficulty], dict):
                    stats[difficulty] = {'high_score': 0, 'games_played': 0}
                    continue
                
                # high_score doğrulaması
                if 'high_score' not in stats[difficulty]:
                    stats[difficulty]['high_score'] = 0
                else:
                    try:
                        score = int(stats[difficulty]['high_score'])
                        # Mantık dışı yüksek skorları sınırla (999999 üzeri şüpheli)
                        if score > 999999 or score < 0:
                            stats[difficulty]['high_score'] = 0
                        else:
                            stats[difficulty]['high_score'] = score
                    except (ValueError, TypeError):
                        stats[difficulty]['high_score'] = 0
                
                # games_played doğrulaması
                if 'games_played' not in stats[difficulty]:
                    stats[difficulty]['games_played'] = 0
                else:
                    try:
                        games = int(stats[difficulty]['games_played'])
                        # Mantık dışı oyun sayılarını sınırla
                        if games > 100000 or games < 0:
                            stats[difficulty]['games_played'] = 0
                        else:
                            stats[difficulty]['games_played'] = games
                    except (ValueError, TypeError):
                        stats[difficulty]['games_played'] = 0
        
        # İzin verilmeyen zorluk seviyeleri kaldır
        keys_to_remove = [key for key in stats if key not in valid_difficulties]
        for key in keys_to_remove:
            del stats[key]
        
        return stats
    
    def get_default_stats(self):
        """Varsayılan istatistikler"""
        return {
            'KOLAY': {'high_score': 0, 'games_played': 0},
            'NORMAL': {'high_score': 0, 'games_played': 0},
            'ZOR': {'high_score': 0, 'games_played': 0}
        }
    
    def save_stats(self):
        """İstatistikleri kaydet"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass
    
    def update_score(self, difficulty, score):
        """Skoru güncelle - yalnızca oyun içinden çağrılır"""
        # Giriş doğrulaması
        if difficulty not in DIFFICULTIES:
            return
        
        if not isinstance(score, int) or score < 0:
            return
        
        # Mantık dışı skorları reddet
        if score > 999999:
            return
        
        # Sadece yeni rekor ise güncelle
        if score > self.stats[difficulty]['high_score']:
            self.stats[difficulty]['high_score'] = score
        
        self.stats[difficulty]['games_played'] += 1
        self.save_stats()
    
    def get_high_score(self, difficulty):
        """En yüksek skoru getir"""
        if difficulty in self.stats:
            return self.stats[difficulty]['high_score']
        return 0
    
    def get_games_played(self, difficulty):
        """Oynanan oyun sayısını getir"""
        if difficulty in self.stats:
            return self.stats[difficulty]['games_played']
        return 0

class Game:
    def __init__(self, difficulty='NORMAL'):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Block Blast - Zorluk Seviyeleri")
        self.clock = pygame.time.Clock()
        
        self.difficulty = difficulty
        self.difficulty_settings = DIFFICULTIES[difficulty]
        self.target_score = self.difficulty_settings['target_score']
        self.score_multiplier = self.difficulty_settings['multiplier']
        
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.blocks = [Block() for _ in range(3)]
        self.next_blocks = [Block() for _ in range(3)]
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.combo_duration = 180
        self.selected_block = None
        self.game_over = False
        self.particles = []
        self.animated_cells = []
        self.floating_texts = []
        self.sound_manager = SoundManager()
        self.score_manager = ScoreManager()
        self.position_blocks()
        
        # Power-up sistemi
        self.powerups = {'bomb': 0, 'lightning': 0, 'rainbow': 0}
        self.active_powerups = []
        
        # Müziği başlat
        self.sound_manager.play_music()
        
    def position_blocks(self):
        """Blokları ekranın altına yerleştir"""
        start_x = 100
        y_pos = WINDOW_HEIGHT - 150
        spacing = 180
        
        for i, block in enumerate(self.blocks):
            block.x = start_x + i * spacing
            block.y = y_pos
            
    def create_particles(self, row, col, color):
        """Parçacık efekti oluştur"""
        x = GRID_X + col * (CELL_SIZE + MARGIN) + CELL_SIZE // 2
        y = GRID_Y + row * (CELL_SIZE + MARGIN) + CELL_SIZE // 2
        
        for _ in range(10):
            self.particles.append(Particle(x, y, color))
            
    def draw_grid(self):
        """Oyun ızgarasını çiz"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_X + col * (CELL_SIZE + MARGIN)
                y = GRID_Y + row * (CELL_SIZE + MARGIN)
                
                if self.grid[row][col]:
                    pulse = math.sin(pygame.time.get_ticks() * 0.001) * 2
                    pygame.draw.rect(self.screen, self.grid[row][col], 
                                   (x, y, CELL_SIZE, CELL_SIZE))
                    inner_rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                    lighter_color = tuple(min(255, c + 30) for c in self.grid[row][col])
                    pygame.draw.rect(self.screen, lighter_color, inner_rect)
                else:
                    pygame.draw.rect(self.screen, LIGHT_GRAY, 
                                   (x, y, CELL_SIZE, CELL_SIZE))
                    
    def draw_block(self, block, x, y, alpha=255):
        """Bir bloğu çiz"""
        scale = block.scale if hasattr(block, 'scale') else 1.0
        
        for row in range(len(block.shape)):
            for col in range(len(block.shape[0])):
                if block.shape[row][col]:
                    base_x = x + col * (CELL_SIZE + MARGIN)
                    base_y = y + row * (CELL_SIZE + MARGIN)
                    
                    size = int(CELL_SIZE * scale)
                    offset = (CELL_SIZE - size) // 2
                    
                    surf = pygame.Surface((size, size))
                    surf.set_alpha(alpha)
                    surf.fill(block.color)
                    self.screen.blit(surf, (base_x + offset, base_y + offset))
                    
                    if scale >= 0.8:
                        inner_surf = pygame.Surface((size - 4, size - 4))
                        inner_surf.set_alpha(alpha // 2)
                        lighter_color = tuple(min(255, c + 40) for c in block.color)
                        inner_surf.fill(lighter_color)
                        self.screen.blit(inner_surf, (base_x + offset + 2, base_y + offset + 2))
                    
    def draw_blocks(self):
        """Tüm kullanılabilir blokları çiz"""
        for block in self.blocks:
            if block and not block.dragging:
                block.update_scale()
                self.draw_block(block, block.x, block.y)
    
    def draw_preview(self):
        """Sonraki blokları önizle"""
        font = pygame.font.Font(None, 24)
        title = font.render("SONRAKI", True, WHITE)
        self.screen.blit(title, (WINDOW_WIDTH - 200, 60))
        
        panel_x = WINDOW_WIDTH - 220
        panel_y = 100
        panel_width = 200
        panel_height = 480
        pygame.draw.rect(self.screen, (40, 40, 40), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, LIGHT_GRAY, (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Zorluk seviyesine göre kaç blok gösterilecek kararı ver
        blocks_to_show = 2 if self.difficulty == 'ZOR' else 3
        
        for i in range(blocks_to_show):
            if i < len(self.next_blocks):
                block = self.next_blocks[i]
                y_offset = panel_y + 20 + i * 140
                
                num_font = pygame.font.Font(None, 18)
                num_text = num_font.render(f"#{i+1}", True, LIGHT_GRAY)
                self.screen.blit(num_text, (panel_x + 10, y_offset))
                
                small_x = panel_x + 60
                small_y = y_offset + 25
                
                for row in range(len(block.shape)):
                    for col in range(len(block.shape[0])):
                        if block.shape[row][col]:
                            size = 20
                            x = small_x + col * (size + 1)
                            y = small_y + row * (size + 1)
                            pygame.draw.rect(self.screen, block.color, (x, y, size, size))
                            inner_rect = pygame.Rect(x + 2, y + 2, size - 4, size - 4)
                            lighter = tuple(min(255, c + 30) for c in block.color)
                            pygame.draw.rect(self.screen, lighter, inner_rect)
    
    def draw_difficulty_info(self):
        """Zorluk seviyesi bilgisini çiz"""
        font = pygame.font.Font(None, 20)
        
        difficulty_color = self.difficulty_settings['color']
        diff_text = font.render(f"Zorluk: {self.difficulty}", True, difficulty_color)
        self.screen.blit(diff_text, (WINDOW_WIDTH - 200, 10))
        
        target_text = font.render(f"Hedef: {self.target_score}", True, WHITE)
        self.screen.blit(target_text, (WINDOW_WIDTH - 200, 35))
        
        high_score = self.score_manager.get_high_score(self.difficulty)
        high_text = font.render(f"Rekor: {high_score}", True, YELLOW)
        self.screen.blit(high_text, (WINDOW_WIDTH - 200, 600))
    
    def draw_powerups(self):
        """Power-upları çiz"""
        powerup_types = [
            ('bomb', RED, '💣'),
            ('lightning', YELLOW, '⚡'),
            ('rainbow', PURPLE, '🌈')
        ]
        
        start_x = 50
        start_y = WINDOW_HEIGHT - 70
        spacing = 100
        
        font = pygame.font.Font(None, 24)
        
        for i, (ptype, color, icon) in enumerate(powerup_types):
            x = start_x + i * spacing
            y = start_y
            
            # Arka plan
            pygame.draw.rect(self.screen, (40, 40, 40), (x, y, 80, 50))
            pygame.draw.rect(self.screen, color, (x, y, 80, 50), 2)
            
            # Sayi
            count_text = font.render(str(self.powerups[ptype]), True, color)
            count_rect = count_text.get_rect(center=(x + 40, y + 25))
            self.screen.blit(count_text, count_rect)
            
            # İkon
            try:
                icon_font = pygame.font.Font(None, 28)
                icon_text = icon_font.render(icon, True, WHITE)
                icon_rect = icon_text.get_rect(center=(x + 40, y + 35))
                self.screen.blit(icon_text, icon_rect)
            except:
                pass
            
            # Talimat
            hint_font = pygame.font.Font(None, 14)
            hint_text = hint_font.render(f"{i+1}", True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(center=(x + 70, y + 45))
            self.screen.blit(hint_text, hint_rect)
        
        # Active power-upları çiz
        for pup in self.active_powerups:
            pup.draw(self.screen)
    
    def draw_sound_indicator(self):
        """Ses durumunu göster"""
        indicator_font = pygame.font.Font(None, 18)
        
        music_status = "🔊" if self.sound_manager.music_enabled else "🔇"
        sfx_status = "🔊" if self.sound_manager.sfx_enabled else "🔇"
        
        music_text = indicator_font.render(f"Müzik {music_status}", True, LIGHT_GRAY)
        sfx_text = indicator_font.render(f"Efekt {sfx_status}", True, LIGHT_GRAY)
        
        self.screen.blit(music_text, (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 50))
        self.screen.blit(sfx_text, (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 25))
                
    def get_grid_pos(self, mouse_x, mouse_y):
        """Fare pozisyonunu ızgara koordinatına çevir"""
        col = (mouse_x - GRID_X) // (CELL_SIZE + MARGIN)
        row = (mouse_y - GRID_Y) // (CELL_SIZE + MARGIN)
        
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            return row, col
        return None, None
    
    def can_place_block(self, block, grid_row, grid_col):
        """Bloğun yerleştirilebilir olup olmadığını kontrol et"""
        for row in range(len(block.shape)):
            for col in range(len(block.shape[0])):
                if block.shape[row][col]:
                    new_row = grid_row + row
                    new_col = grid_col + col
                    
                    if (new_row >= GRID_SIZE or new_col >= GRID_SIZE or
                        new_row < 0 or new_col < 0 or
                        self.grid[new_row][new_col]):
                        return False
        return True
    
    def use_bomb(self):
        """Dinamit güç-upunu kullan"""
        if self.powerups['bomb'] > 0:
            self.powerups['bomb'] -= 1
            pup = PowerUp('bomb', WINDOW_WIDTH//2 - 30, GRID_Y + GRID_SIZE * CELL_SIZE // 2 - 30)
            self.active_powerups.append(pup)
            
            # Rasgele 3 hücreyi temizle
            cleared = 0
            attempts = 0
            while cleared < 3 and attempts < 20:
                row = random.randint(0, GRID_SIZE - 1)
                col = random.randint(0, GRID_SIZE - 1)
                if self.grid[row][col]:
                    color = self.grid[row][col]
                    anim_cell = AnimatedCell(row, col, color)
                    self.animated_cells.append(anim_cell)
                    self.create_particles(row, col, color)
                    self.grid[row][col] = 0
                    cleared += 1
                attempts += 1
            
            if cleared > 0:
                self.sound_manager.play('clear')
                self.floating_texts.append(FloatingText("BOMB!", WINDOW_WIDTH//2, GRID_Y - 30, RED))
    
    def use_lightning(self):
        """Yıldırım güç-upunu kullan"""
        if self.powerups['lightning'] > 0:
            self.powerups['lightning'] -= 1
            pup = PowerUp('lightning', WINDOW_WIDTH//2 - 30, GRID_Y + GRID_SIZE * CELL_SIZE // 2 - 30)
            self.active_powerups.append(pup)
            
            # Rasgele bir sütunu temizle
            col = random.randint(0, GRID_SIZE - 1)
            cleared = 0
            for row in range(GRID_SIZE):
                if self.grid[row][col]:
                    color = self.grid[row][col]
                    anim_cell = AnimatedCell(row, col, color)
                    self.animated_cells.append(anim_cell)
                    self.create_particles(row, col, color)
                    self.grid[row][col] = 0
                    cleared += 1
            
            if cleared > 0:
                self.sound_manager.play('clear')
                self.floating_texts.append(FloatingText("LIGHTNING!", WINDOW_WIDTH//2, GRID_Y - 30, YELLOW))
    
    def use_rainbow(self):
        """Gökkuşağı güç-upunu kullan"""
        if self.powerups['rainbow'] > 0:
            self.powerups['rainbow'] -= 1
            pup = PowerUp('rainbow', WINDOW_WIDTH//2 - 30, GRID_Y + GRID_SIZE * CELL_SIZE // 2 - 30)
            self.active_powerups.append(pup)
            
            # Rasgele bir rengi temizle
            colors_in_grid = set()
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.grid[row][col]:
                        colors_in_grid.add(self.grid[row][col])
            
            if colors_in_grid:
                target_color = random.choice(list(colors_in_grid))
                cleared = 0
                for row in range(GRID_SIZE):
                    for col in range(GRID_SIZE):
                        if self.grid[row][col] == target_color:
                            anim_cell = AnimatedCell(row, col, target_color)
                            self.animated_cells.append(anim_cell)
                            self.create_particles(row, col, target_color)
                            self.grid[row][col] = 0
                            cleared += 1
                
                if cleared > 0:
                    self.sound_manager.play('clear')
                    self.floating_texts.append(FloatingText("RAINBOW!", WINDOW_WIDTH//2, GRID_Y - 30, PURPLE))
                
    def place_block(self, block, grid_row, grid_col):
        """Bloğu ızgaraya yerleştir"""
        self.sound_manager.play('place')
        
        for row in range(len(block.shape)):
            for col in range(len(block.shape[0])):
                if block.shape[row][col]:
                    self.grid[grid_row + row][grid_col + col] = block.color
                    anim_cell = AnimatedCell(grid_row + row, grid_col + col, block.color)
                    anim_cell.animation_type = 'place'
                    anim_cell.scale = 0.3
                    self.animated_cells.append(anim_cell)
                    
        self.blocks[self.blocks.index(block)] = None
        self.check_lines()
        
        if all(b is None for b in self.blocks):
            self.blocks = self.next_blocks
            self.next_blocks = [Block() for _ in range(3)]
            self.position_blocks()
            self.sound_manager.play('success')
            
    def check_lines(self):
        """Dolu satır ve sütunları kontrol et ve temizle"""
        rows_to_clear = []
        for row in range(GRID_SIZE):
            if all(self.grid[row][col] != 0 for col in range(GRID_SIZE)):
                rows_to_clear.append(row)
                
        cols_to_clear = []
        for col in range(GRID_SIZE):
            if all(self.grid[row][col] != 0 for row in range(GRID_SIZE)):
                cols_to_clear.append(col)
        
        lines_cleared = len(rows_to_clear) + len(cols_to_clear)
        
        if lines_cleared > 0:
            self.sound_manager.play('clear')
            
            self.combo += 1
            self.combo_timer = self.combo_duration
            
            base_points = lines_cleared * 10
            combo_multiplier = min(self.combo, 10)
            total_points = int(base_points * combo_multiplier * self.score_multiplier)
            
            if lines_cleared >= 3:
                total_points += int(50 * self.score_multiplier)
            if lines_cleared >= 4:
                total_points += int(100 * self.score_multiplier)
                
            self.score += total_points
            
            # Power-up kazan
            if lines_cleared >= 3 and lines_cleared < 4:
                self.powerups['bomb'] += 1
                self.floating_texts.append(FloatingText("BOMB Kazandı!", WINDOW_WIDTH//2, GRID_Y - 50, RED))
            elif lines_cleared == 4:
                self.powerups['lightning'] += 1
                self.floating_texts.append(FloatingText("LIGHTNING Kazandı!", WINDOW_WIDTH//2, GRID_Y - 50, YELLOW))
            elif lines_cleared > 4:
                self.powerups['rainbow'] += 1
                self.floating_texts.append(FloatingText("RAINBOW Kazandı!", WINDOW_WIDTH//2, GRID_Y - 50, PURPLE))
            
            center_x = GRID_X + (GRID_SIZE * (CELL_SIZE + MARGIN)) // 2
            center_y = GRID_Y + (GRID_SIZE * (CELL_SIZE + MARGIN)) // 2
            
            score_text = f"+{total_points}"
            if combo_multiplier > 1:
                score_text = f"+{total_points} (x{combo_multiplier})"
                
            color = YELLOW if combo_multiplier <= 2 else ORANGE if combo_multiplier <= 5 else RED
            self.floating_texts.append(FloatingText(score_text, center_x, center_y, color))
            
            if combo_multiplier >= 2:
                combo_text = f"COMBO x{combo_multiplier}!"
                combo_color = GREEN if combo_multiplier <= 3 else CYAN if combo_multiplier <= 6 else PURPLE
                self.floating_texts.append(FloatingText(combo_text, center_x, center_y - 40, combo_color))
            
        for row in rows_to_clear:
            for col in range(GRID_SIZE):
                color = self.grid[row][col]
                anim_cell = AnimatedCell(row, col, color)
                self.animated_cells.append(anim_cell)
                self.create_particles(row, col, color)
                self.grid[row][col] = 0
            
        for col in cols_to_clear:
            for row in range(GRID_SIZE):
                if self.grid[row][col] != 0:
                    color = self.grid[row][col]
                    anim_cell = AnimatedCell(row, col, color)
                    self.animated_cells.append(anim_cell)
                    self.create_particles(row, col, color)
                    self.grid[row][col] = 0
            
    def check_game_over(self):
        """Oyun bitişini kontrol et"""
        for block in self.blocks:
            if block:
                for row in range(GRID_SIZE):
                    for col in range(GRID_SIZE):
                        if self.can_place_block(block, row, col):
                            return False
        return True
    
    def draw_score(self):
        """Skoru ve combo'yu çiz"""
        font = pygame.font.Font(None, 48)
        score_text = font.render(f"Skor: {self.score}", True, WHITE)
        
        pulse = math.sin(pygame.time.get_ticks() * 0.003) * 3
        shadow = font.render(f"Skor: {self.score}", True, (100, 100, 100))
        self.screen.blit(shadow, (502 + pulse, 102))
        self.screen.blit(score_text, (500 + pulse, 100))
        
        # Hedef puanı göster
        small_font = pygame.font.Font(None, 24)
        target_text = small_font.render(f"/ {self.target_score}", True, LIGHT_GRAY)
        self.screen.blit(target_text, (650, 110))
        
        # İlerleme çubuğu
        bar_width = 150
        bar_height = 10
        bar_x = 500
        bar_y = 160
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        progress = min(1.0, self.score / self.target_score)
        fill_color = GREEN if progress < 0.5 else YELLOW if progress < 0.9 else CYAN
        pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, int(bar_width * progress), bar_height))
        
        # Design by bilgisi
        credit_font = pygame.font.Font(None, 14)
        credit_text = credit_font.render("Design by TETech Studios", True, LIGHT_GRAY)
        self.screen.blit(credit_text, (10, 10))
        
        if self.combo > 1:
            combo_font = pygame.font.Font(None, 56)
            combo_text = f"COMBO x{self.combo}"
            
            if self.combo <= 3:
                combo_color = GREEN
            elif self.combo <= 6:
                combo_color = CYAN
            else:
                combo_color = PURPLE
                
            combo_pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 5
            combo_surface = combo_font.render(combo_text, True, combo_color)
            combo_rect = combo_surface.get_rect(center=(WINDOW_WIDTH//2 - 100, 30 + combo_pulse))
            
            combo_shadow = combo_font.render(combo_text, True, (50, 50, 50))
            shadow_rect = combo_shadow.get_rect(center=(WINDOW_WIDTH//2 - 100 + 2, 32 + combo_pulse))
            self.screen.blit(combo_shadow, shadow_rect)
            self.screen.blit(combo_surface, combo_rect)
            
            bar_width = 200
            bar_height = 8
            bar_x = WINDOW_WIDTH//2 - 100 - bar_width//2
            bar_y = 55
            
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            
            fill_width = int(bar_width * (self.combo_timer / self.combo_duration))
            pygame.draw.rect(self.screen, combo_color, (bar_x, bar_y, fill_width, bar_height))
        
    def draw_game_over(self):
        """Oyun bitti ekranını çiz"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        game_over_text = font.render("OYUN BİTTİ", True, RED)
        
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 80 + pulse))
        self.screen.blit(game_over_text, text_rect)
        
        # Final skoru
        font_medium = pygame.font.Font(None, 48)
        final_score = font_medium.render(f"Final Skor: {self.score}", True, YELLOW)
        final_rect = final_score.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 10))
        self.screen.blit(final_score, final_rect)
        
        # Hedef başarıldı mı?
        if self.score >= self.target_score:
            success_text = font_medium.render("🎉 BAŞARILI! 🎉", True, GREEN)
            success_rect = success_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
            self.screen.blit(success_text, success_rect)
        else:
            remaining = self.target_score - self.score
            fail_text = font_medium.render(f"Henüz {remaining} puan kaldı!", True, RED)
            fail_rect = fail_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
            self.screen.blit(fail_text, fail_rect)
        
        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render("R: Tekrar | M: Menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 120))
        self.screen.blit(restart_text, restart_rect)
        
    def reset(self):
        """Oyunu sıfırla"""
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.blocks = [Block() for _ in range(3)]
        self.next_blocks = [Block() for _ in range(3)]
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.selected_block = None
        self.game_over = False
        self.particles = []
        self.animated_cells = []
        self.floating_texts = []
        self.powerups = {'bomb': 0, 'lightning': 0, 'rainbow': 0}
        self.active_powerups = []
        self.position_blocks()
        
    def update_particles(self):
        """Parçacıkları güncelle"""
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
            
    def update_animations(self):
        """Animasyonları güncelle"""
        self.animated_cells = [cell for cell in self.animated_cells if not cell.is_done()]
        for cell in self.animated_cells:
            cell.update()
            
    def update_floating_texts(self):
        """Yüzen metinleri güncelle"""
        self.floating_texts = [text for text in self.floating_texts if text.is_alive()]
        for text in self.floating_texts:
            text.update()
            
    def update_combo(self):
        """Combo sayacını güncelle"""
        if self.combo > 0 and self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0
            
    def run(self):
        """Ana oyun döngüsü"""
        running = True
        
        while running:
            self.screen.fill(GRAY)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset()
                    if event.key == pygame.K_m and self.game_over:
                        self.score_manager.update_score(self.difficulty, self.score)
                        return 'menu'
                    
                    # Power-up tuşları
                    if not self.game_over:
                        if event.key == pygame.K_1:
                            self.use_bomb()
                        elif event.key == pygame.K_2:
                            self.use_lightning()
                        elif event.key == pygame.K_3:
                            self.use_rainbow()
                        
                if not self.game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        for block in self.blocks:
                            if block:
                                block_height = len(block.shape) * (CELL_SIZE + MARGIN)
                                block_width = len(block.shape[0]) * (CELL_SIZE + MARGIN)
                                
                                if (block.x <= mouse_x <= block.x + block_width and
                                    block.y <= mouse_y <= block.y + block_height):
                                    block.dragging = True
                                    self.selected_block = block
                                    break
                                    
                    if event.type == pygame.MOUSEBUTTONUP:
                        if self.selected_block:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            grid_row, grid_col = self.get_grid_pos(mouse_x, mouse_y)
                            
                            if grid_row is not None and self.can_place_block(
                                self.selected_block, grid_row, grid_col):
                                self.place_block(self.selected_block, grid_row, grid_col)
                                
                                if self.check_game_over():
                                    self.game_over = True
                                    self.score_manager.update_score(self.difficulty, self.score)
                                    self.sound_manager.play('gameover')
                            
                            self.selected_block.dragging = False
                            self.selected_block = None
            
            # Güncellemeler
            self.update_particles()
            self.update_animations()
            self.update_floating_texts()
            self.update_combo()
            
            # Çizimler
            self.draw_grid()
            
            for cell in self.animated_cells:
                cell.draw(self.screen)
            
            self.draw_blocks()
            self.draw_score()
            self.draw_preview()
            self.draw_difficulty_info()
            self.draw_powerups()  # Power-upları çiz
            self.draw_sound_indicator()  # Ses göstergesi
            
            for particle in self.particles:
                particle.draw(self.screen)
                
            for text in self.floating_texts:
                text.draw(self.screen)
            
            if self.selected_block:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                self.draw_block(self.selected_block, mouse_x - 15, mouse_y - 15, 100)
                self.draw_block(self.selected_block, mouse_x - 20, mouse_y - 20, 200)
                
                grid_row, grid_col = self.get_grid_pos(mouse_x, mouse_y)
                if grid_row is not None:
                    can_place = self.can_place_block(self.selected_block, grid_row, grid_col)
                    preview_color = GREEN if can_place else RED
                    
                    pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 50 + 100
                    
                    for row in range(len(self.selected_block.shape)):
                        for col in range(len(self.selected_block.shape[0])):
                            if self.selected_block.shape[row][col]:
                                if grid_row + row < GRID_SIZE and grid_col + col < GRID_SIZE:
                                    x = GRID_X + (grid_col + col) * (CELL_SIZE + MARGIN)
                                    y = GRID_Y + (grid_row + row) * (CELL_SIZE + MARGIN)
                                    
                                    surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
                                    surf.set_alpha(int(pulse))
                                    surf.fill(preview_color)
                                    self.screen.blit(surf, (x, y))
            
            if self.game_over:
                self.draw_game_over()
                
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

class Menu:
    """Ana menü"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Block Blast - Ana Menü")
        self.clock = pygame.time.Clock()
        self.score_manager = ScoreManager()
        self.sound_manager = SoundManager()
        self.show_settings = False
        
    def draw_menu(self):
        """Menüyü çiz"""
        self.screen.fill(GRAY)
        
        # Başlık
        title_font = pygame.font.Font(None, 96)
        title = title_font.render("BLOCK BLAST", True, CYAN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        # Zorluk seviyeleri
        button_font = pygame.font.Font(None, 48)
        button_y = 250
        button_spacing = 100
        
        buttons = []
        
        for i, (diff_name, diff_info) in enumerate(DIFFICULTIES.items()):
            y = button_y + i * button_spacing
            
            # Button arka planı
            button_width = 300
            button_height = 80
            button_x = WINDOW_WIDTH//2 - button_width//2
            
            pygame.draw.rect(self.screen, diff_info['color'], (button_x, y, button_width, button_height))
            pygame.draw.rect(self.screen, WHITE, (button_x, y, button_width, button_height), 3)
            
            # Button metni
            button_text = button_font.render(diff_name, True, BLACK)
            text_rect = button_text.get_rect(center=(WINDOW_WIDTH//2, y + 25))
            self.screen.blit(button_text, text_rect)
            
            # İstatistikler
            stat_font = pygame.font.Font(None, 24)
            high_score = self.score_manager.get_high_score(diff_name)
            games = self.score_manager.get_games_played(diff_name)
            
            stat_text = stat_font.render(f"Rekor: {high_score} | Oyunlar: {games}", True, WHITE)
            stat_rect = stat_text.get_rect(center=(WINDOW_WIDTH//2, y + 55))
            self.screen.blit(stat_text, stat_rect)
            
            buttons.append((button_x, y, button_width, button_height, diff_name))
        
        # Ayarlar butonu
        settings_button = pygame.Rect(WINDOW_WIDTH - 120, 20, 100, 50)
        settings_color = ORANGE if self.show_settings else LIGHT_GRAY
        pygame.draw.rect(self.screen, settings_color, settings_button)
        pygame.draw.rect(self.screen, WHITE, settings_button, 2)
        
        settings_font = pygame.font.Font(None, 24)
        settings_text = settings_font.render("⚙ AYARLAR", True, BLACK)
        settings_rect = settings_text.get_rect(center=settings_button.center)
        self.screen.blit(settings_text, settings_rect)
        
        # Footer
        footer_font = pygame.font.Font(None, 20)
        footer = footer_font.render("Zorluk seviyesine tıklayın", True, LIGHT_GRAY)
        footer_rect = footer.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 30))
        self.screen.blit(footer, footer_rect)
        
        pygame.display.flip()
        return buttons, settings_button
    
    def draw_settings(self):
        """Ayarlar menüsünü çiz"""
        self.screen.fill(GRAY)
        
        # Başlık
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("SES AYARLARI", True, ORANGE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        # Master Volume
        master_slider = self.draw_volume_slider("Master Ses", self.sound_manager.master_volume, 150, 'master')
        
        # Music Volume
        music_slider = self.draw_volume_slider("Müzik", self.sound_manager.music_volume, 250, 'music')
        
        # SFX Volume
        sfx_slider = self.draw_volume_slider("Efekt Sesler", self.sound_manager.sfx_volume, 350, 'sfx')
        
        # Toggle Buttons
        music_toggle = self.draw_toggle_button("Müzik", self.sound_manager.music_enabled, 450, 'music_toggle')
        sfx_toggle = self.draw_toggle_button("Efekt Sesler", self.sound_manager.sfx_enabled, 530, 'sfx_toggle')
        
        # Geri butonu
        back_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.screen, CYAN, back_button)
        pygame.draw.rect(self.screen, WHITE, back_button, 2)
        
        back_font = pygame.font.Font(None, 36)
        back_text = back_font.render("GERI", True, BLACK)
        back_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_rect)
        
        pygame.display.flip()
        return back_button, master_slider, music_slider, sfx_slider, music_toggle, sfx_toggle
    
    def draw_volume_slider(self, label, value, y, slider_id):
        """Ses seviyesi kaydırıcı çiz"""
        label_font = pygame.font.Font(None, 28)
        label_text = label_font.render(f"{label}: {int(value * 100)}%", True, WHITE)
        self.screen.blit(label_text, (100, y))
        
        # Kaydırıcı arka planı
        slider_x = 100
        slider_y = y + 40
        slider_width = 300
        slider_height = 20
        
        pygame.draw.rect(self.screen, (50, 50, 50), (slider_x, slider_y, slider_width, slider_height))
        pygame.draw.rect(self.screen, LIGHT_GRAY, (slider_x, slider_y, slider_width, slider_height), 2)
        
        # Doluluk
        fill_width = int(slider_width * value)
        color = CYAN if slider_id == 'master' else YELLOW if slider_id == 'music' else GREEN
        pygame.draw.rect(self.screen, color, (slider_x, slider_y, fill_width, slider_height))
        
        return (slider_x, slider_y, slider_width, slider_height, slider_id)
    
    def draw_toggle_button(self, label, enabled, y, button_id):
        """Aç/kapat butonu çiz"""
        label_font = pygame.font.Font(None, 28)
        label_text = label_font.render(label, True, WHITE)
        self.screen.blit(label_text, (100, y))
        
        button_x = 450
        button_width = 100
        button_height = 40
        button_color = GREEN if enabled else RED
        
        pygame.draw.rect(self.screen, button_color, (button_x, y, button_width, button_height))
        pygame.draw.rect(self.screen, WHITE, (button_x, y, button_width, button_height), 2)
        
        button_font = pygame.font.Font(None, 24)
        button_text = button_font.render("AÇ" if enabled else "KAPA", True, BLACK)
        button_rect = button_text.get_rect(center=(button_x + button_width//2, y + button_height//2))
        self.screen.blit(button_text, button_rect)
        
        return (button_x, y, button_width, button_height, button_id)
    
    def run(self):
        """Menü döngüsü"""
        running = True
        
        while running:
            if not self.show_settings:
                buttons, settings_button = self.draw_menu()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        return None
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        # Ayarlar butonuna tıklandı
                        if settings_button.collidepoint(mouse_x, mouse_y):
                            self.show_settings = True
                        
                        # Zorluk butonlarına tıklandı
                        for button_x, button_y, button_w, button_h, difficulty in buttons:
                            if (button_x <= mouse_x <= button_x + button_w and
                                button_y <= mouse_y <= button_y + button_h):
                                return difficulty
            else:
                back_button, master_slider, music_slider, sfx_slider, music_toggle, sfx_toggle = self.draw_settings()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        return None
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        # Geri butonuna tıklandı
                        if back_button.collidepoint(mouse_x, mouse_y):
                            self.show_settings = False
                        
                        # Kaydırıcılara tıklandı
                        # Master Volume
                        slider_x, slider_y, slider_w, slider_h, sid = master_slider
                        if slider_y <= mouse_y <= slider_y + slider_h and slider_x <= mouse_x <= slider_x + slider_w:
                            new_val = (mouse_x - slider_x) / slider_w
                            self.sound_manager.set_master_volume(new_val)
                        
                        # Music Volume
                        slider_x, slider_y, slider_w, slider_h, sid = music_slider
                        if slider_y <= mouse_y <= slider_y + slider_h and slider_x <= mouse_x <= slider_x + slider_w:
                            new_val = (mouse_x - slider_x) / slider_w
                            self.sound_manager.set_music_volume(new_val)
                        
                        # SFX Volume
                        slider_x, slider_y, slider_w, slider_h, sid = sfx_slider
                        if slider_y <= mouse_y <= slider_y + slider_h and slider_x <= mouse_x <= slider_x + slider_w:
                            new_val = (mouse_x - slider_x) / slider_w
                            self.sound_manager.set_sfx_volume(new_val)
                        
                        # Toggle Music
                        toggle_x, toggle_y, toggle_w, toggle_h, tid = music_toggle
                        if (toggle_x <= mouse_x <= toggle_x + toggle_w and
                            toggle_y <= mouse_y <= toggle_y + toggle_h):
                            self.sound_manager.toggle_music()
                        
                        # Toggle SFX
                        toggle_x, toggle_y, toggle_w, toggle_h, tid = sfx_toggle
                        if (toggle_x <= mouse_x <= toggle_x + toggle_w and
                            toggle_y <= mouse_y <= toggle_y + toggle_h):
                            self.sound_manager.toggle_sfx()
            
            self.clock.tick(60)

def main():
    """Ana oyun döngüsü"""
    menu = Menu()
    
    while True:
        difficulty = menu.run()
        
        if difficulty is None:
            break
        
        game = Game(difficulty)
        result = game.run()
        
        if result == 'menu':
            continue
        else:
            break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()