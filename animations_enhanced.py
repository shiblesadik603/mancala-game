"""
Advanced Animation System with Particle Effects and Smooth Transitions
"""
import pygame
import random
import math
from ui_config_enhanced import Colors, Dimensions, AnimationConfig, ease_out_cubic, ease_in_out_cubic


class EnhancedParticle:
    """Enhanced particle with trails and glow"""
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = AnimationConfig.PARTICLE_LIFETIME
        self.max_lifetime = AnimationConfig.PARTICLE_LIFETIME
        self.size = random.randint(3, 7)
        self.trail = []
        self.max_trail_length = 5
    
    def update(self):
        """Update particle with trail"""
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += AnimationConfig.PARTICLE_GRAVITY
        self.velocity_x *= 0.98  # Air resistance
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, surface):
        """Draw particle with trail and glow"""
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            trail_alpha = int(alpha * (i / len(self.trail)) * 0.5)
            trail_size = int(self.size * (i / len(self.trail)))
            if trail_alpha > 0 and trail_size > 0:
                trail_surf = pygame.Surface((trail_size * 3, trail_size * 3), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (*self.color[:3], trail_alpha),
                                 (trail_size * 1.5, trail_size * 1.5), trail_size)
                surface.blit(trail_surf, (int(tx - trail_size * 1.5), int(ty - trail_size * 1.5)))
        
        # Draw glow
        glow_size = self.size * 2
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        for i in range(3):
            glow_alpha = int(alpha * 0.3 / (i + 1))
            pygame.draw.circle(glow_surf, (*self.color[:3], glow_alpha),
                             (glow_size, glow_size), glow_size + i * 3)
        surface.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))
        
        # Draw main particle
        if alpha > 0:
            particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*self.color[:3], alpha),
                             (self.size, self.size), self.size)
            surface.blit(particle_surf, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    """Manages enhanced particles"""
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, count=20, colors=None, explosion=False):
        """Emit particles with optional explosion effect"""
        if colors is None:
            colors = Colors.STONE_COLORS
        
        for _ in range(count):
            if explosion:
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(4, 10)
            else:
                angle = random.uniform(-math.pi/3, -2*math.pi/3)
                speed = random.uniform(3, 7)
            
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            color = random.choice(colors)
            self.particles.append(EnhancedParticle(x, y, color, velocity_x, velocity_y))
    
    def emit_fountain(self, x, y, count=15):
        """Emit particles in fountain pattern"""
        for _ in range(count):
            angle = random.uniform(-math.pi * 0.6, -math.pi * 0.4)
            speed = random.uniform(5, 9)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            color = random.choice(Colors.STONE_COLORS)
            self.particles.append(EnhancedParticle(x, y, color, velocity_x, velocity_y))
    
    def update(self):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(surface)
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()


class PulseGlow:
    """Pulsing glow effect for active elements"""
    def __init__(self, position, radius, color, intensity=1.0):
        self.position = position
        self.radius = radius
        self.color = color
        self.base_intensity = intensity
        self.phase = 0
    
    def update(self):
        """Update pulse animation"""
        self.phase += AnimationConfig.GLOW_PULSE_SPEED
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi
    
    def draw(self, surface):
        """Draw pulsing glow"""
        intensity = self.base_intensity * (0.7 + 0.3 * math.sin(self.phase))
        alpha_base = int(AnimationConfig.GLOW_MIN_ALPHA + 
                        (AnimationConfig.GLOW_MAX_ALPHA - AnimationConfig.GLOW_MIN_ALPHA) * 
                        (0.5 + 0.5 * math.sin(self.phase)))
        
        glow_radius = int(self.radius * (1 + 0.2 * math.sin(self.phase)))
        
        # Draw multiple glow layers
        for i in range(4):
            layer_radius = int(glow_radius * (1 + i * 0.3))
            alpha = int(alpha_base / (i + 1) * intensity)
            glow_surf = pygame.Surface((layer_radius * 3, layer_radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color[:3], alpha),
                             (layer_radius * 1.5, layer_radius * 1.5), layer_radius)
            surface.blit(glow_surf, 
                        (self.position[0] - layer_radius * 1.5,
                         self.position[1] - layer_radius * 1.5))


