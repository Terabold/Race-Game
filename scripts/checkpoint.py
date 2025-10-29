import math
import pygame
from scripts.Constants import BRIGHT_GREEN, DARK_GREEN, GRAY_COLOR

class CheckpointManager:
    """Manages checkpoint zone crossing detection and progression tracking"""
    
    def __init__(self, checkpoint_zones):
        """Initialize checkpoint manager with list of zones"""
        self.zones = checkpoint_zones
        self.current_checkpoint_idx = 0
        self.checkpoints_crossed = 0
        self.total_checkpoints = len(checkpoint_zones)
        
    def reset(self):
        """Reset checkpoint progress"""
        self.current_checkpoint_idx = 0
        self.checkpoints_crossed = 0
        
    def check_crossing(self, prev_pos, current_pos):
        """
        Check if car crossed any checkpoint zone.
        Args:
            prev_pos: Previous position (x,y)
            current_pos: Current position (x,y)
        Returns:
            crossed (bool): True if crossed current checkpoint
            progress (float): How far along the track (0.0–1.0)
            backward_crossed (bool): True if crossed an already cleared checkpoint
        """
        backward_crossed = False

        # Check backward crossings first
        for i in range(self.current_checkpoint_idx):
            zone = self.zones[i]
            p1, p2 = zone
            if self._line_segments_intersect(prev_pos, current_pos, p1, p2):
                backward_crossed = True
                break

        # Check normal checkpoint progression
        if self.current_checkpoint_idx >= self.total_checkpoints:
            return False, 1.0, backward_crossed

        zone = self.zones[self.current_checkpoint_idx]
        p1, p2 = zone

        if self._line_segments_intersect(prev_pos, current_pos, p1, p2):
            self.current_checkpoint_idx += 1
            self.checkpoints_crossed += 1
            progress = self.checkpoints_crossed / self.total_checkpoints
            return True, progress, backward_crossed

        return False, self.checkpoints_crossed / self.total_checkpoints, backward_crossed

    def _line_segments_intersect(self, p1, p2, p3, p4):
        """
        Check if line segment p1-p2 intersects with line segment p3-p4
        using 2D line intersection math
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return False  # Lines are parallel
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        return 0 <= t <= 1 and 0 <= u <= 1
    
    def get_distance_to_checkpoint(self, position):
        """
        Get distance from car to current checkpoint zone.
        Returns closest distance to the line segment.
        """
        if self.current_checkpoint_idx >= self.total_checkpoints:
            return 0  # All done
        
        zone = self.zones[self.current_checkpoint_idx]
        p1, p2 = zone[0], zone[1]
        
        return self._point_to_line_distance(position, p1, p2)
    
    def _point_to_line_distance(self, point, line_start, line_end):
        """Calculate shortest distance from point to line segment"""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Vector from line start to end
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            # Line is just a point
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Parameter t for projection onto line
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        # Closest point on line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
    
    def get_checkpoint_center(self):
        """Get center point of current checkpoint (for visualization)"""
        if self.current_checkpoint_idx >= self.total_checkpoints:
            return None
        
        zone = self.zones[self.current_checkpoint_idx]
        p1, p2 = zone[0], zone[1]
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    def draw_zones(self, surface):
        """Draw checkpoint zones for visualization"""
        for idx, zone in enumerate(self.zones):
            p1, p2 = zone[0], zone[1]
            
            if idx == self.current_checkpoint_idx:
                color = BRIGHT_GREEN
                width = 4
            elif idx < self.current_checkpoint_idx:
                color = GRAY_COLOR
                width = 2
            else:
                color = DARK_GREEN
                width = 2
            
            # Draw line
            pygame.draw.line(surface, color, p1, p2, width)
            
            # Draw endpoints
            pygame.draw.circle(surface, color, p1, 5)
            pygame.draw.circle(surface, color, p2, 5)
            
            # Draw checkpoint number
            if idx <= self.current_checkpoint_idx + 2:
                center_x = (p1[0] + p2[0]) // 2
                center_y = (p1[1] + p2[1]) // 2
                font = pygame.font.Font(None, 20)
                text = font.render(str(idx + 1), True, (255, 255, 255))
                surface.blit(text, (center_x - 6, center_y - 10))