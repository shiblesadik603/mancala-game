"""
Ultra-Modern Mancala - AI vs Player
Featuring neon UI, glassmorphism, and responsive animations
"""
import pygame
import sys
import time
import random
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from ui_config_enhanced import (Colors, Dimensions, fonts, draw_gradient_rect, 
                                 draw_triple_gradient_rect, draw_neon_glow,
                                 draw_glassmorphic_panel, draw_text_with_glow,
                                 draw_radial_gradient, draw_progress_bar,
                                 draw_animated_border, LayoutCalculator)
from animations_enhanced import AnimationManager

pygame.init()

screen = pygame.display.set_mode((Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT))
pygame.display.set_caption('Mancala - AI vs Player')
clock = pygame.time.Clock()

# Fuzzy Logic Setup with error handling
try:
    stones_diff = ctrl.Antecedent(np.arange(-48, 49, 1), 'stones_diff')
    extra_turns = ctrl.Antecedent(np.arange(0, 2, 1), 'extra_turns')
    capturing_opportunities = ctrl.Antecedent(np.arange(0, 2, 1), 'capturing_opportunities')
    winning_prob = ctrl.Consequent(np.arange(0, 101, 1), 'winning_prob')
    
    stones_diff['negative'] = fuzz.trimf(stones_diff.universe, [-48, -48, 0])
    stones_diff['zero'] = fuzz.trimf(stones_diff.universe, [-10, 0, 10])
    stones_diff['positive'] = fuzz.trimf(stones_diff.universe, [0, 48, 48])
    
    extra_turns['no'] = fuzz.trimf(extra_turns.universe, [0, 0, 1])
    extra_turns['yes'] = fuzz.trimf(extra_turns.universe, [0, 1, 1])
    
    capturing_opportunities['no'] = fuzz.trimf(capturing_opportunities.universe, [0, 0, 1])
    capturing_opportunities['yes'] = fuzz.trimf(capturing_opportunities.universe, [0, 1, 1])
    
    winning_prob['low'] = fuzz.trimf(winning_prob.universe, [0, 0, 50])
    winning_prob['medium'] = fuzz.trimf(winning_prob.universe, [25, 50, 75])
    winning_prob['high'] = fuzz.trimf(winning_prob.universe, [50, 100, 100])
    
    rule1 = ctrl.Rule(stones_diff['negative'] & extra_turns['no'] & capturing_opportunities['no'], winning_prob['low'])
    rule2 = ctrl.Rule(stones_diff['negative'] & extra_turns['yes'] & capturing_opportunities['no'], winning_prob['medium'])
    rule3 = ctrl.Rule(stones_diff['negative'] & capturing_opportunities['yes'], winning_prob['medium'])
    rule4 = ctrl.Rule(stones_diff['zero'], winning_prob['medium'])
    rule5 = ctrl.Rule(stones_diff['positive'] & extra_turns['no'] & capturing_opportunities['no'], winning_prob['medium'])
    rule6 = ctrl.Rule(stones_diff['positive'] & extra_turns['yes'] & capturing_opportunities['no'], winning_prob['high'])
    rule7 = ctrl.Rule(stones_diff['positive'] & capturing_opportunities['yes'], winning_prob['high'])
    
    winning_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
    winning_sim = ctrl.ControlSystemSimulation(winning_ctrl)
    FUZZY_AVAILABLE = True
except Exception as e:
    print(f"Warning: Fuzzy logic not available: {e}")
    FUZZY_AVAILABLE = False
    winning_sim = None


def calculate_winning_probability(mancala):
    if not FUZZY_AVAILABLE:
        # Simple fallback: base on score difference
        score_diff = mancala[6] - mancala[13]
        probability = 50 + (score_diff * 2)
        return max(0, min(100, probability))
    
    stones_difference = mancala[6] - mancala[13]
    extra_turn = 1 if any(mancala[i] == (6 - i) for i in range(6) if mancala[i] > 0) else 0
    capturing_opportunity = 1 if any(mancala[i] == 1 and mancala[12 - i] != 0 for i in range(6)) else 0
    
    try:
        winning_sim.input['stones_diff'] = stones_difference
        winning_sim.input['extra_turns'] = extra_turn
        winning_sim.input['capturing_opportunities'] = capturing_opportunity
        winning_sim.compute()
        return winning_sim.output['winning_prob']
    except Exception as e:
        print(f"Fuzzy logic error: {e}")
        # Fallback to simple calculation
        probability = 50 + (stones_difference * 2)
        return max(0, min(100, probability))


def draw_animated_background(surface, phase):
    """Draw animated gradient background"""
    # Base gradients
    draw_triple_gradient_rect(surface, Colors.BG_GRADIENT_START, Colors.BG_GRADIENT_MID,
                              Colors.BG_GRADIENT_END,
                              pygame.Rect(0, 0, Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT),
                              vertical=True)
    
    # Animated glow circles
    for i in range(3):
        x = Dimensions.SCREEN_WIDTH * (0.2 + i * 0.3)
        y = Dimensions.SCREEN_HEIGHT * 0.5 + 100 * pygame.math.Vector2(1, 0).rotate(phase + i * 120).y
        radius = 150 + 50 * pygame.math.Vector2(1, 0).rotate(phase * 2 + i * 90).x
        colors = [Colors.NEON_BLUE, Colors.NEON_PURPLE, Colors.NEON_PINK]
        draw_radial_gradient(surface, (int(x), int(y)), 
                           (*colors[i], 30), (*colors[i], 0), int(radius))


