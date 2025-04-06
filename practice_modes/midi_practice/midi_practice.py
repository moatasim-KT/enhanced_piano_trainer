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
        self.play_button_rect = pygame.Rect(100, 550, 100, 50)
        self.stop_button_rect = pygame.Rect(250, 550, 100, 50)
        self.last_update_time = 0  # Initialize last update time
        self.note_rects = [] # Store note rectangles for highlighting

        # Load a default MIDI file for now (replace with actual file loading)
        try:
            self.midi_data = self.midi_loader.load_midi("media/midi/test_song.mid")
            if self.midi_data:
                self.midi_data["tempo"] = 120  # Add a default tempo if not present
                if self.midi_data["notes"]:
                    self.midi_data["total_ticks"] = max(note["start"] + note["duration"] for note in self.midi_data["notes"])
                else:
                    self.midi_data["total_ticks"] = 0  # Default value for empty notes
        except Exception as e:
            print(f"Failed to load default MIDI file: {e}")
            self.midi_data = None

    def start(self):
        """Override the start method to initialize MIDI practice mode state."""
        print("Starting MIDI Practice Mode")
        super().start()  # This sets is_active to True
        self.playback_position = 0
        self.playing = False
        self.last_update_time = pygame.time.get_ticks()
        self.note_rects = []
        
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
        if self.midi_data:
            self.midi_data["tempo"] = 120  # Add a default tempo if not present
            self.midi_data["total_ticks"] = max(note["start"] + note["duration"] for note in self.midi_data["notes"])

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
                    if self.playback_position >= self.midi_data["total_ticks"]:
                        self.playback_position = 0
                elif self.stop_button_rect.collidepoint(event.pos):
                    self.playing = False
                    print("MIDI Stop button clicked")
                    
        # Update playback position if playing
        if self.playing and self.midi_data:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.last_update_time
            self.last_update_time = current_time
            
            # Calculate the number of ticks to advance based on playback speed
            ticks_per_second = self.midi_data["ticks_per_beat"] * (self.midi_data["tempo"] / 60)
            ticks_to_advance = int(ticks_per_second * (elapsed_time / 1000) * self.playback_speed)
            
            self.playback_position += ticks_to_advance
            
            # Basic loop
            if self.playback_position >= self.midi_data["total_ticks"]:
                self.playback_position = self.midi_data["total_ticks"]
                self.playing = False # Stop at the end

            # --- Note playback logic (needs improvement) ---
            # This is a placeholder and needs a more sophisticated approach
            # to trigger note events at the correct times.
            # For now, it simply plays notes whose start times are within a
            # small window around the current playback position.
            
            # This logic is removed, as note playing will be handled by highlighting
            # keys during the draw phase

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

        # MIDI data visualization (Piano Roll)
        if self.midi_data:
            ticks_per_beat = self.midi_data["ticks_per_beat"]
            notes = self.midi_data["notes"]
            total_ticks = self.midi_data["total_ticks"]
            
            # Calculate scaling factors
            time_scale = 0.02  # Adjust as needed
            pitch_scale = 5  # Adjust as needed
            
            # Define drawing area for the piano roll
            roll_x = 50
            roll_y = 100
            roll_width = 1100
            roll_height = 400
            
            # Draw a background for the piano roll
            pygame.draw.rect(surface, (30, 30, 30), (roll_x, roll_y, roll_width, roll_height))
            
            # Draw a line indicating the current playback position
            playhead_x = roll_x + int(self.playback_position * time_scale)
            pygame.draw.line(surface, (255, 255, 255), (playhead_x, roll_y), (playhead_x, roll_y + roll_height), 2)

            # Iterate through notes and draw them
            self.note_rects = []  # Clear previous rectangles
            for note in notes:
                start_time = note["start"]
                duration = note["duration"]
                pitch = note["note"]
                velocity = note["velocity"]
                
                # Calculate position and size of the note rectangle
                x = roll_x + int(start_time * time_scale)
                y = roll_y + roll_height - int((pitch - 21) * pitch_scale)  # Assuming MIDI notes start at 21 (A0)
                width = int(duration * time_scale)
                height = int(pitch_scale)
                
                # Ensure the note is within the drawing area
                if x < roll_x:
                    x = roll_x
                if x + width > roll_x + roll_width:
                    width = roll_x + roll_width - x
                if y < roll_y:
                    y = roll_y
                if y > roll_y + roll_height:
                    continue  # Skip notes outside the drawing area
                    
                # Choose color based on velocity and if it's currently playing
                is_playing = start_time <= self.playback_position < start_time + duration
                if is_playing:
                    color = (0, 255, 0)  # Green if playing
                    self.piano_view.highlight_key(pitch, (0, 255, 0))
                else:
                    color = (min(255, velocity * 2), 0, 0)  # Red color, brighter with higher velocity

                # Draw the note rectangle
                rect = pygame.Rect(x, y, width, height)
                pygame.draw.rect(surface, color, rect)
                self.note_rects.append(rect)
        else:
            text = self.font.render("No MIDI data loaded.", True, (255, 255, 255))
            surface.blit(text, (roll_x, roll_y + roll_height // 2))
        self.piano_view.draw(surface, self.piano_view.colors)
