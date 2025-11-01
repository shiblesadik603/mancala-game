"""
Enhanced Mancala - Player vs Player with Beautiful Modern UI
"""
import pygame
import sys
import time
import random
from ui_config_enhanced import Colors, Dimensions, Fonts, fonts, draw_gradient_rect, draw_3d_circle, LayoutCalculator
from animations import AnimationManager

pygame.init()

screen = pygame.display.set_mode((Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT))
pygame.display.set_caption('Mancala - Player vs Player')


def draw_background(surface):
    """Draw gradient background"""
    draw_gradient_rect(surface, Colors.BG_GRADIENT_TOP, Colors.BG_GRADIENT_BOTTOM,
                      pygame.Rect(0, 0, Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT),
                      vertical=True)


def draw_board(mancala, animation_manager, highlight_pit=None, turn_message="", current_player=1):
    """Draw the beautiful game board"""
    draw_background(screen)
    
    board_rect = LayoutCalculator.get_board_rect(Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT)
    pit_positions = LayoutCalculator.get_pit_positions(board_rect)
    mancala_positions = LayoutCalculator.get_mancala_positions(board_rect)
    
    # Apply shake offset if active
    shake_offset = animation_manager.get_shake_offset()
    
    # Draw board shadow
    shadow_rect = board_rect.move(8 + shake_offset[0], 8 + shake_offset[1])
    shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 80), 
                    (0, 0, shadow_rect.width, shadow_rect.height), 
                    border_radius=Dimensions.BOARD_BORDER_RADIUS)
    screen.blit(shadow_surf, shadow_rect.topleft)
    
    # Draw main board with gradient
    board_surf = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
    draw_gradient_rect(board_surf, Colors.BOARD_WOOD, Colors.BOARD_DARK,
                      pygame.Rect(0, 0, board_rect.width, board_rect.height),
                      vertical=False, border_radius=Dimensions.BOARD_BORDER_RADIUS)
    screen.blit(board_surf, (board_rect.x + shake_offset[0], board_rect.y + shake_offset[1]))
    
    # Draw border
    pygame.draw.rect(screen, Colors.BOARD_DARK, 
                    board_rect.move(shake_offset[0], shake_offset[1]), 
                    width=4, border_radius=Dimensions.BOARD_BORDER_RADIUS)
    
    # Draw mancala stores with gradient
    for store_id, store_rect in mancala_positions.items():
        # Shadow
        shadow = store_rect.move(5 + shake_offset[0], 5 + shake_offset[1])
        shadow_surf = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60),
                        (0, 0, shadow.width, shadow.height),
                        border_radius=Dimensions.MANCALA_BORDER_RADIUS)
        screen.blit(shadow_surf, shadow.topleft)
        
        # Gradient store (store 6 = Player 2, store 13 = Player 1)
        color1 = Colors.PLAYER2_COLOR if store_id == 6 else Colors.PLAYER1_COLOR
        color2 = Colors.PLAYER2_DARK if store_id == 6 else Colors.PLAYER1_DARK
        
        store_surf = pygame.Surface((store_rect.width, store_rect.height), pygame.SRCALPHA)
        draw_gradient_rect(store_surf, color1, color2,
                          pygame.Rect(0, 0, store_rect.width, store_rect.height),
                          vertical=True, border_radius=Dimensions.MANCALA_BORDER_RADIUS)
        screen.blit(store_surf, (store_rect.x + shake_offset[0], store_rect.y + shake_offset[1]))
        
        # Border
        pygame.draw.rect(screen, Colors.WHITE,
                        store_rect.move(shake_offset[0], shake_offset[1]),
                        width=3, border_radius=Dimensions.MANCALA_BORDER_RADIUS)
        
        # Score text
        score_text = fonts.large.render(str(mancala[store_id]), True, Colors.WHITE)
        text_rect = score_text.get_rect(center=(store_rect.centerx + shake_offset[0], 
                                                 store_rect.centery + shake_offset[1]))
        screen.blit(score_text, text_rect)
    
    # Draw pits
    for pit_id, pos in pit_positions.items():
        is_highlighted = highlight_pit == pit_id
        
        # Determine if this pit is clickable for current player
        is_clickable = False
        if current_player == 1 and 7 <= pit_id <= 12:  # Player 1 (top)
            is_clickable = mancala[pit_id] > 0
        elif current_player == 2 and 0 <= pit_id <= 5:  # Player 2 (bottom)
            is_clickable = mancala[pit_id] > 0
        
        # Shadow
        shadow_pos = (pos[0] + 4 + shake_offset[0], pos[1] + 4 + shake_offset[1])
        pygame.draw.circle(screen, (0, 0, 0, 60), shadow_pos, Dimensions.PIT_RADIUS)
        
        # Pit color
        if is_highlighted:
            pit_color = Colors.HIGHLIGHT
        elif is_clickable:
            pit_color = Colors.ACCENT  # Highlight clickable pits
        else:
            pit_color = Colors.PIT_COLOR
        
        # Draw 3D pit
        pit_pos = (pos[0] + shake_offset[0], pos[1] + shake_offset[1])
        draw_3d_circle(screen, pit_color, pit_pos, Dimensions.PIT_RADIUS, depth=6)
        
        # Border
        pygame.draw.circle(screen, Colors.PIT_SHADOW, pit_pos, 
                         Dimensions.PIT_RADIUS, width=Dimensions.PIT_BORDER_WIDTH)
        
        # Stones count
        stone_count = mancala[pit_id]
        count_text = fonts.medium.render(str(stone_count), True, Colors.WHITE)
        text_rect = count_text.get_rect(center=pit_pos)
        
        # Text shadow
        shadow_text = fonts.medium.render(str(stone_count), True, Colors.DARK_GRAY)
        shadow_rect = text_rect.move(2, 2)
        screen.blit(shadow_text, shadow_rect)
        screen.blit(count_text, text_rect)
    
    # Draw animations
    animation_manager.draw(screen)
    
    # Draw Player 1 panel (top left)
    p1_panel_rect = pygame.Rect(20, 20, 280, 100)
    panel_color = Colors.PLAYER1_COLOR if current_player == 1 else Colors.GRAY
    panel_surf = pygame.Surface((p1_panel_rect.width, p1_panel_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (*panel_color, 200), 
                    (0, 0, p1_panel_rect.width, p1_panel_rect.height),
                    border_radius=Dimensions.PANEL_BORDER_RADIUS)
    screen.blit(panel_surf, p1_panel_rect.topleft)
    
    p1_title = fonts.small.render("👤 Player 1 (Top)", True, Colors.WHITE)
    screen.blit(p1_title, (p1_panel_rect.x + 15, p1_panel_rect.y + 15))
    
    p1_score = fonts.large.render(f"{mancala[13]}", True, Colors.WHITE)
    screen.blit(p1_score, (p1_panel_rect.x + 15, p1_panel_rect.y + 50))
    
    # Draw Player 2 panel (bottom left)
    p2_panel_rect = pygame.Rect(20, Dimensions.SCREEN_HEIGHT - 130, 280, 100)
    panel_color = Colors.PLAYER2_COLOR if current_player == 2 else Colors.GRAY
    panel_surf = pygame.Surface((p2_panel_rect.width, p2_panel_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (*panel_color, 200),
                    (0, 0, p2_panel_rect.width, p2_panel_rect.height),
                    border_radius=Dimensions.PANEL_BORDER_RADIUS)
    screen.blit(panel_surf, p2_panel_rect.topleft)
    
    p2_title = fonts.small.render("👤 Player 2 (Bottom)", True, Colors.WHITE)
    screen.blit(p2_title, (p2_panel_rect.x + 15, p2_panel_rect.y + 15))
    
    p2_score = fonts.large.render(f"{mancala[6]}", True, Colors.WHITE)
    screen.blit(p2_score, (p2_panel_rect.x + 15, p2_panel_rect.y + 50))
    
    # Turn message
    if turn_message:
        turn_surf = fonts.large.render(turn_message, True, Colors.TEXT_PRIMARY)
        turn_rect = turn_surf.get_rect(center=(Dimensions.SCREEN_WIDTH // 2, 
                                               Dimensions.SCREEN_HEIGHT - 80))
        
        # Panel behind text
        panel_rect = pygame.Rect(turn_rect.x - 30, turn_rect.y - 15,
                                turn_rect.width + 60, turn_rect.height + 30)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (*Colors.WHITE, 220),
                        (0, 0, panel_rect.width, panel_rect.height),
                        border_radius=Dimensions.PANEL_BORDER_RADIUS)
        screen.blit(panel_surf, panel_rect.topleft)
        
        screen.blit(turn_surf, turn_rect)
    
    pygame.display.flip()


def game_over_popup(message, p1_score, p2_score):
    """Beautiful game over popup"""
    popup_width, popup_height = 500, 350
    popup_x = (Dimensions.SCREEN_WIDTH - popup_width) // 2
    popup_y = (Dimensions.SCREEN_HEIGHT - popup_height) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    
    # Semi-transparent background
    overlay = pygame.Surface((Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Popup shadow
    shadow_rect = popup_rect.move(8, 8)
    shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 100),
                    (0, 0, shadow_rect.width, shadow_rect.height),
                    border_radius=30)
    screen.blit(shadow_surf, shadow_rect.topleft)
    
    # Main popup with gradient
    popup_surf = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
    
    if "Player 1" in message:
        color1, color2 = Colors.PLAYER1_COLOR, Colors.PLAYER1_DARK
    elif "Player 2" in message:
        color1, color2 = Colors.PLAYER2_COLOR, Colors.PLAYER2_DARK
    else:
        color1, color2 = Colors.ACCENT, Colors.ACCENT_DARK
    
    draw_gradient_rect(popup_surf, color1, color2,
                      pygame.Rect(0, 0, popup_width, popup_height),
                      vertical=True, border_radius=30)
    screen.blit(popup_surf, popup_rect.topleft)
    
    # Border
    pygame.draw.rect(screen, Colors.WHITE, popup_rect, width=4, border_radius=30)
    
    # Title
    title_text = fonts.large.render("GAME OVER", True, Colors.WHITE)
    title_rect = title_text.get_rect(center=(popup_x + popup_width // 2, popup_y + 60))
    screen.blit(title_text, title_rect)
    
    # Result
    result_text = fonts.medium.render(message, True, Colors.WHITE)
    result_rect = result_text.get_rect(center=(popup_x + popup_width // 2, popup_y + 130))
    screen.blit(result_text, result_rect)
    
    # Scores
    score_text = fonts.normal.render(f"Player 1: {p1_score}  -  Player 2: {p2_score}", True, Colors.WHITE)
    score_rect = score_text.get_rect(center=(popup_x + popup_width // 2, popup_y + 190))
    screen.blit(score_text, score_rect)
    
    # Instructions
    restart_text = fonts.small.render("Press SPACE to play again", True, Colors.WHITE)
    restart_rect = restart_text.get_rect(center=(popup_x + popup_width // 2, popup_y + 250))
    screen.blit(restart_text, restart_rect)
    
    quit_text = fonts.small.render("Press ESC to quit", True, Colors.WHITE)
    quit_rect = quit_text.get_rect(center=(popup_x + popup_width // 2, popup_y + 285))
    screen.blit(quit_text, quit_rect)
    
    pygame.display.flip()


class Mancala_Board:
    def __init__(self, mancala=None):
        if mancala is not None:
            self.mancala = mancala[:]
        else:
            self.mancala = [4] * 6 + [0] + [4] * 6 + [0]

    def player_move(self, i):
        j = i
        repeat_turn = False
        add = self.mancala[j]
        self.mancala[j] = 0
        stones = add
        
        while stones > 0:
            i += 1
            if i > 13:
                i = 0
            # Skip opponent's mancala
            if (j <= 5 and i == 13) or (j >= 7 and i == 6):
                continue
            self.mancala[i] += 1
            stones -= 1
        
        # Capture stones
        if (j <= 5 and 0 <= i <= 5 and self.mancala[i] == 1) or \
           (j >= 7 and 7 <= i <= 12 and self.mancala[i] == 1):
            opposite_pit = 12 - i
            if self.mancala[opposite_pit] > 0:
                if j <= 5:  # Player 2
                    self.mancala[6] += 1 + self.mancala[opposite_pit]
                else:  # Player 1
                    self.mancala[13] += 1 + self.mancala[opposite_pit]
                self.mancala[i] = 0
                self.mancala[opposite_pit] = 0
        
        # Check for extra turn
        if (j <= 5 and i == 6) or (j >= 7 and i == 13):
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


def player_vs_player():
    mancala_board = Mancala_Board(None)
    animation_manager = AnimationManager((Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT))
    
    clock = pygame.time.Clock()
    running = True
    current_player = random.choice([1, 2])  # Random starting player
    selected_pit = -1
    
    # Start with fade in
    animation_manager.start_transition(fade_in=True)
    
    draw_board(mancala_board.mancala, animation_manager,
              turn_message=f"Player {current_player}'s Turn",
              current_player=current_player)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                board_rect = LayoutCalculator.get_board_rect(Dimensions.SCREEN_WIDTH, Dimensions.SCREEN_HEIGHT)
                pit_positions = LayoutCalculator.get_pit_positions(board_rect)
                
                for pit_id, pos in pit_positions.items():
                    distance = ((x - pos[0]) ** 2 + (y - pos[1]) ** 2) ** 0.5
                    if distance <= Dimensions.PIT_RADIUS:
                        # Check if valid move for current player
                        if current_player == 1 and 7 <= pit_id <= 12 and mancala_board.mancala[pit_id] > 0:
                            selected_pit = pit_id
                            animation_manager.emit_particles(pos[0], pos[1], count=20)
                            break
                        elif current_player == 2 and 0 <= pit_id <= 5 and mancala_board.mancala[pit_id] > 0:
                            selected_pit = pit_id
                            animation_manager.emit_particles(pos[0], pos[1], count=20)
                            break
        
        # Execute move
        if selected_pit != -1:
            repeat_turn = mancala_board.player_move(selected_pit)
            
            draw_board(mancala_board.mancala, animation_manager,
                      highlight_pit=selected_pit,
                      turn_message=f"Player {current_player}'s Turn" if repeat_turn else f"Player {3 - current_player}'s Turn",
                      current_player=current_player if repeat_turn else (3 - current_player))
            time.sleep(0.4)
            
            if not repeat_turn:
                current_player = 3 - current_player  # Switch player (1->2, 2->1)
            
            selected_pit = -1
        
        # Update animations
        animation_manager.update()
        
        # Game over
        if mancala_board.isEnd():
            p1_score = mancala_board.mancala[13]
            p2_score = mancala_board.mancala[6]
            
            animation_manager.trigger_shake(intensity=10)
            animation_manager.emit_particles(Dimensions.SCREEN_WIDTH // 2, 
                                           Dimensions.SCREEN_HEIGHT // 2, count=50)
            
            if p1_score > p2_score:
                winner_message = "Player 1 WINS!"
            elif p2_score > p1_score:
                winner_message = "Player 2 WINS!"
            else:
                winner_message = "TIE GAME!"
            
            # Draw final state
            for _ in range(20):
                animation_manager.update()
                draw_board(mancala_board.mancala, animation_manager,
                          turn_message="", current_player=current_player)
                time.sleep(0.05)
            
            game_over_popup(winner_message, p1_score, p2_score)
            
            # Wait for restart
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
        
        # Redraw
        if not mancala_board.isEnd():
            draw_board(mancala_board.mancala, animation_manager,
                      turn_message=f"Player {current_player}'s Turn",
                      current_player=current_player)
        
        clock.tick(60)


def splash_screen():
    """Beautiful splash screen"""
    draw_background(screen)
    
    # Title with shadow
    title_text = fonts.title.render("MANCALA", True, Colors.WHITE)
    title_rect = title_text.get_rect(center=(Dimensions.SCREEN_WIDTH // 2, 
                                             Dimensions.SCREEN_HEIGHT // 2 - 80))
    
    shadow_text = fonts.title.render("MANCALA", True, Colors.DARK_GRAY)
    shadow_rect = title_rect.move(4, 4)
    screen.blit(shadow_text, shadow_rect)
    screen.blit(title_text, title_rect)
    
    # Subtitle
    subtitle = fonts.medium.render("Player vs Player", True, Colors.ACCENT)
    subtitle_rect = subtitle.get_rect(center=(Dimensions.SCREEN_WIDTH // 2, 
                                              Dimensions.SCREEN_HEIGHT // 2 + 20))
    screen.blit(subtitle, subtitle_rect)
    
    # Prompt
    prompt = fonts.normal.render("Press any key to start", True, Colors.TEXT_ON_DARK)
    prompt_rect = prompt.get_rect(center=(Dimensions.SCREEN_WIDTH // 2, 
                                         Dimensions.SCREEN_HEIGHT // 2 + 120))
    screen.blit(prompt, prompt_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False


while True:
    splash_screen()
    player_vs_player()

'''player vs player.py ends here'''