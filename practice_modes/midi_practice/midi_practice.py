import pygame
from practice_modes.regular_practice.regular_practice import RegularPracticeMode

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
        self.midi_data = self.midi_loader.load_midi("media/midi/test_song.mid")

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
        # Process events if needed; else ignore them.
        return

    def draw(self, surface: pygame.Surface):
        print("MIDIPracticeMode.draw() called")  # Added print statement
        # Render MIDI practice mode UI
        surface.fill((0, 0, 0))  # Clear the surface

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
