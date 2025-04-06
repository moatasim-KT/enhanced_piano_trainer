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


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_x, mouse_y = event.pos
            if self.play_button_rect.collidepoint(mouse_x, mouse_y):
                if self.playing:
                    pass # Do nothing if already playing
                else:
                    self.start_playback()
            elif self.stop_button_rect.collidepoint(mouse_x, mouse_y):
                if self.playing:
                    self.stop_playback()
                else:
                    pass # Do nothing if already stopped

    def start_playback(self):
        if self.midi_data:
            self.playing = True
            self.playback_position = 0
            self.midi_loader.start_playback("media/midi/test_song.mid")
            print("Started MIDI Playback")

    def stop_playback(self):
        self.playing = False
        self.midi_loader.stop_playback()
        self.piano_view.reset_key_colors()  # Reset key colors when stopping
        print("Stopped MIDI Playback")

    def update(self, events):
        if self.playing and self.midi_data:
            ticks_per_update = 1  # Adjust for smoother or faster playback
            self.playback_position += ticks_per_update * self.playback_speed

            current_events = self.midi_loader.get_current_events(self.playback_position)
            if current_events:
                for event in current_events:
                    if event.type == "note_on":
                        self.piano_view.highlight_key(event.note, (0, 255, 0))  # Green highlight
                    elif event.type == "note_off":
                        self.piano_view.unhighlight_key(event.note)

            if self.playback_position >= self.midi_data["duration"]:
                self.stop_playback()

    def render(self):
        self.piano_view.draw() # Draw the piano

        # Draw "Play" button
        pygame.draw.rect(self.piano_view.screen, (0, 128, 255), self.play_button_rect)
        play_text = self.font.render("Play", True, (255, 255, 255))
        text_rect = play_text.get_rect(center=self.play_button_rect.center)
        self.piano_view.screen.blit(play_text, text_rect)

        # Draw "Stop" button
        pygame.draw.rect(self.piano_view.screen, (255, 0, 0), self.stop_button_rect)
        stop_text = self.font.render("Stop", True, (255, 255, 255))
        text_rect = stop_text.get_rect(center=self.stop_button_rect.center)
        self.piano_view.screen.blit(stop_text, text_rect)

        # Display playback position (for debugging)
        position_text = self.font.render(f"Position: {self.playback_position:.2f}", True, (255, 255, 255))
        self.piano_view.screen.blit(position_text, (10, 10))
