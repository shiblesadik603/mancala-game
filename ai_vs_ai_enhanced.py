"""
Ultra-Modern Mancala - AI vs AI
Watch two AIs battle with stunning visual effects
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
                                 draw_radial_gradient, draw_animated_border,
                                 LayoutCalculator)
from animations_enhanced import AnimationManager

pygame.init()

screen = pygame.display.set_mode((Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT))
pygame.display.set_caption('Mancala - AI vs AI')
clock = pygame.time.Clock()

# Fuzzy Logic Setup (same as before)
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


def calculate_winning_probability(mancala, player):
    if player == 1:
        stones_difference = mancala[6] - mancala[13]
    else:
        stones_difference = mancala[13] - mancala[6]
    
    extra_turn = 0
    capturing_opportunity = 0
    
    if player == 1:
        for i in range(6):
            if mancala[i] > 0 and (i + mancala[i]) == 6:
                extra_turn = 1
                break
        for i in range(6):
            if mancala[i] == 0 and mancala[12 - i] > 0:
                capturing_opportunity = 1
                break
    else:
        for i in range(7, 13):
            if mancala[i] > 0 and (i + mancala[i]) == 13:
                extra_turn = 1
                break
        for i in range(7, 13):
            if mancala[i] == 0 and mancala[12 - i] > 0:
                capturing_opportunity = 1
                break
    
    winning_sim.input['stones_diff'] = stones_difference
    winning_sim.input['extra_turns'] = extra_turn
    winning_sim.input['capturing_opportunities'] = capturing_opportunity
    winning_sim.compute()
    
    return winning_sim.output['winning_prob']


def draw_animated_background(surface, phase):
    """Draw animated gradient background"""
    draw_triple_gradient_rect(surface, Colors.BG_GRADIENT_START, Colors.BG_GRADIENT_MID,
                              Colors.BG_GRADIENT_END,
                              pygame.Rect(0, 0, Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT),
                              vertical=True)
    
    for i in range(3):
        x = Dimensions.SCREEN_WIDTH * (0.2 + i * 0.3)
        y = Dimensions.SCREEN_HEIGHT * 0.5 + 100 * pygame.math.Vector2(1, 0).rotate(phase + i * 120).y
        radius = 150 + 50 * pygame.math.Vector2(1, 0).rotate(phase * 2 + i * 90).x
        colors = [Colors.NEON_BLUE, Colors.NEON_PURPLE, Colors.NEON_PINK]
        draw_radial_gradient(surface, (int(x), int(y)),
                           (*colors[i], 30), (*colors[i], 0), int(radius))


def draw_board(mancala, animation_manager, highlight_pit=None, ai1_prob=0,
               ai2_prob=0, turn_message="", move_count=0, phase=0):
    """Draw the ultra-modern game board"""
    draw_animated_background(screen, phase)
    
    board_rect = LayoutCalculator.get_board_rect(Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT)
    pit_positions = LayoutCalculator.get_pit_positions(board_rect)
    mancala_positions = LayoutCalculator.get_mancala_positions(board_rect)
    
    shake_offset = animation_manager.get_shake_offset()
    
    # Board with glow
    glow_rect = board_rect.inflate(Dimensions.BOARD_GLOW_RADIUS * 2,
                                   Dimensions.BOARD_GLOW_RADIUS * 2)
    draw_neon_glow(screen, glow_rect.center, board_rect.width // 2, Colors.BOARD_GLOW, 0.3)
    
    # Board background
    board_surf = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
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
    
    # Draw mancala stores
    for store_id, store_rect in mancala_positions.items():
        is_ai1 = store_id == 6
        color1 = Colors.PLAYER1_PRIMARY if is_ai1 else Colors.PLAYER2_PRIMARY
        color2 = Colors.PLAYER1_SECONDARY if is_ai1 else Colors.PLAYER2_SECONDARY
        
        draw_neon_glow(screen,
                      (store_rect.centerx + shake_offset[0], store_rect.centery + shake_offset[1]),
                      store_rect.width // 2, color1, 0.4)
        
        store_surf = pygame.Surface((store_rect.width, store_rect.height), pygame.SRCALPHA)
        draw_gradient_rect(store_surf, color1, color2,
                          pygame.Rect(0, 0, store_rect.width, store_rect.height),
                          vertical=True, border_radius=Dimensions.MANCALA_BORDER_RADIUS)
        store_surf.set_alpha(200)
        screen.blit(store_surf, (store_rect.x + shake_offset[0], store_rect.y + shake_offset[1]))
        
        pygame.draw.rect(screen, color1,
                        store_rect.move(shake_offset[0], shake_offset[1]),
                        width=4, border_radius=Dimensions.MANCALA_BORDER_RADIUS)
        
        score = str(mancala[store_id])
        text_pos = (store_rect.centerx + shake_offset[0], store_rect.centery + shake_offset[1])
        draw_text_with_glow(screen, fonts.large, score, text_pos, Colors.TEXT_PRIMARY,
                           glow_color=color1, glow_intensity=3)
    
    # Draw pits
    for pit_id, pos in pit_positions.items():
        is_ai1_pit = 0 <= pit_id <= 5
        is_highlighted = highlight_pit == pit_id
        
        pit_pos = (pos[0] + shake_offset[0], pos[1] + shake_offset[1])
        
        if is_highlighted:
            pit_color = Colors.PIT_SELECTED
            glow_color = Colors.NEON_YELLOW
            glow_intensity = 1.2
        else:
            pit_color = Colors.PIT_ACTIVE if mancala[pit_id] > 0 else Colors.PIT_INACTIVE
            glow_color = Colors.PLAYER1_PRIMARY if is_ai1_pit else Colors.PLAYER2_PRIMARY
            glow_intensity = 0.4 if mancala[pit_id] > 0 else 0.1
        
        if glow_intensity > 0.2:
            draw_neon_glow(screen, pit_pos, Dimensions.PIT_RADIUS, glow_color, glow_intensity)
        
        draw_radial_gradient(screen, pit_pos, pit_color, Colors.PIT_INACTIVE, Dimensions.PIT_RADIUS)
        
        border_color = glow_color if mancala[pit_id] > 0 else Colors.PIT_BORDER_INACTIVE
        pygame.draw.circle(screen, border_color, pit_pos, Dimensions.PIT_RADIUS, width=3)
        
        # Inner shadow
        shadow_surf = pygame.Surface((Dimensions.PIT_RADIUS * 3, Dimensions.PIT_RADIUS * 3), pygame.SRCALPHA)
        for i in range(5):
            alpha = 40 - i * 8
            pygame.draw.circle(shadow_surf, (0, 0, 0, alpha),
                             (Dimensions.PIT_RADIUS * 1.5, Dimensions.PIT_RADIUS * 1.5),
                             Dimensions.PIT_RADIUS - i * 2)
        screen.blit(shadow_surf, (pit_pos[0] - Dimensions.PIT_RADIUS * 1.5,
                                  pit_pos[1] - Dimensions.PIT_RADIUS * 1.5))
        
        stone_count = mancala[pit_id]
        count_color = Colors.TEXT_PRIMARY if stone_count > 0 else Colors.TEXT_SECONDARY
        draw_text_with_glow(screen, fonts.medium, str(stone_count), pit_pos,
                           count_color, glow_color=glow_color if mancala[pit_id] > 0 else None,
                           glow_intensity=2 if mancala[pit_id] > 0 else 0)
    
    animation_manager.draw(screen)
    
    # AI 1 Panel (bottom left) - FIXED: No overlap with board
    ai1_panel_rect = pygame.Rect(20, Dimensions.SCREEN_HEIGHT - 160, 
                                  Dimensions.PANEL_WIDTH, Dimensions.PANEL_HEIGHT)
    draw_glassmorphic_panel(screen, ai1_panel_rect)
    
    draw_neon_glow(screen, (ai1_panel_rect.x + 40, ai1_panel_rect.y + 30), 15, Colors.PLAYER1_PRIMARY, 0.8)
    pygame.draw.circle(screen, Colors.PLAYER1_PRIMARY, (ai1_panel_rect.x + 40, ai1_panel_rect.y + 30), 15)
    
    ai1_title = fonts.small.render("🤖 AI 1 Win Chance", True, Colors.TEXT_SECONDARY)
    screen.blit(ai1_title, (ai1_panel_rect.x + 70, ai1_panel_rect.y + 20))
    
    draw_text_with_glow(screen, fonts.large, f"{ai1_prob:.1f}%",
                       (ai1_panel_rect.x + 70, ai1_panel_rect.y + 65),
                       Colors.PLAYER1_PRIMARY, glow_color=Colors.PLAYER1_PRIMARY, glow_intensity=2)
    
    bar_rect = pygame.Rect(ai1_panel_rect.x + 25, ai1_panel_rect.y + 105,
                          Dimensions.PANEL_WIDTH - 50, 18)
    from ui_config_enhanced import draw_progress_bar
    draw_progress_bar(screen, bar_rect, ai1_prob / 100,
                     Colors.PLAYER1_PRIMARY, Colors.PLAYER1_SECONDARY)
    
    # AI 2 Panel (top-left corner) - FIXED: Top corner position
    ai2_panel_rect = pygame.Rect(20, 20, Dimensions.PANEL_WIDTH, Dimensions.PANEL_HEIGHT)
    draw_glassmorphic_panel(screen, ai2_panel_rect)
    
    draw_neon_glow(screen, (ai2_panel_rect.x + 40, ai2_panel_rect.y + 30), 15, Colors.PLAYER2_PRIMARY, 0.8)
    pygame.draw.circle(screen, Colors.PLAYER2_PRIMARY, (ai2_panel_rect.x + 40, ai2_panel_rect.y + 30), 15)
    
    ai2_title = fonts.small.render("🤖 AI 2 Win Chance", True, Colors.TEXT_SECONDARY)
    screen.blit(ai2_title, (ai2_panel_rect.x + 70, ai2_panel_rect.y + 20))
    
    draw_text_with_glow(screen, fonts.large, f"{ai2_prob:.1f}%",
                       (ai2_panel_rect.x + 70, ai2_panel_rect.y + 65),
                       Colors.PLAYER2_PRIMARY, glow_color=Colors.PLAYER2_PRIMARY, glow_intensity=2)
    
    bar_rect = pygame.Rect(ai2_panel_rect.x + 25, ai2_panel_rect.y + 105,
                          Dimensions.PANEL_WIDTH - 50, 18)
    draw_progress_bar(screen, bar_rect, ai2_prob / 100,
                     Colors.PLAYER2_PRIMARY, Colors.PLAYER2_SECONDARY)
    
    # Move counter
    move_panel_rect = pygame.Rect(Dimensions.SCREEN_WIDTH - 250, 40, 210, 80)
    draw_glassmorphic_panel(screen, move_panel_rect)
    
    move_text = f"Move: {move_count}"
    draw_text_with_glow(screen, fonts.normal, move_text,
                       (move_panel_rect.centerx, move_panel_rect.centery),
                       Colors.TEXT_PRIMARY, glow_color=Colors.NEON_BLUE, glow_intensity=2)
    
    # Turn indicator
    animation_manager.draw_turn_indicator(screen, fonts.large)
    
    pygame.display.flip()


def game_over_popup(message, ai1_score, ai2_score):
    """Ultra-modern game over popup"""
    popup_width, popup_height = 700, 500
    popup_x = (Dimensions.SCREEN_WIDTH - popup_width) // 2
    popup_y = (Dimensions.SCREEN_HEIGHT - popup_height) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    
    overlay = pygame.Surface((Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))
    
    if "AI 1" in message:
        color1, color2 = Colors.PLAYER1_PRIMARY, Colors.PLAYER1_SECONDARY
    elif "AI 2" in message:
        color1, color2 = Colors.PLAYER2_PRIMARY, Colors.PLAYER2_SECONDARY
    else:
        color1, color2 = Colors.NEON_YELLOW, Colors.NEON_ORANGE
    
    draw_neon_glow(screen, popup_rect.center, popup_width // 2, color1, 0.8, layers=6)
    
    popup_surf = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
    draw_gradient_rect(popup_surf, Colors.BG_DARK_PRIMARY, Colors.BG_DARK_SECONDARY,
                      pygame.Rect(0, 0, popup_width, popup_height),
                      vertical=True, border_radius=50)
    popup_surf.set_alpha(240)
    screen.blit(popup_surf, popup_rect.topleft)
    
    for i in range(3):
        border_alpha = 200 - i * 60
        pygame.draw.rect(screen, (*color1, border_alpha), popup_rect.inflate(i * 4, i * 4),
                        width=3, border_radius=50)
    
    draw_text_with_glow(screen, fonts.mega, "GAME OVER",
                       (popup_x + popup_width // 2, popup_y + 100),
                       Colors.TEXT_PRIMARY, glow_color=color1, glow_intensity=4)
    
    draw_text_with_glow(screen, fonts.large, message,
                       (popup_x + popup_width // 2, popup_y + 220),
                       color1, glow_color=color1, glow_intensity=3)
    
    score_y = popup_y + 310
    ai1_text = f"AI 1: {ai1_score}"
    draw_text_with_glow(screen, fonts.medium, ai1_text,
                       (popup_x + popup_width // 2 - 100, score_y),
                       Colors.PLAYER1_PRIMARY, glow_color=Colors.PLAYER1_PRIMARY,
                       glow_intensity=2)
    
    vs_text = fonts.normal.render("VS", True, Colors.TEXT_SECONDARY)
    vs_rect = vs_text.get_rect(center=(popup_x + popup_width // 2, score_y))
    screen.blit(vs_text, vs_rect)
    
    ai2_text = f"AI 2: {ai2_score}"
    draw_text_with_glow(screen, fonts.medium, ai2_text,
                       (popup_x + popup_width // 2 + 100, score_y),
                       Colors.PLAYER2_PRIMARY, glow_color=Colors.PLAYER2_PRIMARY,
                       glow_intensity=2)
    
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

    def animated_player_move(self, pit_index, animation_manager, ai1_prob, ai2_prob, move_count, phase, draw_callback):
        """
        Execute move with step-by-step animation showing each marble being distributed.
        draw_callback should be a function that draws the board after each marble placement.
        """
        j = pit_index
        repeat_turn = False
        stones_to_distribute = self.mancala[j]
        self.mancala[j] = 0
        
        current_pos = j
        
        if pit_index > 6:  # North player (AI 2)
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
                                ai1_prob=ai1_prob, ai2_prob=ai2_prob,
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
                            ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                            move_count=move_count, phase=phase)
                time.sleep(0.3)
            
            if current_pos == 13:
                repeat_turn = True
                
        else:  # South player (AI 1)
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
                                ai1_prob=ai1_prob, ai2_prob=ai2_prob,
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
                            ai1_prob=ai1_prob, ai2_prob=ai2_prob,
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


def ai_vs_ai():
    mancala_board = Mancala_Board(None)
    animation_manager = AnimationManager((Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT))
    
    running = True
    ai1_turn = True
    move_count = 0
    phase = 0
    
    animation_manager.start_transition(fade_in=True)
    animation_manager.show_turn_indicator("AI 1's Turn", Colors.PLAYER1_PRIMARY)
    
    ai1_prob = calculate_winning_probability(mancala_board.mancala, 1)
    ai2_prob = calculate_winning_probability(mancala_board.mancala, 2)
    
    # Show initial board with fade-in animation
    start_time = time.time()
    while time.time() - start_time < 2.0:  # Increased from 1.5 to 2.0 seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        animation_manager.update()
        phase += 0.5
        draw_board(mancala_board.mancala, animation_manager,
                   ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                   turn_message="AI 1's Turn", move_count=move_count, phase=phase)
        clock.tick(60)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pass  # Speed up
        
        if not mancala_board.isEnd():
            if ai1_turn:
                # Show "AI 1 Thinking..." - 1 second
                animation_manager.show_turn_indicator("AI 1 Thinking...", Colors.PLAYER1_PRIMARY)
                think_start = time.time()
                while time.time() - think_start < 1.0:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    animation_manager.update()
                    phase += 0.5
                    draw_board(mancala_board.mancala, animation_manager,
                             ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                             move_count=move_count, phase=phase)
                    clock.tick(60)
                
                _, ai_move = alphabeta(mancala_board, 5, -100000, 100000, False)
                if ai_move != -1:
                    move_count += 1
                    
                    # Show AI 1 thinking - highlight the pit it will choose - 1 second
                    board_rect = LayoutCalculator.get_board_rect(Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT)
                    pit_positions = LayoutCalculator.get_pit_positions(board_rect)
                    
                    pre_move_start = time.time()
                    while time.time() - pre_move_start < 1.0:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        animation_manager.update()
                        phase += 0.5
                        draw_board(mancala_board.mancala, animation_manager, highlight_pit=ai_move,
                                 ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                                 move_count=move_count, phase=phase)
                        clock.tick(60)
                    
                    animation_manager.emit_fountain(*pit_positions[ai_move], count=35)
                    
                    # Use animated move to show marble distribution step by step
                    def draw_callback(mancala, anim_mgr, highlight_pit, ai1_prob, ai2_prob, move_count, phase):
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        anim_mgr.update()
                        draw_board(mancala, anim_mgr, highlight_pit=highlight_pit,
                                 ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                                 move_count=move_count, phase=phase)
                    
                    repeat_turn = mancala_board.animated_player_move(
                        ai_move, animation_manager, ai1_prob, ai2_prob, 
                        move_count, phase, draw_callback
                    )
                    
                    ai1_prob = calculate_winning_probability(mancala_board.mancala, 1)
                    ai2_prob = calculate_winning_probability(mancala_board.mancala, 2)
                    
                    if repeat_turn:
                        animation_manager.show_turn_indicator("AI 1 Extra Turn!", Colors.NEON_GREEN)
                    else:
                        animation_manager.show_turn_indicator("AI 2's Turn", Colors.PLAYER2_PRIMARY)
                    
                    draw_board(mancala_board.mancala, animation_manager, highlight_pit=ai_move,
                             ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                             move_count=move_count, phase=phase)
                    
                    # Show the result - 2 seconds when switching players, 1 second for extra turn
                    result_display_time = 1.0 if repeat_turn else 2.0
                    move_start = time.time()
                    while time.time() - move_start < result_display_time:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        animation_manager.update()
                        phase += 0.5
                        draw_board(mancala_board.mancala, animation_manager, highlight_pit=ai_move,
                                 ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                                 move_count=move_count, phase=phase)
                        clock.tick(60)
                    
                    ai1_turn = repeat_turn
                else:
                    ai1_turn = False
            else:
                # Show "AI 2 Thinking..." - 1 second
                animation_manager.show_turn_indicator("AI 2 Thinking...", Colors.PLAYER2_PRIMARY)
                think_start = time.time()
                while time.time() - think_start < 1.0:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    animation_manager.update()
                    phase += 0.5
                    draw_board(mancala_board.mancala, animation_manager,
                             ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                             move_count=move_count, phase=phase)
                    clock.tick(60)
                
                _, ai_move = alphabeta(mancala_board, 5, -100000, 100000, True)
                if ai_move != -1:
                    move_count += 1
                    
                    # Show AI 2 thinking - highlight the pit it will choose - 1 second
                    board_rect = LayoutCalculator.get_board_rect(Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT)
                    pit_positions = LayoutCalculator.get_pit_positions(board_rect)
                    
                    pre_move_start = time.time()
                    while time.time() - pre_move_start < 1.0:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        animation_manager.update()
                        phase += 0.5
                        draw_board(mancala_board.mancala, animation_manager, highlight_pit=ai_move,
                                 ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                                 move_count=move_count, phase=phase)
                        clock.tick(60)
                    
                    animation_manager.emit_fountain(*pit_positions[ai_move], count=35)
                    
                    # Use animated move to show marble distribution step by step
                    def draw_callback(mancala, anim_mgr, highlight_pit, ai1_prob, ai2_prob, move_count, phase):
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        anim_mgr.update()
                        draw_board(mancala, anim_mgr, highlight_pit=highlight_pit,
                                 ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                                 move_count=move_count, phase=phase)
                    
                    repeat_turn = mancala_board.animated_player_move(
                        ai_move, animation_manager, ai1_prob, ai2_prob, 
                        move_count, phase, draw_callback
                    )
                    
                    ai1_prob = calculate_winning_probability(mancala_board.mancala, 1)
                    ai2_prob = calculate_winning_probability(mancala_board.mancala, 2)
                    
                    if repeat_turn:
                        animation_manager.show_turn_indicator("AI 2 Extra Turn!", Colors.NEON_PINK)
                    else:
                        animation_manager.show_turn_indicator("AI 1's Turn", Colors.PLAYER1_PRIMARY)
                    
                    draw_board(mancala_board.mancala, animation_manager, highlight_pit=ai_move,
                             ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                             move_count=move_count, phase=phase)
                    
                    # Show the result - 2 seconds when switching players, 1 second for extra turn
                    result_display_time = 1.0 if repeat_turn else 2.0
                    move_start = time.time()
                    while time.time() - move_start < result_display_time:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        animation_manager.update()
                        phase += 0.5
                        draw_board(mancala_board.mancala, animation_manager, highlight_pit=ai_move,
                                 ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                                 move_count=move_count, phase=phase)
                        clock.tick(60)
                    
                    ai1_turn = not repeat_turn
                else:
                    ai1_turn = True
        
        animation_manager.update()
        phase += 0.5
        
        if mancala_board.isEnd():
            ai1_score = mancala_board.mancala[6]
            ai2_score = mancala_board.mancala[13]
            
            animation_manager.trigger_shake(intensity=18)
            animation_manager.emit_particles(Dimensions.SCREEN_WIDTH // 2,
                                           Dimensions.SCREEN_HEIGHT // 2, count=100, explosion=True)
            
            if ai2_score > ai1_score:
                winner_message = "AI 2 WINS!"
            elif ai1_score > ai2_score:
                winner_message = "AI 1 WINS!"
            else:
                winner_message = "TIE GAME!"
            
            for _ in range(40):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                animation_manager.update()
                phase += 0.5
                draw_board(mancala_board.mancala, animation_manager,
                          ai1_prob=ai1_prob, ai2_prob=ai2_prob,
                          move_count=move_count, phase=phase)
                clock.tick(30)
            
            game_over_popup(winner_message, ai1_score, ai2_score)
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            waiting = False
                            running = False
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
        
        clock.tick(60)


def splash_screen():
    """Ultra-modern splash screen"""
    phase = 0
    waiting = True
    
    while waiting:
        draw_animated_background(screen, phase)
        
        title_pos = (Dimensions.SCREEN_WIDTH // 2, Dimensions.SCREEN_HEIGHT // 2 - 120)
        draw_neon_glow(screen, title_pos, 200, Colors.NEON_BLUE, 0.6, layers=8)
        draw_text_with_glow(screen, fonts.mega, "MANCALA", title_pos,
                           Colors.TEXT_PRIMARY, glow_color=Colors.NEON_BLUE,
                           glow_intensity=5)
        
        subtitle_pos = (Dimensions.SCREEN_WIDTH // 2, Dimensions.SCREEN_HEIGHT // 2 + 20)
        draw_text_with_glow(screen, fonts.large, "AI vs AI Mode",
                           subtitle_pos, Colors.NEON_PURPLE,
                           glow_color=Colors.NEON_PURPLE, glow_intensity=3)
        
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
    ai_vs_ai()

'''ai_vs_ai_enhanced.py ends here'''