class HoverEffect:
    """Smooth hover animation for pits"""
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius
        self.current_scale = 1.0
        self.target_scale = 1.0
        self.is_hovering = False
    
    def set_hover(self, hovering):
        """Set hover state"""
        self.is_hovering = hovering
        self.target_scale = Dimensions.PIT_HOVER_SCALE if hovering else 1.0
    
    def update(self):
        """Update hover animation"""
        diff = self.target_scale - self.current_scale
        self.current_scale += diff * AnimationConfig.HOVER_SCALE_SPEED
    
    def get_scaled_radius(self):
        """Get current scaled radius"""
        return int(self.radius * self.current_scale)
    
    def draw(self, surface, color):
        """Draw hover effect"""
        if self.is_hovering:
            # Draw expanding ring
            ring_radius = self.get_scaled_radius()
            for i in range(3):
                alpha = int(150 - i * 40)
                pygame.draw.circle(surface, (*color[:3], alpha), self.position,
                                 ring_radius + i * 3, width=2)


class ScoreCounter:
    """Animated score counter"""
    def __init__(self, position, initial_value=0):
        self.position = position
        self.current_value = initial_value
        self.display_value = float(initial_value)
        self.target_value = initial_value
    
    def set_value(self, value):
        """Set new target value"""
        self.target_value = value
    
    def update(self):
        """Update counter animation"""
        diff = self.target_value - self.display_value
        self.display_value += diff * 0.15
        if abs(diff) < 0.1:
            self.display_value = self.target_value
    
    def get_display_value(self):
        """Get current display value"""
        return int(round(self.display_value))


class ShakeEffect:
    """Enhanced screen shake"""
    def __init__(self, intensity=AnimationConfig.SHAKE_INTENSITY):
        self.intensity = intensity
        self.duration = AnimationConfig.SHAKE_DURATION
        self.progress = 0
        self.offset_x = 0
        self.offset_y = 0
    
    def update(self):
        """Update shake with decay"""
        if self.progress >= self.duration:
            self.offset_x = 0
            self.offset_y = 0
            return False
        
        current_intensity = self.intensity * (1 - self.progress / self.duration)
        angle = random.uniform(0, 2 * math.pi)
        self.offset_x = int(math.cos(angle) * current_intensity)
        self.offset_y = int(math.sin(angle) * current_intensity)
        
        self.progress += 1
        return True
    
    def get_offset(self):
        """Get current shake offset"""
        return (self.offset_x, self.offset_y)


class TransitionEffect:
    """Smooth fade transitions"""
    def __init__(self, screen_size, fade_in=True, duration=AnimationConfig.FADE_DURATION):
        self.screen_size = screen_size
        self.fade_in = fade_in
        self.duration = duration
        self.progress = 0
        self.active = True
    
    def update(self):
        """Update transition"""
        if not self.active:
            return False
        
        self.progress += 1
        if self.progress >= self.duration:
            self.active = False
            return False
        return True
    
    def draw(self, surface):
        """Draw transition overlay"""
        if not self.active:
            return
        
        t = self.progress / self.duration
        t = ease_in_out_cubic(t)
        
        if self.fade_in:
            alpha = int(255 * (1 - t))
        else:
            alpha = int(255 * t)
        
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))


