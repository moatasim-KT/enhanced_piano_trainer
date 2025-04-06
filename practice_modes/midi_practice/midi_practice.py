import pygame
from practice_modes.regular_practice.regular_practice import RegularPracticeMode
import logging
class MIDIPracticeMode(RegularPracticeMode):
    def __init__(self, piano_view, sound_engine, midi_loader):
        super().__init__(piano_view, sound_engine)
        self.midi_loader = midi_loader
        self.playing = False
        self.midi_data = None  # To store loaded MIDI data (ticks, notes)
        self.playback_position = 0
        self.playback_speed = 1.0  # Add playback speed control
        self.font = pygame.font.Font(None, 36) # Initialize font
        self.play_button_rect = pygame.Rect(100, 500, 100, 50)
        self.stop_button_rect = pygame.Rect(250, 500, 100, 50)

        # Load a default MIDI file for now (replace with actual file loading)
        try:
            self.midi_data = self.midi_loader.load_midi("media/midi/test_song.mid")
        except Exception as e:
            print(f"Failed to load default MIDI file: {e}")
            self.midi_data = None

    def start(self):
        """Override the start method to initialize MIDI practice mode state."""
        print("Starting MIDI Practice Mode")
        super().start()  # This sets is_active to True
        self.playback_position = 0
        self.playing = False
        
    def stop(self):
        """Override the stop method to clean up MIDI practice mode state."""
        print("Stopping MIDI Practice Mode")
        self.playing = False
        super().stop()  # This sets is_active to False
        
    def load_midi(self, midi_file_path: str):
        """
        Load a MIDI file using the midi_loader.
        
        Args:
            midi_file_path: Path to the MIDI file.
        """
        self.midi_data = self.midi_loader.load_midi(midi_file_path)

    def handle_event(self, event):
        # Handle events specific to MIDI practice mode
        return

    def update(self, events):
        """Process events and update playback state."""
        if not self.is_active:
            print("WARNING: update called on inactive MIDI practice mode")
            return
            
        # Handle mouse clicks for buttons
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_button_rect.collidepoint(event.pos):
                    self.playing = True
                    print("MIDI Play button clicked")
                elif self.stop_button_rect.collidepoint(event.pos):
                    self.playing = False
                    print("MIDI Stop button clicked")
                    
        # Update playback position if playing
        if self.playing and self.midi_data:
            # Simple playback position update for demonstration
            # In a real implementation, this would advance based on time
            self.playback_position += 1

    def draw(self, surface: pygame.Surface):
        """Draw the MIDI practice mode UI."""
        if not self.is_active:
            print("WARNING: draw called on inactive MIDI practice mode")
            return
            
        print("MIDIPracticeMode.draw() called")
            
        # First call the parent class draw method to draw basic UI elements
        super().draw(surface)
        
        # Then add MIDI practice specific UI elements
        # We don't need to clear the surface again since parent already did

        # Draw Play button
        pygame.draw.rect(surface, (0, 255, 0), self.play_button_rect)
        play_text = self.font.render("Play", True, (0, 0, 0))
        play_text_rect = play_text.get_rect(center=self.play_button_rect.center)
        surface.blit(play_text, play_text_rect)

        # Draw Stop button
        pygame.draw.rect(surface, (255, 0, 0), self.stop_button_rect)
        stop_text = self.font.render("Stop", True, (0, 0, 0))
        stop_text_rect = stop_text.get_rect(center=self.stop_button_rect.center)
        surface.blit(stop_text, stop_text_rect)

        # Placeholder for MIDI data visualization
        # Add code here to visualize the MIDI data (e.g., piano roll)
