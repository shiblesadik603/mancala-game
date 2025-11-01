"""
Ultra-Modern UI Configuration for Mancala Game
Featuring glassmorphism, neon accents, and fluid animations
"""
import pygame
import math

# ==================== VIBRANT COLOR PALETTE ====================

class Colors:
    # Neon & Vibrant Accents
    NEON_BLUE = (0, 242, 254)
    NEON_PURPLE = (191, 64, 191)
    NEON_PINK = (255, 20, 147)
    NEON_GREEN = (57, 255, 20)
    NEON_ORANGE = (255, 140, 0)
    NEON_YELLOW = (255, 255, 0)
    
    # Modern Dark Theme
    BG_DARK_PRIMARY = (10, 10, 25)
    BG_DARK_SECONDARY = (15, 15, 35)
    BG_GRADIENT_START = (20, 20, 50)
    BG_GRADIENT_MID = (30, 10, 60)
    BG_GRADIENT_END = (15, 30, 70)
    
    # Glassmorphism
    GLASS_WHITE = (255, 255, 255, 80)
    GLASS_LIGHT = (255, 255, 255, 120)
    GLASS_BORDER = (255, 255, 255, 180)
    GLASS_SHADOW = (0, 0, 0, 100)
    
    # Player Colors with Glow
    PLAYER1_PRIMARY = (0, 255, 200)      # Cyan-Green
    PLAYER1_SECONDARY = (0, 200, 255)    # Sky Blue
    PLAYER1_GLOW = (0, 255, 200, 150)
    PLAYER1_DARK = (0, 150, 120)
    
    PLAYER2_PRIMARY = (255, 100, 200)    # Hot Pink
    PLAYER2_SECONDARY = (200, 50, 255)   # Purple
    PLAYER2_GLOW = (255, 100, 200, 150)
    PLAYER2_DARK = (180, 50, 140)
    
    # Board Colors
    BOARD_PRIMARY = (40, 30, 80)
    BOARD_SECONDARY = (60, 40, 100)
    BOARD_BORDER = (100, 200, 255)
    BOARD_GLOW = (100, 200, 255, 100)
    
    # Pit Colors
    PIT_INACTIVE = (30, 30, 60)
    PIT_ACTIVE = (50, 50, 100)
    PIT_HOVER = (80, 80, 140)
    PIT_SELECTED = (255, 200, 0)
    PIT_BORDER_INACTIVE = (60, 60, 100)
    PIT_BORDER_ACTIVE = (255, 200, 0)
    
    # Stone Colors (Vibrant)
    STONE_COLORS = [
        (255, 50, 100),   # Hot Pink
        (50, 150, 255),   # Sky Blue
        (100, 255, 100),  # Lime Green
        (255, 200, 50),   # Gold
        (200, 100, 255),  # Purple
        (255, 150, 50),   # Orange
        (50, 255, 200),   # Cyan
        (255, 100, 150),  # Rose
    ]
    
    # UI Elements
    PANEL_BG = (20, 20, 40, 200)
    PANEL_BORDER = (100, 200, 255, 255)
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (200, 220, 255)
    TEXT_ACCENT = (255, 200, 0)
    
    # Effects
    GLOW_STRONG = (255, 255, 255, 200)
    GLOW_MEDIUM = (255, 255, 255, 120)
    GLOW_SOFT = (255, 255, 255, 60)
    PARTICLE_GLOW = (255, 200, 100, 255)
    
    # Status Colors
    WIN_COLOR = (100, 255, 100)
    LOSE_COLOR = (255, 100, 100)
    TIE_COLOR = (255, 255, 100)


# ==================== ENHANCED DIMENSIONS ====================

class Dimensions:
    # Screen
    SCREEN_WIDTH = 1400
    SCREEN_HEIGHT = 900
    
    # Board - FIXED: Smaller to prevent panel overlap
    BOARD_WIDTH = 900
    BOARD_HEIGHT = 340
    BOARD_BORDER_RADIUS = 40
    BOARD_PADDING = 50
    BOARD_GLOW_RADIUS = 25
    
    # Pits - FIXED: Smaller for better spacing
    PIT_RADIUS = 50
    PIT_BORDER_WIDTH = 3
    PIT_GLOW_RADIUS = 65
    PIT_HOVER_SCALE = 1.12
    PIT_DEPTH = 6
    
    # Mancala Stores - FIXED: Proportional to board
    MANCALA_WIDTH = 100
    MANCALA_HEIGHT = 260
    MANCALA_BORDER_RADIUS = 50
    
    # Stones
    STONE_RADIUS = 10
    STONE_GLOW_RADIUS = 15
    
    # UI Panels - FIXED: Positioned to not overlap board
    PANEL_WIDTH = 320
    PANEL_HEIGHT = 130
    PANEL_BORDER_RADIUS = 25
    MINI_PANEL_HEIGHT = 75
    
    # Animations
    PULSE_SPEED = 0.08
    GLOW_PULSE_INTENSITY = 0.3
    PARTICLE_COUNT = 30


