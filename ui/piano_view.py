import pygame
import pygame.midi
from typing import Dict, List, Tuple, Optional, Union, Set

class PianoKey:
    """Class representing a single piano key with its properties and state"""
    
    def __init__(self, 
                note_number: int, 
                is_white: bool, 
                position: Tuple[int, int], 
                size: Tuple[int, int]):
        self.note_number = note_number
        self.is_white = is_white
        self.position = position  # (x, y)
        self.size = size          # (width, height)
        self.is_pressed = False
        self.highlight_color = None
        self.label = ""
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if a point is within the key's bounds"""
        x, y = point
        kx, ky = self.position
        kw, kh = self.size
        return (kx <= x <= kx + kw) and (ky <= y <= ky + kh)
    
    def draw(self, surface: pygame.Surface, 
             colors: Dict[str, Tuple[int, int, int]],
             show_labels: bool = True,
             font: Optional[pygame.font.Font] = None) -> None:
        """Draw the key on the given surface"""
        # Determine the color based on the key state
        if self.highlight_color:
            color = self.highlight_color
        elif self.is_pressed:
            color = colors['pressed'] if self.is_white else colors['black_pressed']
        else:
            color = colors['white'] if self.is_white else colors['black']
        
        # Draw the key
        pygame.draw.rect(surface, color, (*self.position, *self.size))
        
        # Draw the border
        border_color = colors['border']
        pygame.draw.rect(surface, border_color, (*self.position, *self.size), 1)
        
        # Draw the label if requested
        if show_labels and self.label and font:
            label_surface = font.render(self.label, True, colors['text'])
            label_rect = label_surface.get_rect(
                center=(self.position[0] + self.size[0] // 2,
                        self.position[1] + self.size[1] - 15)
            )
            surface.blit(label_surface, label_rect)


class PianoView:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        
        # Set fixed note range for the piano (for example, A0 to C8)
        self.start_note = 21
        self.end_note = 108
        
        self._calculate_dimensions()

    def _calculate_dimensions(self):
        total_keys = self.end_note - self.start_note + 1

