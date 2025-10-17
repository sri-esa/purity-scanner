# src/hardware/stage_controller.py
import time
import logging
from typing import Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StageConfig:
    """Configuration for stage controller"""
    x_max_mm: float = 50.0
    y_max_mm: float = 50.0
    home_pos: Tuple[float, float] = (0.0, 0.0)
    max_speed_mm_s: float = 10.0
    acceleration_mm_s2: float = 50.0

class StageController:
    """
    Minimal hardware abstraction for an X-Y motorized stage.
    Replace move_rel/move_abs method internals with your physical stage commands.
    
    This is a mock implementation - replace with actual hardware interface:
    - Serial communication (pyserial)
    - USB/Ethernet motion controllers
    - Vendor-specific SDKs (Thorlabs, Newport, etc.)
    """

    def __init__(self, config: Optional[StageConfig] = None):
        self.config = config or StageConfig()
        self.x = self.config.home_pos[0]
        self.y = self.config.home_pos[1]
        self.is_homed = False
        self.is_connected = False
        self.emergency_stop = False

    def connect(self, port: Optional[str] = None):
        """
        Open connection to stage hardware
        
        Args:
            port: Serial port, IP address, or device identifier
        """
        try:
            # TODO: Replace with actual hardware connection
            # Examples:
            # - Serial: self.serial = serial.Serial(port, 9600, timeout=1)
            # - TCP: self.socket = socket.connect((ip, port))
            # - Vendor SDK: self.controller = VendorAPI.connect(device_id)
            
            logger.info(f"StageController: connecting to {port or 'default'}")
            time.sleep(0.1)  # Simulate connection time
            self.is_connected = True
            logger.info("✅ Stage controller connected")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to stage: {e}")
            raise

    def disconnect(self):
        """Close hardware connection"""
        try:
            # TODO: Close actual hardware connections
            self.is_connected = False
            logger.info("Stage controller disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting stage: {e}")

    def home(self) -> Tuple[float, float]:
        """
        Home the stage to reference position
        
        Returns:
            Current position after homing
        """
        if not self.is_connected:
            raise RuntimeError("Stage not connected")
            
        logger.info("Homing stage...")
        
        # TODO: Send actual homing commands
        # Examples:
        # - G-code: self.send_command("G28")
        # - Vendor: self.controller.home_all_axes()
        
        # Simulate homing time
        time.sleep(1.0)
        
        self.x, self.y = self.config.home_pos
        self.is_homed = True
        
        logger.info(f"✅ Stage homed to ({self.x}, {self.y})")
        return (self.x, self.y)

    def move_abs(self, x_mm: float, y_mm: float, wait: bool = True) -> Tuple[float, float]:
        """
        Move to absolute position
        
        Args:
            x_mm: Target X position in mm
            y_mm: Target Y position in mm
            wait: Wait for move to complete
            
        Returns:
            Final position (x, y)
        """
        if not self.is_connected:
            raise RuntimeError("Stage not connected")
        if not self.is_homed:
            raise RuntimeError("Stage not homed - call home() first")
        if self.emergency_stop:
            raise RuntimeError("Emergency stop active")
            
        # Validate bounds
        if not (0 <= x_mm <= self.config.x_max_mm):
            raise ValueError(f"X position {x_mm} outside bounds [0, {self.config.x_max_mm}]")
        if not (0 <= y_mm <= self.config.y_max_mm):
            raise ValueError(f"Y position {y_mm} outside bounds [0, {self.config.y_max_mm}]")
        
        logger.debug(f"Moving to absolute position x={x_mm:.3f}, y={y_mm:.3f}")
        
        # Calculate travel distance and time
        dx = abs(self.x - x_mm)
        dy = abs(self.y - y_mm)
        travel_distance = (dx**2 + dy**2)**0.5
        
        # TODO: Send actual move commands
        # Examples:
        # - G-code: self.send_command(f"G1 X{x_mm} Y{y_mm} F{feed_rate}")
        # - Vendor: self.controller.move_absolute(x_mm, y_mm)
        
        # Simulate realistic move time based on distance and speed
        travel_time = travel_distance / self.config.max_speed_mm_s + 0.1  # +settling time
        
        # Update position immediately (in real hardware, query actual position)
        self.x, self.y = x_mm, y_mm
        
        if wait:
            time.sleep(travel_time)
            
        return (self.x, self.y)

    def move_rel(self, dx_mm: float, dy_mm: float, wait: bool = True) -> Tuple[float, float]:
        """
        Move relative to current position
        
        Args:
            dx_mm: Relative X movement in mm
            dy_mm: Relative Y movement in mm
            wait: Wait for move to complete
            
        Returns:
            Final position (x, y)
        """
        return self.move_abs(self.x + dx_mm, self.y + dy_mm, wait)

    def get_position(self) -> Tuple[float, float]:
        """
        Get current stage position
        
        Returns:
            Current position (x, y) in mm
        """
        if not self.is_connected:
            raise RuntimeError("Stage not connected")
            
        # TODO: Query actual hardware position
        # Examples:
        # - G-code: position = self.send_query("M114")
        # - Vendor: position = self.controller.get_position()
        
        return (self.x, self.y)

    def stop(self):
        """Emergency stop - halt all motion immediately"""
        logger.warning("🛑 Emergency stop activated")
        self.emergency_stop = True
        
        # TODO: Send emergency stop command to hardware
        # Examples:
        # - G-code: self.send_command("M112")
        # - Vendor: self.controller.emergency_stop()

    def reset_emergency_stop(self):
        """Clear emergency stop condition"""
        logger.info("Clearing emergency stop")
        self.emergency_stop = False
        
        # TODO: Reset hardware emergency stop state if needed

    def is_moving(self) -> bool:
        """
        Check if stage is currently moving
        
        Returns:
            True if any axis is in motion
        """
        # TODO: Query hardware motion status
        # For now, assume moves are instantaneous in simulation
        return False

    def set_speed(self, speed_mm_s: float):
        """
        Set maximum movement speed
        
        Args:
            speed_mm_s: Maximum speed in mm/s
        """
        if speed_mm_s <= 0 or speed_mm_s > self.config.max_speed_mm_s:
            raise ValueError(f"Speed must be between 0 and {self.config.max_speed_mm_s} mm/s")
            
        # TODO: Send speed command to hardware
        logger.info(f"Stage speed set to {speed_mm_s} mm/s")

    def get_limits(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Get stage travel limits
        
        Returns:
            ((x_min, x_max), (y_min, y_max)) in mm
        """
        return ((0.0, self.config.x_max_mm), (0.0, self.config.y_max_mm))

    def __enter__(self):
        """Context manager entry"""
        if not self.is_connected:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