# ==================== PREMIUM FONTS ====================

class Fonts:
    def __init__(self):
        pygame.font.init()
        try:
            self.mega = pygame.font.Font(None, 120)
            self.title = pygame.font.Font(None, 92)
            self.large = pygame.font.Font(None, 64)
            self.medium = pygame.font.Font(None, 48)
            self.normal = pygame.font.Font(None, 36)
            self.small = pygame.font.Font(None, 28)
            self.tiny = pygame.font.Font(None, 20)
        except:
            self.mega = pygame.font.SysFont('Arial', 120, bold=True)
            self.title = pygame.font.SysFont('Arial', 92, bold=True)
            self.large = pygame.font.SysFont('Arial', 64, bold=True)
            self.medium = pygame.font.SysFont('Arial', 48, bold=True)
            self.normal = pygame.font.SysFont('Arial', 36)
            self.small = pygame.font.SysFont('Arial', 28)
            self.tiny = pygame.font.SysFont('Arial', 20)


# ==================== ANIMATION CONFIG ====================

class AnimationConfig:
    # Particle System
    PARTICLE_LIFETIME = 90
    PARTICLE_SPEED_MIN = 3
    PARTICLE_SPEED_MAX = 8
    PARTICLE_GRAVITY = 0.25
    
    # Glow Effects
    GLOW_PULSE_SPEED = 0.06
    GLOW_MIN_ALPHA = 80
    GLOW_MAX_ALPHA = 200
    
    # Stone Movement
    STONE_DROP_DURATION = 35
    STONE_BOUNCE_HEIGHT = 20
    
    # Screen Effects
    SHAKE_INTENSITY = 15
    SHAKE_DURATION = 25
    
    # Transitions
    FADE_DURATION = 30
    
    # Hover Effects
    HOVER_SCALE_SPEED = 0.15
    HOVER_GLOW_INTENSITY = 1.5


# ==================== ADVANCED DRAWING FUNCTIONS ====================

def draw_radial_gradient(surface, center, inner_color, outer_color, radius):
    """Draw a radial gradient circle"""
    gradient_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    
    for i in range(radius, 0, -1):
        ratio = (radius - i) / radius
        color = blend_colors(inner_color, outer_color, ratio)
        pygame.draw.circle(gradient_surf, color, (radius, radius), i)
    
    surface.blit(gradient_surf, (center[0] - radius, center[1] - radius))


def draw_gradient_rect(surface, color1, color2, rect, vertical=True, border_radius=0):
    """Draw a smooth gradient rectangle"""
    gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    if vertical:
        for y in range(rect.height):
            ratio = y / rect.height
            color = blend_colors(color1, color2, ratio)
            pygame.draw.line(gradient_surface, color, (0, y), (rect.width, y))
    else:
        for x in range(rect.width):
            ratio = x / rect.width
            color = blend_colors(color1, color2, ratio)
            pygame.draw.line(gradient_surface, color, (x, 0), (x, rect.height))
    
    if border_radius > 0:
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, rect.width, rect.height), 
                        border_radius=border_radius)
        gradient_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    
    surface.blit(gradient_surface, rect.topleft)


