# scripts/checkpoint.py
import pygame
from scripts.Constants import TRACK_CHECKPOINT_ZONES

class CheckpointManager:
    """
    Handles checkpoint crossing detection with proper tracking.
    """
    def __init__(self):
        self.zones = TRACK_CHECKPOINT_ZONES
        self.total_checkpoints = len(TRACK_CHECKPOINT_ZONES)

        self.reset()

    def reset(self):
        """Reset all checkpoint tracking"""
        self.current_idx = 0
        self.crossed_count = 0
        # Track how many times each checkpoint was crossed (for visualization)
        self.checkpoint_cross_counts = [0] * self.total_checkpoints
        self.prev_car_pos = None

    def check_crossing(self, car_pos):
        """
        Check if car crossed current checkpoint.
        Returns: (crossed_forward, backward_crossed)
        
        crossed_forward: True if crossed the NEXT checkpoint in sequence
        backward_crossed: True if crossed an ALREADY CLEARED checkpoint
        """
        if self.prev_car_pos is None:
            self.prev_car_pos = car_pos
            return False, False

        # Check if we're done with all checkpoints
        if self.current_idx >= self.total_checkpoints:
            self.prev_car_pos = car_pos
            return False, False

        # Check current checkpoint
        current_zone = self.zones[self.current_idx]
        p1, p2 = current_zone

        if self._line_segments_intersect(self.prev_car_pos, car_pos, p1, p2):
            # Crossed current checkpoint!
            self.checkpoint_cross_counts[self.current_idx] += 1
            self.crossed_count += 1
            self.current_idx += 1
            self.prev_car_pos = car_pos
            return True, False

        # Check backward crossings (any already-cleared checkpoint)
        for i in range(self.current_idx):
            zone = self.zones[i]
            p1, p2 = zone
            if self._line_segments_intersect(self.prev_car_pos, car_pos, p1, p2):
                # Crossed a previous checkpoint
                self.checkpoint_cross_counts[i] += 1
                print(f"⚠️  BACKWARD CROSS: Checkpoint {i+1} (x{self.checkpoint_cross_counts[i]})")
                self.prev_car_pos = car_pos
                return False, True

        self.prev_car_pos = car_pos
        return False, False

    def _line_segments_intersect(self, p1, p2, p3, p4):
        """Check if line segment p1-p2 intersects with line segment p3-p4"""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return False
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        return 0 <= t <= 1 and 0 <= u <= 1

    def draw(self, surface):
        """Draw checkpoint zones with center dots and cross counts"""
        font = pygame.font.Font(None, 18)
        
        for i, (p1, p2) in enumerate(self.zones):
            cross_count = self.checkpoint_cross_counts[i]
            
            # Calculate the center of the checkpoint line
            cx = (p1[0] + p2[0]) / 2
            cy = (p1[1] + p2[1]) / 2
            
            # Determine color based on state and cross count
            if i == self.current_idx:
                color = (0, 255, 0)  # Bright green for current
                width = 4
            elif i < self.current_idx:
                # Completed checkpoints
                if cross_count > 1:
                    color = (255, 0, 0)  # Red for backward crossing
                    width = 3
                else:
                    color = (100, 100, 100)  # Gray for completed
                    width = 2
            else:
                color = (0, 100, 0)  # Dark green for upcoming
                width = 2
            
            # Draw the line segment for the checkpoint
            pygame.draw.line(surface, color, p1, p2, width)
            
            # Draw a small dot at the center for reference
            pygame.draw.circle(surface, color, (int(cx), int(cy)), 4)
            
            # Draw cross count if > 0
            if cross_count > 0:
                count_text = font.render(f"x{cross_count}", True, (255, 255, 255))
                # Add black background for readability
                text_bg = pygame.Surface((count_text.get_width() + 4, count_text.get_height() + 2))
                text_bg.set_alpha(180)
                text_bg.fill((0, 0, 0))
                surface.blit(text_bg, (int(cx) + 10, int(cy) - 10))
                surface.blit(count_text, (int(cx) + 12, int(cy) - 9))