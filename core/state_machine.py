"""Assistant State Machine

Manages state transitions for the voice assistant.
States: LISTENING (wake word), WAITING_SELECTION (choosing from list), COMMAND_MODE (active listening)
"""

import time
from typing import Optional


class AssistantStateMachine:
    """Manages state transitions and command mode timeout for the voice assistant."""
    
    # State Constants
    STATE_LISTENING = 0          # Listening for wake word
    STATE_WAITING_SELECTION = 1  # Waiting for user to select from list
    STATE_COMMAND_MODE = 2       # Wake word detected, listening for commands
    
    COMMAND_TIMEOUT = 20  # seconds
    
    def __init__(self):
        """Initialize state machine in LISTENING mode."""
        self._state = self.STATE_LISTENING
        self._command_mode_start: Optional[float] = None
    
    @property
    def state(self) -> int:
        """Get current state."""
        return self._state
    
    def get_state(self) -> int:
        """Get current state (alternative getter)."""
        return self._state
    
    def transition_to(self, new_state: int) -> None:
        """
        Transition to a new state.
        
        Args:
            new_state: One of STATE_LISTENING, STATE_WAITING_SELECTION, STATE_COMMAND_MODE
        """
        if new_state not in [self.STATE_LISTENING, self.STATE_WAITING_SELECTION, self.STATE_COMMAND_MODE]:
            raise ValueError(f"Invalid state: {new_state}")
        
        # Special handling for command mode
        if new_state == self.STATE_COMMAND_MODE:
            self._command_mode_start = time.time()
        else:
            self._command_mode_start = None
        
        self._state = new_state
    
    def is_command_mode_expired(self) -> bool:
        """
        Check if command mode has timed out.
        
        Returns:
            True if in command mode and timeout exceeded
        """
        if self._state != self.STATE_COMMAND_MODE:
            return False
        
        if self._command_mode_start is None:
            return False
        
        elapsed = time.time() - self._command_mode_start
        return elapsed > self.COMMAND_TIMEOUT
    
    def reset_command_timer(self) -> None:
        """Reset the command mode timeout (when user speaks in command mode)."""
        if self._state == self.STATE_COMMAND_MODE:
            self._command_mode_start = time.time()
    
    def is_listening(self) -> bool:
        """Check if currently in LISTENING state."""
        return self._state == self.STATE_LISTENING
    
    def is_waiting_selection(self) -> bool:
        """Check if currently in WAITING_SELECTION state."""
        return self._state == self.STATE_WAITING_SELECTION
    
    def is_command_mode(self) -> bool:
        """Check if currently in COMMAND_MODE state."""
        return self._state == self.STATE_COMMAND_MODE