def draw_triple_gradient_rect(surface, color1, color2, color3, rect, vertical=True, border_radius=0):
    """Draw a three-color gradient"""
    gradient_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    if vertical:
        third = rect.height // 3
        for y in range(rect.height):
            if y < third:
                ratio = y / third
                color = blend_colors(color1, color2, ratio)
            elif y < third * 2:
                ratio = (y - third) / third
                color = blend_colors(color2, color3, ratio)
            else:
                ratio = (y - third * 2) / third
                color = blend_colors(color3, color2, ratio)
            pygame.draw.line(gradient_surface, color, (0, y), (rect.width, y))
    else:
        third = rect.width // 3
        for x in range(rect.width):
            if x < third:
                ratio = x / third
                color = blend_colors(color1, color2, ratio)
            elif x < third * 2:
                ratio = (x - third) / third
                color = blend_colors(color2, color3, ratio)
            else:
                ratio = (x - third * 2) / third
                color = blend_colors(color3, color2, ratio)
            pygame.draw.line(gradient_surface, color, (x, 0), (x, rect.height))
    
    if border_radius > 0:
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, rect.width, rect.height), 
                        border_radius=border_radius)
        gradient_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    
    surface.blit(gradient_surface, rect.topleft)


def blend_colors(color1, color2, ratio):
    """Blend two colors smoothly"""
    r = int(color1[0] + (color2[0] - color1[0]) * ratio)
    g = int(color1[1] + (color2[1] - color1[1]) * ratio)
    b = int(color1[2] + (color2[2] - color1[2]) * ratio)
    a = 255
    if len(color1) > 3:
        a = int(color1[3] + (color2[3] - color1[3]) * ratio) if len(color2) > 3 else color1[3]
    return (r, g, b, a) if len(color1) > 3 or len(color2) > 3 else (r, g, b)


def draw_neon_glow(surface, pos, radius, color, intensity=1.0, layers=5):
    """Draw a neon glow effect"""
    glow_surf = pygame.Surface((radius * 6, radius * 6), pygame.SRCALPHA)
    
    for i in range(layers):
        alpha = int((intensity * 255 / (i + 1)) * 0.6)
        glow_radius = int(radius * (1 + i * 0.5))
        glow_color = (*color[:3], alpha)
        pygame.draw.circle(glow_surf, glow_color, (radius * 3, radius * 3), glow_radius)
    
    surface.blit(glow_surf, (pos[0] - radius * 3, pos[1] - radius * 3))


def draw_glassmorphic_panel(surface, rect, bg_color=None, border_color=None, blur_strength=3):
    """Draw a modern glassmorphic panel"""
    if bg_color is None:
        bg_color = Colors.GLASS_WHITE
    if border_color is None:
        border_color = Colors.GLASS_BORDER
    
    # Background with blur effect simulation
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, bg_color, (0, 0, rect.width, rect.height),
                    border_radius=Dimensions.PANEL_BORDER_RADIUS)
    
    # Add noise/texture for glass effect
    for _ in range(100):
        x = pygame.math.Vector2(rect.width * pygame.math.Vector2(1, 0).rotate(360 * _ / 100))
        noise_alpha = 20
        pygame.draw.circle(panel_surf, (255, 255, 255, noise_alpha),
                         (int(x.x) % rect.width, int(_ * rect.height / 100)), 2)
    
    surface.blit(panel_surf, rect.topleft)
    
    # Border with gradient
    pygame.draw.rect(surface, border_color, rect, width=3,
                    border_radius=Dimensions.PANEL_BORDER_RADIUS)
    
    # Inner highlight
    highlight_rect = rect.inflate(-6, -6)
    pygame.draw.rect(surface, (255, 255, 255, 60), highlight_rect, width=2,
                    border_radius=Dimensions.PANEL_BORDER_RADIUS - 3)


def draw_3d_circle(surface, color, center, radius, depth=8):
    """Draw a 3D circle with depth"""
    for i in range(depth, 0, -1):
        layer_radius = radius - i
        if layer_radius <= 0:
            break
        depth_ratio = i / depth
        layer_color = blend_colors(color, (0, 0, 0), depth_ratio * 0.3)
        pygame.draw.circle(surface, layer_color, center, layer_radius)


def draw_animated_border(surface, rect, color, phase, width=3, border_radius=0):
    """Draw an animated glowing border"""
    alpha = int(128 + 127 * math.sin(phase))
    border_color = (*color[:3], alpha)
    
    border_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, border_color, (0, 0, rect.width, rect.height),
                    width=width, border_radius=border_radius)
    surface.blit(border_surf, rect.topleft)


