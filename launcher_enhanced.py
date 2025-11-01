"""
Ultra-Modern Mancala Game Launcher - FIXED VERSION
Featuring glassmorphism, neon effects, and smooth animations
"""
import os
import sys
import subprocess
import pygame
from ui_config_enhanced import (Colors, Dimensions, fonts, draw_gradient_rect,
                                 draw_triple_gradient_rect, draw_neon_glow,
                                 draw_glassmorphic_panel, draw_text_with_glow,
                                 draw_radial_gradient, draw_animated_border)

pygame.init()

WINDOW_SIZE = (1400, 900)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Mancala - Select Game Mode")
clock = pygame.time.Clock()

# Game mode cards
CARDS = [
    {
        "label": "🎮 AI vs Player",
        "subtitle": "Challenge the smart AI",
        "description": "Test your skills against an intelligent opponent",
        "file": "ai_vs_player_enhanced.py",
        "color1": Colors.PLAYER1_PRIMARY,
        "color2": Colors.PLAYER1_SECONDARY,
        "icon": "🎮"
    },
    {
        "label": "👥 Player vs Player",
        "subtitle": "Local multiplayer",
        "description": "Play with a friend on the same device",
        "file": "player_vs_player.py",
        "color1": Colors.NEON_ORANGE,
        "color2": Colors.NEON_YELLOW,
        "icon": "👥"
    },
    {
        "label": "🤖 AI vs AI",
        "subtitle": "Watch AI battle",
        "description": "Observe two AI players compete",
        "file": "ai_vs_ai_enhanced.py",
        "color1": Colors.PLAYER2_PRIMARY,
        "color2": Colors.PLAYER2_SECONDARY,
        "icon": "🤖"
    }
]

# Card layout
CARD_WIDTH = 380
CARD_HEIGHT = 260
CARD_SPACING = 50
start_x = (WINDOW_SIZE[0] - (CARD_WIDTH * 3 + CARD_SPACING * 2)) // 2
start_y = WINDOW_SIZE[1] // 2 - CARD_HEIGHT // 2 + 60

card_rects = []
for i in range(len(CARDS)):
    x = start_x + i * (CARD_WIDTH + CARD_SPACING)
    y = start_y
    card_rects.append(pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT))


def draw_animated_background(phase):
    """Draw animated gradient background"""
    draw_triple_gradient_rect(screen, Colors.BG_GRADIENT_START, Colors.BG_GRADIENT_MID,
                              Colors.BG_GRADIENT_END,
                              pygame.Rect(0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]),
                              vertical=True)
    
    # Animated glow orbs
    for i in range(4):
        x = WINDOW_SIZE[0] * (0.15 + i * 0.25)
        y = WINDOW_SIZE[1] * 0.5 + 120 * pygame.math.Vector2(1, 0).rotate(phase + i * 90).y
        radius = 180 + 60 * pygame.math.Vector2(1, 0).rotate(phase * 1.5 + i * 60).x
        colors = [Colors.NEON_BLUE, Colors.NEON_PURPLE, Colors.NEON_PINK, Colors.NEON_GREEN]
        draw_radial_gradient(screen, (int(x), int(y)),
                           (*colors[i], 25), (*colors[i], 0), int(radius))


