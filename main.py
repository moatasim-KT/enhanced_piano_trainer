#!/usr/bin/env python3
import sys
import os
import pygame
import argparse
from pygame.locals import *

# Import custom modules
from ui.piano_view import PianoView
from audio.sound_engine import SoundEngine
from practice_modes.regular_practice.regular_practice import RegularPracticeMode
from practice_modes.midi_practice.midi_practice import MIDIPracticeMode
from midi_processing.midi_loader import MidiLoader

class EnhancedPianoTrainer:
    def __init__(self):
        """Initialize the Enhanced Piano Trainer application."""
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Enhanced Piano Trainer")
        
        # Initialize screen
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Initialize clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initialize components
        self.sound_engine = SoundEngine(os.path.join("media", "samples"))
        self.piano_view = PianoView(self.screen, self.screen_width, self.screen_height)
        self.midi_loader = MidiLoader(os.path.join("media", "midi"))
        
        # Initialize practice modes
        # Use a proper subclass of RegularPracticeMode instead of the base class
        from practice_modes.regular_practice.regular_practice import NoteIdentificationPractice, ScalePractice
        # Create instances of specific practice modes rather than the base class
        self.regular_practice = NoteIdentificationPractice(self.piano_view, self.sound_engine)
        self.scale_practice = ScalePractice(self.piano_view, self.sound_engine)
        self.midi_practice = MIDIPracticeMode(self.piano_view, self.sound_engine, self.midi_loader)
        
        # Track mode states
        self.initialized_modes = set()
        
        # Set default active mode
        self.active_mode = self.regular_practice
        
        # Menu state
        self.in_menu = True
        self.menu_options = [
            "Note Practice", 
            "Scale Practice",
            "MIDI Practice", 
            "Settings", 
            "Exit"
        ]
        self.selected_option = 0
        
        # Font for UI
        self.font = pygame.font.SysFont("Arial", 30)
        self.title_font = pygame.font.SysFont("Arial", 50, bold=True)
        
        # Color definitions
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
        self.LIGHT_BLUE = (100, 100, 255)
        self.GRAY = (150, 150, 150)
        
        # Application state
        self.running = True
        self.cache_menu_options()

    def cache_menu_options(self):
        """Cache rendered menu options for faster drawing."""
        self.cached_menu_options = []
        for i, option in enumerate(self.menu_options):
            text = self.font.render(option, True, self.WHITE)
            text_rect = text.get_rect(center=(self.screen_width // 2, 250 + i * 60))
            self.cached_menu_options.append((text, text_rect))

    def handle_events(self, events):
        """
        Handle pygame events and update the application state accordingly.
        This method processes a list of pygame events and performs actions based on the type of each event:
        - QUIT: Sets the running flag to False to stop the application.
        - KEYDOWN:
            - K_ESCAPE: If in the menu, sets running to False (exiting the application); otherwise, toggles the menu state.
            - When in the menu:
                - K_UP: Moves the selection up by decrementing the selected option index.
                - K_DOWN: Moves the selection down by incrementing the selected option index.
                - K_RETURN: Forces a synchronous update of the display before executing the selected menu option.
        - MOUSEBUTTONDOWN:
            - When in the menu, checks if the mouse click falls within an expanded area around any menu option.
              If a clickable menu option is detected, updates the selected option, redraws the menu, forces a display update,
              and executes the corresponding menu option.
        Parameters:
            events (list): A list of pygame events to be handled.
        """
        """Handle pygame events."""
        for event in events:
            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.in_menu:
                        self.running = False
                    else:
                        self.in_menu = True
                # Menu navigation
                if self.in_menu:
                    if event.key == K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == K_RETURN:
                        print(f"RETURN key pressed, executing menu option: {self.selected_option}")
                        # Force synchronous update before executing menu option
                        pygame.display.flip()
                        self.execute_menu_option(self.selected_option)
            
            elif event.type == MOUSEBUTTONDOWN:
                if self.in_menu:
                    mouse_x, mouse_y = event.pos
                    print(f"Mouse clicked at position: ({mouse_x}, {mouse_y})")
                    for i, (_, text_rect) in enumerate(self.cached_menu_options):
                        # Expand the clickable area slightly
                        expanded_rect = pygame.Rect(
                            text_rect.left - 10, 
                            text_rect.top - 5, 
                            text_rect.width + 20, 
                            text_rect.height + 10
                        )
                        if expanded_rect.collidepoint(mouse_x, mouse_y):
                            print(f"Menu option {i} ({self.menu_options[i]}) clicked")
                            # Set the selected option to provide visual feedback
                            self.selected_option = i
                            
                            # Draw the menu with updated selection before executing
                            self.draw_menu()
                            pygame.display.flip()
                            
                            # Execute the selected option
                            self.execute_menu_option(i)
                            break

    def stop_current_mode(self):
        """Stop and cleanup the current mode if it exists."""
        if self.active_mode is not None:
            print(f"Stopping current mode: {self.active_mode.__class__.__name__}")
            if hasattr(self.active_mode, 'stop'):
                try:
                    self.active_mode.stop()
                except Exception as e:
                    print(f"Error stopping {self.active_mode.__class__.__name__}: {e}")
            else:
                print("WARNING: active_mode has no stop method!")
            if hasattr(self, 'initialized_modes') and self.active_mode in self.initialized_modes:
                self.initialized_modes.remove(self.active_mode)

    def select_mode(self, option):
        """Return the new mode instance and its name based on the option."""
        if option == 0:
            print("Setting up Note Practice mode")
            return self.regular_practice, "Note Practice"
        elif option == 1:
            print("Setting up Scale Practice mode")
            return self.scale_practice, "Scale Practice"
        elif option == 2:
            print("Setting up MIDI Practice mode")
            return self.midi_practice, "MIDI Practice"
        else:
            raise ValueError("Invalid practice mode option")

    def activate_mode(self, new_mode, mode_name):
        """Activate the given mode by starting it and verifying activation."""
        # Stop previous instance if needed (done already in stop_current_mode)
        if hasattr(new_mode, 'is_active') and new_mode.is_active:
            print(f"WARNING: {mode_name} mode was already active. Restarting...")
            if hasattr(new_mode, 'stop'):
                new_mode.stop()

        if not hasattr(new_mode, 'start'):
            raise AttributeError(f"{mode_name} mode has no start method")

        print(f"Activating {mode_name} mode")
        new_mode.start()
        if hasattr(new_mode, 'is_active'):
            if not new_mode.is_active:
                print(f"WARNING: {mode_name} mode did not activate. Forcing active state.")
                new_mode.is_active = True
            else:
                print(f"{mode_name} mode successfully activated")
        else:
            print(f"WARNING: {mode_name} mode has no is_active attribute")

        # Track that this mode is initialized
        if hasattr(self, 'initialized_modes'):
            self.initialized_modes.add(new_mode)
        return new_mode

    def execute_menu_option(self, option):
        """Execute the selected menu option."""
        print(f"Executing menu option: {option} - {self.menu_options[option]}")
        previous_mode = self.active_mode
        was_in_menu = self.in_menu

        # Handle simple options
        if option == 4:  # Exit
            print("Exit selected - closing application")
            self.running = False
            return
        if option == 3:  # Settings
            print("Settings selected - displaying settings (not implemented)")
            return

        try:
            self._extracted_from_execute_menu_option_18(option)
        except Exception as e:
            import traceback
            print(f"ERROR executing menu option {option}: {e}")
            traceback.print_exc()
            # Restore previous state on failure
            self.active_mode = previous_mode
            self.in_menu = was_in_menu

    # TODO Rename this here and in `execute_menu_option`
    def _extracted_from_execute_menu_option_18(self, option):
        # Stop current practice mode if any
        self.stop_current_mode()

        # Select new mode based on option
        new_mode, mode_name = self.select_mode(option)
        # Activate new mode
        self.active_mode = self.activate_mode(new_mode, mode_name)
        # Switch out of menu now that new mode is active
        self.in_menu = False
        print(f"Successfully switched to {mode_name} mode")

        # Force a test draw to validate mode functionality
        pygame.time.delay(100)  # Give a small delay for state update
        self._test_draw_mode()

        pygame.display.flip()

    def _test_draw_mode(self):
        """Perform a test draw of the active mode to ensure it's working."""
        if not hasattr(self.active_mode, 'draw'):
            raise AttributeError(f"{self.active_mode.__class__.__name__} has no draw method")
        # Clear screen before test draw
        self.screen.fill(self.BLACK)
        self.active_mode.draw(self.screen)
        pygame.display.flip()
        print("Test draw successful")
    
    def draw_menu(self):
        """Draw the main menu."""
        self.screen.fill(self.BLACK)
        
        # Draw title
        title = self.title_font.render("Enhanced Piano Trainer", True, self.WHITE)
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw menu options
        for i, (text, text_rect) in enumerate(self.cached_menu_options):
            color = self.LIGHT_BLUE if i == self.selected_option else self.WHITE
            colored_text = self.font.render(self.menu_options[i], True, color)
            self.screen.blit(colored_text, text_rect)
            
            # Draw rectangle around the option for better click visibility
            # Expand the clickable area slightly
            expanded_rect = pygame.Rect(
                text_rect.left - 10, 
                text_rect.top - 5, 
                text_rect.width + 20, 
                text_rect.height + 10
            )
            pygame.draw.rect(self.screen, color, expanded_rect, 2)  # 2 is the border width
        # Draw instructions
        instructions = self.font.render("Use UP/DOWN arrows to navigate, ENTER to select, or CLICK on option", True, self.GRAY)
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        self.screen.blit(instructions, instructions_rect)
        
        pygame.display.flip()

    def has_menu_changed(self):
        """Checks if the selected menu option has changed."""
        if not hasattr(self, 'previous_selected_option'):
            self.previous_selected_option = self.selected_option
            return False
        changed = self.previous_selected_option != self.selected_option
        self.previous_selected_option = self.selected_option
        return changed
    def draw_full_screen(self):
        """Force a full screen redraw regardless of mode."""
        self.screen.fill(self.BLACK)  # Clear screen
        print(f"Drawing full screen, in_menu={self.in_menu}")

        # Draw appropriate content
        if self.in_menu:
            print("Drawing menu screen")
            self.draw_menu()
        elif hasattr(self, 'active_mode') and self.active_mode is not None:
            try:
                mode_name = self.active_mode.__class__.__name__
                print(f"Drawing {mode_name} screen")

                # Verify mode is active before drawing
                if hasattr(self.active_mode, 'is_active') and not self.active_mode.is_active:
                    print(f"WARNING: {mode_name} not active during full screen draw")
                    if hasattr(self.active_mode, 'start'):
                        try:
                            print(f"Activating {mode_name}")
                            self.active_mode.start()
                        except Exception as start_error:
                            print(f"Error activating {mode_name}: {start_error}")
                            # Last resort - force active state
                            self.active_mode.is_active = True
                    else:
                        print(f"{mode_name} has no start method, forcing active state")
                        self.active_mode.is_active = True

                if hasattr(self.active_mode, 'draw'):
                    self.active_mode.draw(self.screen)
                    print(f"Successfully drew {mode_name} screen")
                else:
                    print(f"WARNING: {mode_name} has no draw method, falling back to menu")
                    self.in_menu = True
                    self.draw_menu()
            except Exception as e:
                self._extracted_from_draw_full_screen_38(e)
        else:
            print("WARNING: No active mode to draw, falling back to menu")
            self.in_menu = True
            self.draw_menu()

        # Add visible marker for debug purposes
        debug_text = self.font.render("ESC: Menu", True, (150, 150, 150))
        self.screen.blit(debug_text, (10, self.screen_height - 30))
        pygame.display.flip()  # Make sure to update the display

    # TODO Rename this here and in `draw_full_screen`
    def _extracted_from_draw_full_screen_38(self, e):
        mode_name = self.active_mode.__class__.__name__ if hasattr(self, 'active_mode') else "Unknown"
        print(f"ERROR drawing {mode_name} screen: {str(e)}")
        import traceback
        traceback.print_exc()
        self.in_menu = True
        self.draw_menu()
    def initialize_modes(self):
        """Initialize practice modes with required setup."""
        print("Initializing practice modes")

        # Verify all required methods exist
        for mode_name, mode in [("Regular Practice", self.regular_practice), 
                               ("MIDI Practice", self.midi_practice)]:
            # Check for essential methods
            missing_methods = []
            missing_methods.extend(
                method
                for method in ['start', 'stop', 'update', 'draw']
                if not hasattr(mode, method)
            )
            if missing_methods:
                print(f"WARNING: {mode_name} is missing methods: {', '.join(missing_methods)}")
            else:
                print(f"{mode_name} has all required methods")

        # Initialize active mode tracking
        self.initialized_modes = set()
    def handle_mode_error(self, error, error_type="general", mode_name=None):
        """Centralized error handling for mode errors."""
        if not mode_name and hasattr(self, 'active_mode') and self.active_mode:
            mode_name = self.active_mode.__class__.__name__
        else:
            mode_name = mode_name or "Unknown"
            
        print(f"ERROR {error_type} in {mode_name}: {str(error)}")
        import traceback
        traceback.print_exc()
        
        # Try to stop the broken mode before returning to menu
        if hasattr(self, 'active_mode') and self.active_mode is not None:
            try:
                if hasattr(self.active_mode, 'stop'):
                    print(f"Stopping {mode_name} due to {error_type} failure")
                    self.active_mode.stop()
            except Exception as stop_error:
                print(f"Error stopping mode after {error_type} failure: {stop_error}")
                
        # Return to menu
        self.in_menu = True
        self.draw_full_screen()  # Use full screen redraw to ensure proper state
        pygame.time.delay(100)  # Small delay to ensure state is updated properly
        return True  # Return True to indicate error was handled

    def run(self):
        """Main application loop."""
        # Initialize modes
        self.initialize_modes()
        print("Enhanced Piano Trainer started")
        
        # Initial screen setup
        self.draw_full_screen()
        while self.running:
            events = pygame.event.get()
            
            # Store state before event handling
            was_in_menu = self.in_menu
            
            # Handle events first
            try:
                self.handle_events(events)
            except Exception as e:
                print(f"ERROR in event handling: {e}")
                import traceback
                traceback.print_exc()
                # Stay in current state on event error, but ensure screen is redrawn
                self.draw_full_screen()
            # Process state change if menu state has changed
            if was_in_menu != self.in_menu:
                print(f"Menu state changed: {was_in_menu} -> {self.in_menu}")
                # Special handling for mode transitions
                if not self.in_menu and hasattr(self, 'active_mode') and self.active_mode:
                    # Get mode name for better error messages
                    mode_name = self.active_mode.__class__.__name__
                    
                    # Verify mode is active after transition
                    if hasattr(self.active_mode, 'is_active') and not self.active_mode.is_active:
                        print(f"Ensuring {mode_name} is active after menu transition")
                        try:
                            if hasattr(self.active_mode, 'start'):
                                self.active_mode.start()
                                print(f"Successfully activated {mode_name} after transition")
                            else:
                                print(f"ERROR: {mode_name} has no start method")
                                self.in_menu = True
                        except Exception as e:
                                   self.draw_full_screen()  # Ensure proper state after failure
            
            # Draw the appropriate screen based on menu state
            if self.in_menu:
                self.draw_menu()
            else:
                try:
                    # Verify the active mode exists and is active
                    if not hasattr(self, 'active_mode') or self.active_mode is None:
                        print("ERROR: No active mode set, returning to menu")
                        self.in_menu = True
                        self.draw_full_screen()
                        continue
                    # Log current mode for debugging
                    mode_name = self.active_mode.__class__.__name__
                    print(f"Active mode: {mode_name}")
                    
                    # Check if mode is properly initialized
                    if hasattr(self.active_mode, 'is_active'):
                        if not self.active_mode.is_active:
                            print(f"WARNING: {mode_name} is not active, restarting it")
                            try:
                                if hasattr(self.active_mode, 'start'):
                                    self.active_mode.start()
                                    print(f"Restarted {mode_name}")
                                else:
                                    print(f"ERROR: {mode_name} has no start method")
                                    self.in_menu = True
                                    self.draw_full_screen()  # Use full screen redraw to ensure proper state
                                    continue
                            except Exception as e:
                                print(f"ERROR restarting {mode_name}: {e}")
                                self.in_menu = True
                                self.draw_full_screen()  # Use full screen redraw to ensure proper state
                                continue
                    else:
                        print(f"WARNING: {mode_name} has no is_active attribute")
                    
                    # Verify consistent menu state
                    if self.in_menu:
                        print("CRITICAL: We're in practice mode but in_menu is True! Returning to menu...")
                        self.draw_full_screen()  # Force menu redraw
                        continue
                    
                    # Verify the mode is properly initialized
                    if hasattr(self.active_mode, 'is_active') and not self.active_mode.is_active:
                        print(f"WARNING: {mode_name} reports not active but we're in practice mode")
                        # Try to activate the mode once more
                        if hasattr(self.active_mode, 'start'):
                            try:
                                print(f"Attempting to restart {mode_name}")
                                self.active_mode.start()
                                print(f"Successfully restarted {mode_name}")
                            except Exception as e:
                                print(f"Failed to restart {mode_name}: {e}")
                                # Force active as last resort, then continue
                                self.active_mode.is_active = True
                                print(f"Forced {mode_name} to active state as recovery measure")
                        else:
                            # No start method, just force active
                            self.active_mode.is_active = True
                            print(f"Forced {mode_name} active (no start method available)")
                    # Update and draw the active mode
                    mode_name = self.active_mode.__class__.__name__
                    
                    # Update mode
                    if hasattr(self.active_mode, 'update'):
                        try:
                            self.active_mode.update(events)
                        except Exception as e:
                            if self.handle_mode_error(e, "updating", mode_name):
                                continue
                    else:
                        print(f"WARNING: {mode_name} has no update method!")
                        
                    # Draw mode
                    if hasattr(self.active_mode, 'draw'):
                        print(f"Drawing {mode_name} - starting draw call")
                        try:
                            # Clear the screen before drawing
                            self.screen.fill(self.BLACK)
                            
                            # Check if is_active flag is set before drawing
                            # We already validated active state, but check one more time
                            # in case something deactivated it during update
                            if hasattr(self.active_mode, 'is_active') and not self.active_mode.is_active:
                                print(f"WARNING: {mode_name} became inactive between update and draw")
                                # Just force it active for this frame to avoid errors
                                self.active_mode.is_active = True
                                
                            # Now draw the mode
                            self.active_mode.draw(self.screen)
                            # Add ESC hint consistently across all screens
                            hint = self.font.render("Press ESC to return to menu", True, self.GRAY)
                            self.screen.blit(hint, (20, self.screen_height - 30))
                            pygame.display.flip()  # Ensure screen updates are shown
                            print(f"Successfully drew {mode_name}")
                        except Exception as e:
                            if self.handle_mode_error(e, "drawing", mode_name):
                                continue
                    else:
                        print(f"WARNING: {mode_name} has no draw method!")
                        # Check if this mode has any way to interact with the user
                        if not hasattr(self.active_mode, 'update'):
                            print(f"CRITICAL: {mode_name} has neither draw nor update methods, returning to menu")
                            self.in_menu = True
                            self.draw_full_screen()  # Use full screen redraw to ensure proper state
                            continue
                        else:
                            # Mode has update but no draw, try to continue anyway
                            print(f"Continuing with {mode_name} despite no draw method (has update method)")
                            # Add some minimal feedback to show the mode is active
                            self.screen.fill(self.BLACK)  # Clear screen first
                            mode_info = self.font.render(f"Active: {mode_name}", True, self.WHITE)
                            self.screen.blit(mode_info, (20, 20))
                            # Add ESC hint
                            hint = self.font.render("Press ESC to return to menu", True, self.GRAY)
                            self.screen.blit(hint, (20, 60))
                            pygame.display.flip()
                except Exception as e:
                    self.handle_mode_error(e, "critical")
        # Cleanup
        pygame.quit()
        sys.exit()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Enhanced Piano Trainer")
    parser.add_argument("--midi", type=str, help="Path to MIDI file to load on startup")
    parser.add_argument("--mode", type=str, choices=["regular", "midi"], 
                        default="regular", help="Practice mode to start with")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    app = EnhancedPianoTrainer()
    
    # Handle command line arguments
    if args.midi:
        app.midi_practice.load_midi(args.midi)
        app.active_mode = app.midi_practice
        app.in_menu = False
    
    if args.mode == "midi" and not args.midi:
        app.active_mode = app.midi_practice
        app.in_menu = False
    
    # Run the application
    app.run()