def draw_text_with_glow(surface, font, text, pos, color, glow_color=None, glow_intensity=2):
    """Draw text with neon glow effect"""
    if glow_color is None:
        glow_color = color
    
    # Render text
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=pos)
    
    # Draw glow layers
    for i in range(glow_intensity, 0, -1):
        glow_surf = font.render(text, True, (*glow_color[:3], 100 // i))
        glow_rect = glow_surf.get_rect(center=(pos[0] + i, pos[1] + i))
        surface.blit(glow_surf, glow_rect)
    
    # Draw main text
    surface.blit(text_surf, text_rect)
    return text_rect


def draw_progress_bar(surface, rect, progress, color1, color2, border_radius=15):
    """Draw an animated progress bar"""
    # Background
    bg_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surf, (50, 50, 80, 180), (0, 0, rect.width, rect.height),
                    border_radius=border_radius)
    surface.blit(bg_surf, rect.topleft)
    
    # Fill
    fill_width = int(rect.width * progress)
    if fill_width > 0:
        fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
        fill_surf = pygame.Surface((fill_width, rect.height), pygame.SRCALPHA)
        draw_gradient_rect(fill_surf, color1, color2,
                          pygame.Rect(0, 0, fill_width, rect.height),
                          vertical=False, border_radius=border_radius)
        surface.blit(fill_surf, fill_rect.topleft)
        
        # Shine effect
        shine_height = rect.height // 2
        pygame.draw.rect(surface, (255, 255, 255, 60),
                        pygame.Rect(rect.x, rect.y, fill_width, shine_height),
                        border_radius=border_radius)
    
    # Border
    pygame.draw.rect(surface, (255, 255, 255, 180), rect, width=2, border_radius=border_radius)


# ==================== LAYOUT CALCULATOR ====================

class LayoutCalculator:
    @staticmethod
    def get_board_rect(screen_width, screen_height):
        """Calculate board position"""
        x = (screen_width - Dimensions.BOARD_WIDTH) // 2
        y = (screen_height - Dimensions.BOARD_HEIGHT) // 2
        return pygame.Rect(x, y, Dimensions.BOARD_WIDTH, Dimensions.BOARD_HEIGHT)
    
    @staticmethod
    def get_pit_positions(board_rect):
        """Calculate pit positions with perfect spacing - FIXED NO OVERLAP"""
        positions = {}
        
        available_width = (Dimensions.BOARD_WIDTH - 2 * Dimensions.MANCALA_WIDTH - 
                          2 * Dimensions.BOARD_PADDING)
        pit_spacing = available_width / 6
        
        # Bottom row (0-5) - FIXED: Proper spacing from edge
        bottom_y = board_rect.y + board_rect.height - Dimensions.BOARD_PADDING - Dimensions.PIT_RADIUS
        for i in range(6):
            x = (board_rect.x + Dimensions.MANCALA_WIDTH + Dimensions.BOARD_PADDING + 
                 pit_spacing * i + pit_spacing // 2)
            positions[i] = (int(x), int(bottom_y))
        
        # Top row (7-12) - FIXED: Proper spacing from edge
        top_y = board_rect.y + Dimensions.BOARD_PADDING + Dimensions.PIT_RADIUS
        for i in range(6):
            pit_index = 12 - i
            x = (board_rect.x + Dimensions.MANCALA_WIDTH + Dimensions.BOARD_PADDING + 
                 pit_spacing * i + pit_spacing // 2)
            positions[pit_index] = (int(x), int(top_y))
        
        return positions
    
    @staticmethod
    def get_mancala_positions(board_rect):
        """Calculate mancala store positions - FIXED SPACING"""
        left_x = board_rect.x + Dimensions.BOARD_PADDING - 10
        right_x = board_rect.x + board_rect.width - Dimensions.MANCALA_WIDTH - Dimensions.BOARD_PADDING + 10
        center_y = board_rect.y + (board_rect.height - Dimensions.MANCALA_HEIGHT) // 2
        
        return {
            13: pygame.Rect(left_x, center_y, Dimensions.MANCALA_WIDTH, Dimensions.MANCALA_HEIGHT),
            6: pygame.Rect(right_x, center_y, Dimensions.MANCALA_WIDTH, Dimensions.MANCALA_HEIGHT)
        }


# ==================== EASING FUNCTIONS ====================

def ease_out_cubic(t):
    return 1 - pow(1 - t, 3)

def ease_in_out_cubic(t):
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

def ease_out_elastic(t):
    c4 = (2 * math.pi) / 3
    if t == 0 or t == 1:
        return t
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


# Initialize fonts
fonts = Fonts()

'''ui_config_enhanced.py ends here'''