def draw_board(mancala, animation_manager, highlight_pit=None, probability=0,
               turn_message="", suggested_move=None, hover_pit=None, phase=0, move_count=0):
    """Draw the ultra-modern game board"""
    draw_animated_background(screen, phase)
    
    board_rect = LayoutCalculator.get_board_rect(Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT)
    pit_positions = LayoutCalculator.get_pit_positions(board_rect)
    mancala_positions = LayoutCalculator.get_mancala_positions(board_rect)
    
    shake_offset = animation_manager.get_shake_offset()
    
    # Board with glassmorphism
    board_surf = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
    
    # Outer glow
    glow_rect = board_rect.inflate(Dimensions.BOARD_GLOW_RADIUS * 2, 
                                   Dimensions.BOARD_GLOW_RADIUS * 2)
    draw_neon_glow(screen, glow_rect.center, board_rect.width // 2, Colors.BOARD_GLOW, 0.3)
    
    # Board background
    draw_triple_gradient_rect(board_surf, Colors.BOARD_PRIMARY, Colors.BOARD_SECONDARY,
                              Colors.BOARD_PRIMARY,
                              pygame.Rect(0, 0, board_rect.width, board_rect.height),
                              vertical=False, border_radius=Dimensions.BOARD_BORDER_RADIUS)
    
    board_surf.set_alpha(220)
    screen.blit(board_surf, (board_rect.x + shake_offset[0], board_rect.y + shake_offset[1]))
    
    # Animated border
    draw_animated_border(screen, board_rect.move(shake_offset[0], shake_offset[1]),
                        Colors.BOARD_BORDER, phase, width=4,
                        border_radius=Dimensions.BOARD_BORDER_RADIUS)
    
    # Inner highlight
    inner_rect = board_rect.inflate(-10, -10).move(shake_offset[0], shake_offset[1])
    border_color = Colors.GLASS_BORDER[:3] if len(Colors.GLASS_BORDER) > 3 else Colors.GLASS_BORDER
    pygame.draw.rect(screen, (*border_color, 100), inner_rect, width=2,
                    border_radius=Dimensions.BOARD_BORDER_RADIUS - 5)
    
    # Draw mancala stores with neon effect
    for store_id, store_rect in mancala_positions.items():
        is_player = store_id == 6
        color1 = Colors.PLAYER1_PRIMARY if is_player else Colors.PLAYER2_PRIMARY
        color2 = Colors.PLAYER1_SECONDARY if is_player else Colors.PLAYER2_SECONDARY
        
        # Glow effect
        draw_neon_glow(screen, 
                      (store_rect.centerx + shake_offset[0], store_rect.centery + shake_offset[1]),
                      store_rect.width // 2, color1, 0.4)
        
        # Store background
        store_surf = pygame.Surface((store_rect.width, store_rect.height), pygame.SRCALPHA)
        draw_gradient_rect(store_surf, color1, color2,
                          pygame.Rect(0, 0, store_rect.width, store_rect.height),
                          vertical=True, border_radius=Dimensions.MANCALA_BORDER_RADIUS)
        store_surf.set_alpha(200)
        screen.blit(store_surf, (store_rect.x + shake_offset[0], store_rect.y + shake_offset[1]))
        
        # Border with glow
        border_color = color1 if is_player else color2
        pygame.draw.rect(screen, border_color,
                        store_rect.move(shake_offset[0], shake_offset[1]),
                        width=4, border_radius=Dimensions.MANCALA_BORDER_RADIUS)
        
        # Score with glow effect
        score = str(mancala[store_id])
        text_pos = (store_rect.centerx + shake_offset[0], store_rect.centery + shake_offset[1])
        draw_text_with_glow(screen, fonts.large, score, text_pos, Colors.TEXT_PRIMARY,
                           glow_color=border_color, glow_intensity=3)
    
    # Draw pits with hover effects
    for pit_id, pos in pit_positions.items():
        is_player_pit = 0 <= pit_id <= 5
        is_highlighted = highlight_pit == pit_id
        is_suggested = suggested_move == pit_id
        is_hover = hover_pit == pit_id
        can_play = is_player_pit and mancala[pit_id] > 0
        
        pit_pos = (pos[0] + shake_offset[0], pos[1] + shake_offset[1])
        
        # Add/update hover effect
        hover_effect = animation_manager.add_hover_effect(pit_id, pit_pos, Dimensions.PIT_RADIUS)
        current_radius = hover_effect.get_scaled_radius()
        
        # Determine pit color and glow
        if is_highlighted:
            pit_color = Colors.PIT_SELECTED
            glow_color = Colors.NEON_YELLOW
            glow_intensity = 1.2
        elif is_suggested:
            pit_color = Colors.PIT_ACTIVE
            glow_color = Colors.NEON_ORANGE
            glow_intensity = 0.8
        elif is_hover and can_play:
            pit_color = Colors.PIT_HOVER
            glow_color = Colors.PLAYER1_PRIMARY
            glow_intensity = 0.6
        elif can_play:
            pit_color = Colors.PIT_ACTIVE
            glow_color = Colors.PLAYER1_PRIMARY
            glow_intensity = 0.3
        else:
            pit_color = Colors.PIT_INACTIVE
            glow_color = Colors.PIT_BORDER_INACTIVE
            glow_intensity = 0.1
        
        # Glow effect
        if glow_intensity > 0.2:
            draw_neon_glow(screen, pit_pos, current_radius, glow_color, glow_intensity)
        
        # Pit background with radial gradient
        draw_radial_gradient(screen, pit_pos, pit_color, Colors.PIT_INACTIVE, current_radius)
        
        # Border
        border_color = glow_color if can_play or is_highlighted else Colors.PIT_BORDER_INACTIVE
        pygame.draw.circle(screen, border_color, pit_pos, current_radius, width=3)
        
        # Inner shadow
        shadow_surf = pygame.Surface((current_radius * 3, current_radius * 3), pygame.SRCALPHA)
        for i in range(5):
            alpha = 40 - i * 8
            pygame.draw.circle(shadow_surf, (0, 0, 0, alpha),
                             (current_radius * 1.5, current_radius * 1.5),
                             current_radius - i * 2)
        screen.blit(shadow_surf, (pit_pos[0] - current_radius * 1.5, 
                                  pit_pos[1] - current_radius * 1.5))
        
        # Stone count with glow
        stone_count = mancala[pit_id]
        count_color = Colors.TEXT_PRIMARY if stone_count > 0 else Colors.TEXT_SECONDARY
        draw_text_with_glow(screen, fonts.medium, str(stone_count), pit_pos,
                           count_color, glow_color=glow_color if can_play else None,
                           glow_intensity=2 if can_play else 0)
        
        # Pit number label - FIXED: Inside pit, no overlap
        label_color = Colors.TEXT_SECONDARY if stone_count == 0 else (*Colors.TEXT_SECONDARY, 180)
        label = fonts.tiny.render(str(pit_id + 1), True, label_color)
        # Position label at bottom of pit, inside the circle
        label_y = pit_pos[1] + current_radius - 15
        label_rect = label.get_rect(center=(pit_pos[0], label_y))
        screen.blit(label, label_rect)
    
    # Draw animations
    animation_manager.draw(screen)
    
    # Player Win Chance Panel (bottom-left)
    player_panel_rect = pygame.Rect(20, Dimensions.SCREEN_HEIGHT - 160, 
                                     Dimensions.PANEL_WIDTH, Dimensions.PANEL_HEIGHT)
    draw_glassmorphic_panel(screen, player_panel_rect)
    
    draw_neon_glow(screen, (player_panel_rect.x + 40, player_panel_rect.y + 30), 15, Colors.PLAYER1_PRIMARY, 0.8)
    pygame.draw.circle(screen, Colors.PLAYER1_PRIMARY, (player_panel_rect.x + 40, player_panel_rect.y + 30), 15)
    
    player_title = fonts.small.render("🎮 Your Win Chance", True, Colors.TEXT_SECONDARY)
    screen.blit(player_title, (player_panel_rect.x + 70, player_panel_rect.y + 20))
    
    draw_text_with_glow(screen, fonts.large, f"{probability:.1f}%",
                       (player_panel_rect.x + 70, player_panel_rect.y + 65),
                       Colors.PLAYER1_PRIMARY, glow_color=Colors.PLAYER1_PRIMARY, glow_intensity=2)
    
    bar_rect = pygame.Rect(player_panel_rect.x + 25, player_panel_rect.y + 105,
                          Dimensions.PANEL_WIDTH - 50, 18)
    draw_progress_bar(screen, bar_rect, probability / 100,
                     Colors.PLAYER1_PRIMARY, Colors.PLAYER1_SECONDARY)
    
    # AI Win Chance Panel (top-left)
    ai_panel_rect = pygame.Rect(20, 20, Dimensions.PANEL_WIDTH, Dimensions.PANEL_HEIGHT)
    draw_glassmorphic_panel(screen, ai_panel_rect)
    
    draw_neon_glow(screen, (ai_panel_rect.x + 40, ai_panel_rect.y + 30), 15, Colors.PLAYER2_PRIMARY, 0.8)
    pygame.draw.circle(screen, Colors.PLAYER2_PRIMARY, (ai_panel_rect.x + 40, ai_panel_rect.y + 30), 15)
    
    ai_title = fonts.small.render("🤖 AI Win Chance", True, Colors.TEXT_SECONDARY)
    screen.blit(ai_title, (ai_panel_rect.x + 70, ai_panel_rect.y + 20))
    
    ai_probability = 100 - probability
    draw_text_with_glow(screen, fonts.large, f"{ai_probability:.1f}%",
                       (ai_panel_rect.x + 70, ai_panel_rect.y + 65),
                       Colors.PLAYER2_PRIMARY, glow_color=Colors.PLAYER2_PRIMARY, glow_intensity=2)
    
    bar_rect2 = pygame.Rect(ai_panel_rect.x + 25, ai_panel_rect.y + 105,
                           Dimensions.PANEL_WIDTH - 50, 18)
    draw_progress_bar(screen, bar_rect2, ai_probability / 100,
                     Colors.PLAYER2_PRIMARY, Colors.PLAYER2_SECONDARY)
    
    # Move counter panel (top-right)
    move_panel_rect = pygame.Rect(Dimensions.SCREEN_WIDTH - Dimensions.PANEL_WIDTH - 20, 20,
                                   Dimensions.PANEL_WIDTH, Dimensions.MINI_PANEL_HEIGHT)
    draw_glassmorphic_panel(screen, move_panel_rect,
                           bg_color=(*Colors.NEON_BLUE, 40),
                           border_color=Colors.NEON_BLUE)
    
    move_text = f"Move: {move_count}"
    draw_text_with_glow(screen, fonts.normal, move_text,
                       (move_panel_rect.centerx, move_panel_rect.centery),
                       Colors.TEXT_PRIMARY, glow_color=Colors.NEON_BLUE, glow_intensity=2)
    
    # ESC button panel (below move counter)
    esc_panel_rect = pygame.Rect(Dimensions.SCREEN_WIDTH - Dimensions.PANEL_WIDTH - 20,
                                  move_panel_rect.bottom + 15,
                                  Dimensions.PANEL_WIDTH, Dimensions.MINI_PANEL_HEIGHT)
    draw_glassmorphic_panel(screen, esc_panel_rect,
                           bg_color=(*Colors.NEON_PURPLE, 40),
                           border_color=Colors.GLASS_BORDER)
    
    esc_text = fonts.small.render("Press ESC to quit", True, Colors.TEXT_SECONDARY)
    esc_rect = esc_text.get_rect(center=(esc_panel_rect.centerx, esc_panel_rect.centery))
    screen.blit(esc_text, esc_rect)
    
    # AI Suggestion panel (below player panel if active)
    if suggested_move is not None:
        suggest_rect = pygame.Rect(20, player_panel_rect.bottom + 15, 
                                    Dimensions.PANEL_WIDTH, Dimensions.MINI_PANEL_HEIGHT)
        draw_glassmorphic_panel(screen, suggest_rect, 
                               bg_color=(*Colors.NEON_ORANGE, 60),
                               border_color=Colors.NEON_ORANGE)
        
        # Lightning icon
        icon_x = suggest_rect.x + 30
        icon_y = suggest_rect.centery
        draw_neon_glow(screen, (icon_x, icon_y), 12, Colors.NEON_YELLOW, 1.0)
        
        # Text
        suggest_title = fonts.small.render("💡 AI Suggestion", True, Colors.TEXT_PRIMARY)
        screen.blit(suggest_title, (suggest_rect.x + 60, suggest_rect.y + 20))
        
        suggest_text = f"Play Pit {suggested_move + 1}"
        draw_text_with_glow(screen, fonts.normal, suggest_text,
                           (suggest_rect.x + 60, suggest_rect.y + 50),
                           Colors.NEON_YELLOW, glow_color=Colors.NEON_ORANGE,
                           glow_intensity=2)
    
    # Turn indicator
    animation_manager.draw_turn_indicator(screen, fonts.large)
    
    pygame.display.flip()


def game_over_popup(message, player_score, ai_score):
    """Ultra-modern game over popup"""
    popup_width, popup_height = 700, 500
    popup_x = (Dimensions.SCREEN_WIDTH - popup_width) // 2
    popup_y = (Dimensions.SCREEN_HEIGHT - popup_height) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    
    # Dark overlay
    overlay = pygame.Surface((Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))
    
    # Determine colors
    if "WIN" in message:
        color1, color2 = Colors.PLAYER1_PRIMARY, Colors.PLAYER1_SECONDARY
    elif "LOSE" in message:
        color1, color2 = Colors.PLAYER2_PRIMARY, Colors.PLAYER2_SECONDARY
    else:
        color1, color2 = Colors.NEON_YELLOW, Colors.NEON_ORANGE
    
    # Outer glow
    draw_neon_glow(screen, popup_rect.center, popup_width // 2, color1, 0.8, layers=6)
    
    # Popup background
    popup_surf = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
    draw_gradient_rect(popup_surf, Colors.BG_DARK_PRIMARY, Colors.BG_DARK_SECONDARY,
                      pygame.Rect(0, 0, popup_width, popup_height),
                      vertical=True, border_radius=50)
    popup_surf.set_alpha(240)
    screen.blit(popup_surf, popup_rect.topleft)
    
    # Animated border
    for i in range(3):
        border_alpha = 200 - i * 60
        pygame.draw.rect(screen, (*color1, border_alpha), popup_rect.inflate(i * 4, i * 4),
                        width=3, border_radius=50)
    
    # Title with mega glow
    draw_text_with_glow(screen, fonts.mega, "GAME OVER",
                       (popup_x + popup_width // 2, popup_y + 100),
                       Colors.TEXT_PRIMARY, glow_color=color1, glow_intensity=4)
    
    # Result
    draw_text_with_glow(screen, fonts.large, message,
                       (popup_x + popup_width // 2, popup_y + 220),
                       color1, glow_color=color1, glow_intensity=3)
    
    # Scores with icons
    score_y = popup_y + 310
    
    # Player score
    player_text = f"You: {player_score}"
    draw_text_with_glow(screen, fonts.medium, player_text,
                       (popup_x + popup_width // 2 - 100, score_y),
                       Colors.PLAYER1_PRIMARY, glow_color=Colors.PLAYER1_PRIMARY,
                       glow_intensity=2)
    
    # VS
    vs_text = fonts.normal.render("VS", True, Colors.TEXT_SECONDARY)
    vs_rect = vs_text.get_rect(center=(popup_x + popup_width // 2, score_y))
    screen.blit(vs_text, vs_rect)
    
    # AI score
    ai_text = f"AI: {ai_score}"
    draw_text_with_glow(screen, fonts.medium, ai_text,
                       (popup_x + popup_width // 2 + 100, score_y),
                       Colors.PLAYER2_PRIMARY, glow_color=Colors.PLAYER2_PRIMARY,
                       glow_intensity=2)
    
    # Instructions
    instr_y = popup_y + 410
    restart_text = fonts.small.render("Press SPACE to play again", True, Colors.TEXT_SECONDARY)
    restart_rect = restart_text.get_rect(center=(popup_x + popup_width // 2, instr_y))
    screen.blit(restart_text, restart_rect)
    
    quit_text = fonts.small.render("Press ESC to quit", True, Colors.TEXT_SECONDARY)
    quit_rect = quit_text.get_rect(center=(popup_x + popup_width // 2, instr_y + 40))
    screen.blit(quit_text, quit_rect)
    
    pygame.display.flip()


class Mancala_Board:
    def __init__(self, mancala):
        if mancala is not None:
            self.mancala = mancala[:]
        else:
            self.mancala = [4] * 6 + [0] + [4] * 6 + [0]

    def player_move(self, i):
        j = i
        repeat_turn = False
        add = self.mancala[j]
        self.mancala[j] = 0
        if i > 6:
            stones = add
            while stones > 0:
                i += 1             
                i = i % 14
                if i == 6:
                    continue
                else:
                    self.mancala[i % 14] += 1
                stones -= 1
            if i > 6 and self.mancala[i] == 1 and i != 13 and self.mancala[-i + 12] != 0:
                self.mancala[13] += 1 + self.mancala[-i + 12]
                self.mancala[i] = 0
                self.mancala[-i + 12] = 0
            if i == 13:
                repeat_turn = True
        else:
            stones = add
            while stones > 0:
                i += 1
                i = i % 14
                if i == 13:
                    continue
                else:
                    self.mancala[i % 14] += 1
                stones -= 1
            if i < 6 and self.mancala[i] == 1 and i != 6 and self.mancala[-i + 12] != 0:
                self.mancala[6] += 1 + self.mancala[-i + 12]
                self.mancala[i] = 0
                self.mancala[-i + 12] = 0
            if i == 6:
                repeat_turn = True
        return repeat_turn

    def animated_player_move(self, pit_index, animation_manager, player_prob, ai_prob, move_count, phase, draw_callback):
        """
        Execute move with step-by-step animation showing each marble being distributed.
        """
        j = pit_index
        repeat_turn = False
        stones_to_distribute = self.mancala[j]
        self.mancala[j] = 0
        
        current_pos = j
        
        if pit_index > 6:  # AI (North) player
            while stones_to_distribute > 0:
                current_pos += 1
                current_pos = current_pos % 14
                if current_pos == 6:  # Skip opponent's store
                    continue
                else:
                    self.mancala[current_pos] += 1
                    stones_to_distribute -= 1
                    
                    # Highlight the pit that just received a marble
                    draw_callback(self.mancala, animation_manager, highlight_pit=current_pos,
                                player_prob=player_prob, ai_prob=ai_prob,
                                move_count=move_count, phase=phase)
                    time.sleep(0.15)  # Pause to show each marble placement
            
            # Capture logic
            if current_pos > 6 and self.mancala[current_pos] == 1 and current_pos != 13 and self.mancala[-current_pos + 12] != 0:
                captured = self.mancala[-current_pos + 12]
                self.mancala[13] += 1 + captured
                self.mancala[current_pos] = 0
                self.mancala[-current_pos + 12] = 0
                
                # Show capture animation
                draw_callback(self.mancala, animation_manager, highlight_pit=13,
                            player_prob=player_prob, ai_prob=ai_prob,
                            move_count=move_count, phase=phase)
                time.sleep(0.3)
            
            if current_pos == 13:
                repeat_turn = True
                
        else:  # Player (South)
            while stones_to_distribute > 0:
                current_pos += 1
                current_pos = current_pos % 14
                if current_pos == 13:  # Skip opponent's store
                    continue
                else:
                    self.mancala[current_pos] += 1
                    stones_to_distribute -= 1
                    
                    # Highlight the pit that just received a marble
                    draw_callback(self.mancala, animation_manager, highlight_pit=current_pos,
                                player_prob=player_prob, ai_prob=ai_prob,
                                move_count=move_count, phase=phase)
                    time.sleep(0.15)  # Pause to show each marble placement
            
            # Capture logic
            if current_pos < 6 and self.mancala[current_pos] == 1 and current_pos != 6 and self.mancala[-current_pos + 12] != 0:
                captured = self.mancala[-current_pos + 12]
                self.mancala[6] += 1 + captured
                self.mancala[current_pos] = 0
                self.mancala[-current_pos + 12] = 0
                
                # Show capture animation
                draw_callback(self.mancala, animation_manager, highlight_pit=6,
                            player_prob=player_prob, ai_prob=ai_prob,
                            move_count=move_count, phase=phase)
                time.sleep(0.3)
            
            if current_pos == 6:
                repeat_turn = True
        
        return repeat_turn

    def isEnd(self):
        if sum(self.mancala[0:6]) == 0:
            self.mancala[13] += sum(self.mancala[7:13])
            for i in range(14):
                if i != 13 and i != 6:
                    self.mancala[i] = 0
            return True
        elif sum(self.mancala[7:13]) == 0:
            self.mancala[6] += sum(self.mancala[0:6])
            for i in range(14):
                if i != 13 and i != 6:
                    self.mancala[i] = 0
            return True
        return False

    def husVal(self):
        if self.isEnd():
            if self.mancala[13] > self.mancala[6]:
                return 100
            elif self.mancala[13] == self.mancala[6]:
                return 0
            else:
                return -100
        else:
            return self.mancala[13] - self.mancala[6]


def alphabeta(mancala, depth, alpha, beta, MinorMax):
    if depth == 0 or mancala.isEnd():
        return mancala.husVal(), -1
    if MinorMax:
        v = -1000000
        player_move = -1
        for i in range(7, 13, 1):
            if mancala.mancala[i] == 0: continue
            a = Mancala_Board(mancala.mancala[:])
            minormax = a.player_move(i)
            newv, _ = alphabeta(a, depth - 1, alpha, beta, minormax)
            if v < newv:
                player_move = i
                v = newv
            alpha = max(alpha, v)
            if alpha >= beta:
                break
        return v, player_move
    else:
        v = 1000000
        player_move = -1
        for i in range(0, 6, 1):
            if mancala.mancala[i] == 0: continue
            a = Mancala_Board(mancala.mancala[:])
            minormax = a.player_move(i)
            newv, _ = alphabeta(a, depth - 1, alpha, beta, not minormax)
            if v > newv:
                player_move = i
                v = newv
            beta = min(beta, v)
            if alpha >= beta:
                break
        return v, player_move


def genetic_algorithm(mancala_board, population_size=50, generations=20, mutation_rate=0.1):
    def initialize_population(size, num_pits):
        return [random.sample(range(6), num_pits) for _ in range(size)]
    
    def fitness(individual, mancala_board):
        board_copy = Mancala_Board(mancala_board.mancala[:])
        total_stones = 0
        for move in individual:
            if board_copy.mancala[move] > 0:
                board_copy.player_move(move)
                total_stones += board_copy.mancala[6]
        return total_stones
    
    def crossover(parent1, parent2):
        crossover_point = random.randint(1, len(parent1) - 1)
        return parent1[:crossover_point] + parent2[crossover_point:]
    
    def mutate(individual, mutation_rate):
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                individual[i] = random.randint(0, 5)
        return individual
    
    population = initialize_population(population_size, 3)
    
    for _ in range(generations):
        population = sorted(population, key=lambda x: fitness(x, mancala_board), reverse=True)
        new_population = population[:population_size // 2]
        
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(population[:population_size // 2], 2)
            child = crossover(parent1, parent2)
            child = mutate(child, mutation_rate)
            new_population.append(child)
        
        population = new_population
    
    best_sequence = max(population, key=lambda x: fitness(x, mancala_board))
    return best_sequence[0]


def player_aibot():
    mancala_board = Mancala_Board(None)
    animation_manager = AnimationManager((Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT))
    
    running = True
    player_turn = True
    selected_pit = -1
    suggested_move = None
    hover_pit = None
    phase = 0
    move_count = 0  # Track move counter
    
    animation_manager.start_transition(fade_in=True)
    animation_manager.show_turn_indicator("Your Turn", Colors.PLAYER1_PRIMARY)
    
    probability = calculate_winning_probability(mancala_board.mancala)
    draw_board(mancala_board.mancala, animation_manager,
              probability=probability, phase=phase, move_count=move_count)
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Update hover state
        old_hover = hover_pit
        hover_pit = None
        
        if player_turn:
            board_rect = LayoutCalculator.get_board_rect(Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT)
            pit_positions = LayoutCalculator.get_pit_positions(board_rect)
            
            for pit_id, pos in pit_positions.items():
                if 0 <= pit_id <= 5 and mancala_board.mancala[pit_id] > 0:
                    distance = ((mouse_pos[0] - pos[0]) ** 2 + (mouse_pos[1] - pos[1]) ** 2) ** 0.5
                    if distance <= Dimensions.PIT_RADIUS:
                        hover_pit = pit_id
                        break
        
        # Update hover effects
        if old_hover != hover_pit:
            if old_hover is not None:
                animation_manager.set_pit_hover(old_hover, False)
            if hover_pit is not None:
                animation_manager.set_pit_hover(hover_pit, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    sys.exit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                if hover_pit is not None:
                    selected_pit = hover_pit
                    board_rect = LayoutCalculator.get_board_rect(Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT)
                    pit_positions = LayoutCalculator.get_pit_positions(board_rect)
                    animation_manager.emit_fountain(*pit_positions[selected_pit], count=40)
        
        if player_turn and suggested_move is None:
            suggested_move = genetic_algorithm(mancala_board)
        
        if selected_pit != -1 and player_turn:
            move_count += 1  # Increment move counter
            
            # Show selected pit for 1 second
            pre_move_start = time.time()
            while time.time() - pre_move_start < 1.0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                animation_manager.update()
                phase += 0.5
                probability = calculate_winning_probability(mancala_board.mancala)
                draw_board(mancala_board.mancala, animation_manager, highlight_pit=selected_pit,
                          probability=probability, suggested_move=suggested_move,
                          phase=phase, move_count=move_count)
                clock.tick(60)
            
            # Animated move showing marble distribution
            def draw_callback(mancala, anim_mgr, highlight_pit, player_prob, ai_prob, move_count, phase):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                anim_mgr.update()
                draw_board(mancala, anim_mgr, highlight_pit=highlight_pit,
                         probability=player_prob, suggested_move=None,
                         phase=phase, move_count=move_count)
            
            repeat_turn = mancala_board.animated_player_move(
                selected_pit, animation_manager, probability, 0, 0, phase, draw_callback
            )
            
            probability = calculate_winning_probability(mancala_board.mancala)
            
            if repeat_turn:
                animation_manager.show_turn_indicator("Extra Turn!", Colors.NEON_GREEN)
            else:
                animation_manager.show_turn_indicator("AI's Turn", Colors.PLAYER2_PRIMARY)
            
            draw_board(mancala_board.mancala, animation_manager, highlight_pit=selected_pit,
                      probability=probability, suggested_move=None if repeat_turn else suggested_move,
                      phase=phase, move_count=move_count)
            
            # Show result - 2 seconds when switching to AI, 1 second for extra turn
            result_display_time = 1.0 if repeat_turn else 2.0
            result_start = time.time()
            while time.time() - result_start < result_display_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                animation_manager.update()
                phase += 0.5
                draw_board(mancala_board.mancala, animation_manager, highlight_pit=selected_pit,
                          probability=probability, suggested_move=None if repeat_turn else suggested_move,
                          phase=phase, move_count=move_count)
                clock.tick(60)
            
            player_turn = repeat_turn
            selected_pit = -1
            if not repeat_turn:
                suggested_move = None
                hover_pit = None
        
        if not player_turn and not mancala_board.isEnd():
            # Show "AI Thinking..." for 1 second
            animation_manager.show_turn_indicator("AI Thinking...", Colors.PLAYER2_PRIMARY)
            think_start = time.time()
            while time.time() - think_start < 1.0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                animation_manager.update()
                phase += 0.5
                probability = calculate_winning_probability(mancala_board.mancala)
                draw_board(mancala_board.mancala, animation_manager,
                         probability=probability, phase=phase, move_count=move_count)
                clock.tick(60)
            
            _, ai_move = alphabeta(mancala_board, 5, -100000, 100000, True)
            if ai_move != -1:
                move_count += 1  # Increment move counter for AI
                
                # Show AI's selected pit for 1 second
                pre_move_start = time.time()
                while time.time() - pre_move_start < 1.0:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    animation_manager.update()
                    phase += 0.5
                    probability = calculate_winning_probability(mancala_board.mancala)
                    draw_board(mancala_board.mancala, animation_manager, highlight_pit=ai_move,
                              probability=probability, phase=phase, move_count=move_count)
                    clock.tick(60)
                
                board_rect = LayoutCalculator.get_board_rect(Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT)
                pit_positions = LayoutCalculator.get_pit_positions(board_rect)
                animation_manager.emit_fountain(*pit_positions[ai_move], count=40)
                
                # Animated move showing marble distribution
                def draw_callback(mancala, anim_mgr, highlight_pit, player_prob, ai_prob, move_count, phase):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    anim_mgr.update()
                    draw_board(mancala, anim_mgr, highlight_pit=highlight_pit,
                             probability=player_prob, phase=phase, move_count=move_count)
                
                repeat_turn = mancala_board.animated_player_move(
                    ai_move, animation_manager, probability, 0, 0, phase, draw_callback
                )
                
                probability = calculate_winning_probability(mancala_board.mancala)
                
                if repeat_turn:
                    animation_manager.show_turn_indicator("AI Extra Turn!", Colors.NEON_PINK)
                else:
                    animation_manager.show_turn_indicator("Your Turn", Colors.PLAYER1_PRIMARY)
                
                draw_board(mancala_board.mancala, animation_manager, highlight_pit=ai_move,
                          probability=probability, phase=phase, move_count=move_count)
                
                # Show result - 2 seconds when switching to player, 1 second for extra turn
                result_display_time = 1.0 if repeat_turn else 2.0
                result_start = time.time()
                while time.time() - result_start < result_display_time:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    animation_manager.update()
                    phase += 0.5
                    draw_board(mancala_board.mancala, animation_manager, highlight_pit=ai_move,
                              probability=probability, phase=phase, move_count=move_count)
                    clock.tick(60)
                
                player_turn = not repeat_turn
                if player_turn:
                    suggested_move = None
        
        animation_manager.update()
        phase += 0.5
        
        if mancala_board.isEnd():
            player_score = mancala_board.mancala[6]
            ai_score = mancala_board.mancala[13]
            
            animation_manager.trigger_shake(intensity=18)
            animation_manager.emit_particles(Dimensions.SCREEN_WIDTH // 2,
                                           Dimensions.SCREEN_HEIGHT // 2, count=100, explosion=True)
            
            if ai_score > player_score:
                message = "AI WINS!"
            elif player_score > ai_score:
                message = "YOU WIN!"
            else:
                message = "TIE GAME!"
            
            for _ in range(40):
                animation_manager.update()
                phase += 0.5
                draw_board(mancala_board.mancala, animation_manager,
                          probability=probability, phase=phase, move_count=move_count)
                time.sleep(0.03)
            
            game_over_popup(message, player_score, ai_score)
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            waiting = False
                            # Restart the game by calling the function recursively
                            player_aibot()
                            return  # Exit current game instance
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
        
        if not mancala_board.isEnd():
            draw_board(mancala_board.mancala, animation_manager,
                      probability=probability, hover_pit=hover_pit,
                      suggested_move=suggested_move if player_turn else None,
                      phase=phase, move_count=move_count)
        
        clock.tick(60)


def splash_screen():
    """Ultra-modern splash screen"""
    phase = 0
    waiting = True
    
    while waiting:
        draw_animated_background(screen, phase)
        
        # Title with massive glow
        title_pos = (Dimensions.SCREEN_WIDTH // 2, Dimensions.SCREEN_HEIGHT // 2 - 120)
        draw_neon_glow(screen, title_pos, 200, Colors.NEON_BLUE, 0.6, layers=8)
        draw_text_with_glow(screen, fonts.mega, "MANCALA", title_pos,
                           Colors.TEXT_PRIMARY, glow_color=Colors.NEON_BLUE,
                           glow_intensity=5)
        
        # Subtitle
        subtitle_pos = (Dimensions.SCREEN_WIDTH // 2, Dimensions.SCREEN_HEIGHT // 2 + 20)
        draw_text_with_glow(screen, fonts.large, "AI vs Player",
                           subtitle_pos, Colors.NEON_PURPLE,
                           glow_color=Colors.NEON_PURPLE, glow_intensity=3)
        
        # Animated prompt
        pulse = 0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(phase * 3).x
        prompt_alpha = int(150 + 105 * pulse)
        prompt = fonts.normal.render("Press any key to start", True, (*Colors.TEXT_PRIMARY, prompt_alpha))
        prompt_rect = prompt.get_rect(center=(Dimensions.SCREEN_WIDTH // 2,
                                              Dimensions.SCREEN_HEIGHT // 2 + 160))
        screen.blit(prompt, prompt_rect)
        
        pygame.display.flip()
        phase += 0.5
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        
        clock.tick(60)


# Start game directly without splash screen loop
if __name__ == "__main__":
    try:
        player_aibot()
    except Exception as e:
        print(f"Error running AI vs Player: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error message to user
        try:
            error_screen = pygame.display.set_mode((800, 600))
            error_screen.fill((20, 20, 30))
            
            error_font = pygame.font.Font(None, 36)
            error_text = error_font.render("Game Error - Check Console", True, (255, 100, 100))
            error_rect = error_text.get_rect(center=(400, 250))
            error_screen.blit(error_text, error_rect)
            
            detail_font = pygame.font.Font(None, 24)
            detail_text = detail_font.render(f"{str(e)[:60]}", True, (200, 200, 200))
            detail_rect = detail_text.get_rect(center=(400, 300))
            error_screen.blit(detail_text, detail_rect)
            
            instruction_text = detail_font.render("Press any key to exit", True, (150, 150, 150))
            instruction_rect = instruction_text.get_rect(center=(400, 400))
            error_screen.blit(instruction_text, instruction_rect)
            
            pygame.display.flip()
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                        waiting = False
            
            pygame.quit()
        except:
            pass
        
        sys.exit(1)

'''ai_vs_player_enhanced.py ends here'''