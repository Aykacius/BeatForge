"""Unit tests for mapping engine."""

import pytest
import numpy as np
from app.mapping.cursor_physics import CursorPhysics
from app.mapping.pattern_grammar import PatternGrammar


@pytest.fixture
def cursor_physics():
    """Create cursor physics instance."""
    return CursorPhysics(
        min_distance=50.0,
        max_distance=250.0,
        playfield_width=512,
        playfield_height=384,
    )


@pytest.fixture
def pattern_grammar():
    """Create pattern grammar instance."""
    return PatternGrammar()


def test_cursor_physics_basic(cursor_physics):
    """Test basic cursor physics."""
    current_pos = (256.0, 192.0)
    target_pos = (300.0, 192.0)
    velocity = np.array([0.0, 0.0])
    direction = 0.0
    
    new_x, new_y, new_vel, new_dir = cursor_physics.apply(
        current_pos=current_pos,
        target_pos=target_pos,
        current_velocity=velocity,
        current_direction=direction,
        time_since_last=0.1,
    )
    
    assert 0 <= new_x <= 512
    assert 0 <= new_y <= 384
    assert isinstance(new_vel, np.ndarray)
    assert isinstance(new_dir, float)


def test_cursor_physics_momentum(cursor_physics):
    """Test cursor momentum preservation."""
    current_pos = (256.0, 192.0)
    target_pos = (256.0, 192.0)
    velocity = np.array([100.0, 0.0])
    direction = 0.0
    
    new_x, new_y, new_vel, new_dir = cursor_physics.apply(
        current_pos=current_pos,
        target_pos=target_pos,
        current_velocity=velocity,
        current_direction=direction,
        time_since_last=0.1,
    )
    
    # Velocity should decay
    new_speed = np.linalg.norm(new_vel)
    old_speed = np.linalg.norm(velocity)
    assert new_speed < old_speed


def test_pattern_grammar_stream(pattern_grammar):
    """Test stream pattern generation."""
    config = {
        "min_spacing": 80.0,
        "max_spacing": 200.0,
        "stream_length": 5,
    }
    
    positions = pattern_grammar.generate("stream", config)
    
    assert len(positions) == 5
    for x, y in positions:
        assert 0 <= x <= 512
        assert 0 <= y <= 384


def test_pattern_grammar_jump(pattern_grammar):
    """Test jump pattern generation."""
    config = {
        "jump_distance": 150.0,
    }
    
    positions = pattern_grammar.generate("jump", config)
    
    assert len(positions) == 2
    # Distance between jumps should be roughly 2x the jump distance
    dx = positions[0][0] - positions[1][0]
    dy = positions[0][1] - positions[1][1]
    distance = np.sqrt(dx**2 + dy**2)
    assert distance > 200  # Should be far apart