def draw_card(rect, card_info, hover, pressed=False, phase=0):
    """Draw a glassmorphic game mode card"""
    color1 = card_info["color1"]
    color2 = card_info["color2"]
    
    # Hover effect - lift card
    offset_y = -10 if hover else 0
    if pressed:
        offset_y = 5
    
    current_rect = rect.move(0, offset_y)
    
    # Outer glow
    if hover:
        draw_neon_glow(screen, current_rect.center, CARD_WIDTH // 2, color1, 0.8, layers=6)
    
    # Card shadow layers
    for i in range(3):
        shadow_offset = (5 - offset_y) + i * 3
        shadow_alpha = 60 - i * 15
        shadow_rect = current_rect.move(shadow_offset, shadow_offset)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, shadow_alpha),
                        (0, 0, shadow_rect.width, shadow_rect.height),
                        border_radius=30)
        screen.blit(shadow_surf, shadow_rect.topleft)
    
    # Card background with glassmorphism
    card_surf = pygame.Surface((current_rect.width, current_rect.height), pygame.SRCALPHA)
    
    # Gradient background
    draw_gradient_rect(card_surf, Colors.BG_DARK_PRIMARY, Colors.BG_DARK_SECONDARY,
                      pygame.Rect(0, 0, current_rect.width, current_rect.height),
                      vertical=True, border_radius=30)
    
    # Glass overlay
    glass_surf = pygame.Surface((current_rect.width, current_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(glass_surf, Colors.GLASS_WHITE,
                    (0, 0, current_rect.width, current_rect.height),
                    border_radius=30)
    card_surf.blit(glass_surf, (0, 0))
    
    screen.blit(card_surf, current_rect.topleft)
    
    # Animated border - FIXED
    if hover:
        draw_animated_border(screen, current_rect, color1, phase, width=4, border_radius=30)
    else:
        # FIX: Extract RGB values only
        border_color = Colors.GLASS_BORDER[:3] if len(Colors.GLASS_BORDER) > 3 else Colors.GLASS_BORDER
        pygame.draw.rect(screen, (*border_color, 150), current_rect,
                        width=3, border_radius=30)
    
    # Inner highlight - FIXED
    inner_rect = current_rect.inflate(-8, -8)
    highlight_color = Colors.GLASS_BORDER[:3] if len(Colors.GLASS_BORDER) > 3 else Colors.GLASS_BORDER
    pygame.draw.rect(screen, (*highlight_color, 80), inner_rect,
                    width=2, border_radius=27)
    
    # Icon with glow
    icon_y = current_rect.y + 50
    icon_size = 60
    
    if hover:
        draw_neon_glow(screen, (current_rect.centerx, icon_y), icon_size // 2, color1, 0.6)
    
    icon_text = fonts.large.render(card_info["icon"], True, color1)
    icon_rect = icon_text.get_rect(center=(current_rect.centerx, icon_y))
    screen.blit(icon_text, icon_rect)
    
    # Title
    title_y = current_rect.y + 120
    if hover:
        draw_text_with_glow(screen, fonts.normal, card_info["label"],
                           (current_rect.centerx, title_y),
                           Colors.TEXT_PRIMARY, glow_color=color1, glow_intensity=2)
    else:
        title_text = fonts.normal.render(card_info["label"], True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(current_rect.centerx, title_y))
        screen.blit(title_text, title_rect)
    
    # Subtitle
    subtitle_y = current_rect.y + 160
    subtitle_color = color1 if hover else Colors.TEXT_SECONDARY
    subtitle_text = fonts.small.render(card_info["subtitle"], True, subtitle_color)
    subtitle_rect = subtitle_text.get_rect(center=(current_rect.centerx, subtitle_y))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Description
    desc_y = current_rect.y + 195
    desc_text = fonts.tiny.render(card_info["description"], True, Colors.TEXT_SECONDARY)
    desc_rect = desc_text.get_rect(center=(current_rect.centerx, desc_y))
    screen.blit(desc_text, desc_rect)
    
    # Hover indicator
    if hover:
        indicator_y = current_rect.y + CARD_HEIGHT - 25
        indicator_text = fonts.tiny.render("▶ Click to play", True, color1)
        indicator_rect = indicator_text.get_rect(center=(current_rect.centerx, indicator_y))
        
        # Pulsing effect
        pulse = 0.8 + 0.2 * pygame.math.Vector2(1, 0).rotate(phase * 5).x
        indicator_text.set_alpha(int(255 * pulse))
        screen.blit(indicator_text, indicator_rect)


def draw_title(phase):
    """Draw animated title"""
    title_y = 150
    
    # Massive glow
    draw_neon_glow(screen, (WINDOW_SIZE[0] // 2, title_y), 250, Colors.NEON_BLUE, 0.5, layers=8)
    
    # Title with glow
    draw_text_with_glow(screen, fonts.mega, "MANCALA",
                       (WINDOW_SIZE[0] // 2, title_y),
                       Colors.TEXT_PRIMARY, glow_color=Colors.NEON_BLUE,
                       glow_intensity=5)
    
    # Animated subtitle
    subtitle_y = title_y + 80
    pulse = 0.7 + 0.3 * pygame.math.Vector2(1, 0).rotate(phase * 2).x
    subtitle_color = tuple(int(c * pulse) for c in Colors.NEON_PURPLE[:3])
    
    draw_text_with_glow(screen, fonts.medium, "Choose Your Game Mode",
                       (WINDOW_SIZE[0] // 2, subtitle_y),
                       subtitle_color, glow_color=Colors.NEON_PURPLE,
                       glow_intensity=2)


def draw_footer():
    """Draw footer with instructions"""
    footer_y = WINDOW_SIZE[1] - 60
    
    footer_panel = pygame.Rect(WINDOW_SIZE[0] // 2 - 200, footer_y - 20, 400, 60)
    draw_glassmorphic_panel(screen, footer_panel, 
                           bg_color=(*Colors.BG_DARK_PRIMARY, 150),
                           border_color=Colors.GLASS_BORDER)
    
    footer_text = fonts.small.render("Press ESC to quit", True, Colors.TEXT_SECONDARY)
    footer_rect = footer_text.get_rect(center=(WINDOW_SIZE[0] // 2, footer_y))
    screen.blit(footer_text, footer_rect)


def show_message(lines, duration=2.0, phase=0):
    """Show a glassmorphic message popup"""
    msg_w, msg_h = 700, 250 + len(lines) * 40
    msg_rect = pygame.Rect(0, 0, msg_w, msg_h)
    msg_rect.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
    
    # Overlay
    overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Glow
    draw_neon_glow(screen, msg_rect.center, msg_w // 2, Colors.NEON_ORANGE, 0.7, layers=6)
    
    # Message box
    msg_surf = pygame.Surface((msg_w, msg_h), pygame.SRCALPHA)
    draw_gradient_rect(msg_surf, Colors.BG_DARK_PRIMARY, Colors.BG_DARK_SECONDARY,
                      pygame.Rect(0, 0, msg_w, msg_h),
                      vertical=True, border_radius=40)
    msg_surf.set_alpha(240)
    screen.blit(msg_surf, msg_rect.topleft)
    
    # Border
    pygame.draw.rect(screen, Colors.NEON_ORANGE, msg_rect, width=4, border_radius=40)
    
    # Content
    y_offset = 60
    for line in lines:
        if "⚠️" in line or "❌" in line:
            color = Colors.NEON_ORANGE
            draw_text_with_glow(screen, fonts.medium, line,
                               (msg_rect.centerx, msg_rect.top + y_offset),
                               color, glow_color=color, glow_intensity=2)
        else:
            text = fonts.normal.render(line, True, Colors.TEXT_PRIMARY)
            text_rect = text.get_rect(center=(msg_rect.centerx, msg_rect.top + y_offset))
            screen.blit(text, text_rect)
        y_offset += 50
    
    pygame.display.flip()
    pygame.time.wait(int(duration * 1000))


def launch_game(game_file):
    """Launch the selected game"""
    script_path = os.path.join(os.path.dirname(__file__), game_file)
    
    if not os.path.exists(script_path):
        show_message([
            "⚠️ File Not Found!",
            f"Cannot find: {game_file}",
            "",
            "Please ensure all game files are present"
        ])
        return
    
    try:
        subprocess.call([sys.executable, script_path])
    except Exception as e:
        show_message([
            "❌ Launch Failed!",
            f"Error: {str(e)}",
            "",
            "Check console for details"
        ])


def main():
    """Main launcher loop"""
    hover_idx = None
    pressed_idx = None
    phase = 0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                hover_idx = None
                for i, rect in enumerate(card_rects):
                    if rect.collidepoint(mx, my):
                        hover_idx = i
                        break
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, rect in enumerate(card_rects):
                    if rect.collidepoint(mx, my):
                        pressed_idx = i
                        break
            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if pressed_idx is not None:
                    mx, my = event.pos
                    if card_rects[pressed_idx].collidepoint(mx, my):
                        launch_game(CARDS[pressed_idx]["file"])
                    pressed_idx = None
        
        # Draw everything
        draw_animated_background(phase)
        draw_title(phase)
        
        for i, (card_info, rect) in enumerate(zip(CARDS, card_rects)):
            is_hover = (hover_idx == i)
            is_pressed = (pressed_idx == i)
            draw_card(rect, card_info, is_hover, is_pressed, phase)
        
        draw_footer()
        
        pygame.display.flip()
        phase += 0.5
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()

'''launcher_enhanced.py FIXED ends here'''