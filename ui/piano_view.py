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
        white_keys = [n for n in range(self.start_note, self.end_note + 1) if self._is_white_key(n)]
        num_white_keys = len(white_keys)
        white_key_width = self.width // num_white_keys
        black_key_width = int(white_key_width * 0.6)
        black_key_height = int(self.height * 0.6)

        self.keys = []
        white_key_x = 0
        for note in range(self.start_note, self.end_note + 1):
            if self._is_white_key(note):
                key = PianoKey(note, True, (white_key_x, 0), (white_key_width, self.height))
                self.keys.append(key)
                white_key_x += white_key_width
            else:
                previous_white_key_x = next(
                    (
                        self.keys[i].position[0]
                        for i in range(len(self.keys) - 1, -1, -1)
                        if self.keys[i].is_white
                    ),
                    None,
                )
                if previous_white_key_x is not None:
                    key = PianoKey(note, False, (previous_white_key_x + white_key_width - black_key_width // 2, 0), (black_key_width, black_key_height))
                    self.keys.append(key)
                else:
                    # Handle the case where no white key has been added yet
                    # For now, we skip adding the black key
                    print(f"Skipping black key for note {note} as no white key has been added yet.")
    def _is_white_key(self, note_number: int) -> bool:
        """Helper function to determine if a note is a white key"""
        # A simple way to identify white keys based on MIDI note number.  
        # This will need to be adjusted for different keyboard layouts or note ranges.
        return (note_number % 12) in [0, 2, 4, 5, 7, 9, 11]

    def highlight_key(self, note_number: int, color: Tuple[int, int, int]):
        for key in self.keys:
            if key.note_number == note_number:
                key.highlight_color = color
                break

    def unhighlight_key(self, note_number: int):
        for key in self.keys:
            if key.note_number == note_number:
                key.highlight_color = None
                break

    def reset_key_colors(self):
        for key in self.keys:
            key.highlight_color = None