class TurnIndicator:
    """Animated turn indicator"""
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.active = False
        self.message = ""
        self.color = Colors.TEXT_PRIMARY
        self.phase = 0
        self.show_duration = 60
        self.show_progress = 0
    
    def show(self, message, color=None):
        """Show turn indicator"""
        self.active = True
        self.message = message
        self.color = color if color else Colors.TEXT_PRIMARY
        self.show_progress = 0
        self.phase = 0
    
    def update(self):
        """Update animation"""
        if not self.active:
            return
        
        self.phase += 0.15
        self.show_progress += 1
        
        if self.show_progress >= self.show_duration:
            self.active = False
    
    def draw(self, surface, font):
        """Draw turn indicator"""
        if not self.active:
            return
        
        # Calculate alpha for fade in/out
        if self.show_progress < 15:
            alpha = int(255 * (self.show_progress / 15))
        elif self.show_progress > self.show_duration - 15:
            alpha = int(255 * ((self.show_duration - self.show_progress) / 15))
        else:
            alpha = 255
        
        # Pulsing scale
        scale = 1.0 + 0.1 * math.sin(self.phase)
        
        # Render text
        text_surf = font.render(self.message, True, self.color)
        original_size = text_surf.get_size()
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        scaled_surf = pygame.transform.scale(text_surf, new_size)
        
        # Apply alpha
        scaled_surf.set_alpha(alpha)
        
        # Position at top center
        rect = scaled_surf.get_rect(center=(self.screen_size[0] // 2, 100))
        
        # Draw glow
        for i in range(3):
            glow_surf = scaled_surf.copy()
            glow_surf.set_alpha(alpha // (i + 2))
            glow_rect = rect.move(i * 2, i * 2)
            surface.blit(glow_surf, glow_rect)
        
        # Draw main text
        surface.blit(scaled_surf, rect)


class AnimationManager:
    """Central animation manager"""
    def __init__(self, screen_size):
        self.particles = ParticleSystem()
        self.glows = []
        self.hover_effects = {}
        self.shake = None
        self.transition = None
        self.turn_indicator = TurnIndicator(screen_size)
        self.score_counters = {}
        self.screen_size = screen_size
    
    def add_glow(self, position, radius, color, intensity=1.0):
        """Add pulsing glow"""
        glow = PulseGlow(position, radius, color, intensity)
        self.glows.append(glow)
    
    def add_hover_effect(self, pit_id, position, radius):
        """Add hover effect for pit"""
        if pit_id not in self.hover_effects:
            self.hover_effects[pit_id] = HoverEffect(position, radius)
        return self.hover_effects[pit_id]
    
    def set_pit_hover(self, pit_id, hovering):
        """Set hover state for pit"""
        if pit_id in self.hover_effects:
            self.hover_effects[pit_id].set_hover(hovering)
    
    def emit_particles(self, x, y, count=20, explosion=False):
        """Emit particles"""
        self.particles.emit(x, y, count, explosion=explosion)
    
    def emit_fountain(self, x, y, count=15):
        """Emit fountain particles"""
        self.particles.emit_fountain(x, y, count)
    
    def trigger_shake(self, intensity=AnimationConfig.SHAKE_INTENSITY):
        """Trigger screen shake"""
        self.shake = ShakeEffect(intensity)
    
    def start_transition(self, fade_in=True):
        """Start screen transition"""
        self.transition = TransitionEffect(self.screen_size, fade_in)
    
    def show_turn_indicator(self, message, color=None):
        """Show turn indicator"""
        self.turn_indicator.show(message, color)
    
    def add_score_counter(self, key, position, initial_value=0):
        """Add score counter"""
        self.score_counters[key] = ScoreCounter(position, initial_value)
    
    def update_score(self, key, value):
        """Update score counter"""
        if key in self.score_counters:
            self.score_counters[key].set_value(value)
    
    def update(self):
        """Update all animations"""
        self.particles.update()
        
        for glow in self.glows:
            glow.update()
        
        for hover in self.hover_effects.values():
            hover.update()
        
        for counter in self.score_counters.values():
            counter.update()
        
        if self.shake:
            if not self.shake.update():
                self.shake = None
        
        if self.transition:
            self.transition.update()
        
        self.turn_indicator.update()
    
    def draw(self, surface):
        """Draw all animations"""
        self.particles.draw(surface)
        
        for glow in self.glows:
            glow.draw(surface)
        
        for hover in self.hover_effects.values():
            # Hover effects are drawn in the main draw loop
            pass
        
        if self.transition:
            self.transition.draw(surface)
    
    def draw_turn_indicator(self, surface, font):
        """Draw turn indicator"""
        self.turn_indicator.draw(surface, font)
    
    def get_shake_offset(self):
        """Get current shake offset"""
        if self.shake:
            return self.shake.get_offset()
        return (0, 0)
    
    def clear_glows(self):
        """Clear all glows"""
        self.glows.clear()
    
    def clear_all(self):
        """Clear all animations"""
        self.particles.clear()
        self.glows.clear()
        self.hover_effects.clear()
        self.shake = None
        self.transition = None

'''animations_enhanced.py ends here'''