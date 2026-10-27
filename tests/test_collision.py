from endoscope_ai_training.core.collision import CollisionConfig, CollisionDetector, CollisionLevel, judge_collision


def test_judge_collision_returns_none_when_far_from_wall():
    state, strength = judge_collision(20.0, 0.9, 0.0, 0)
    assert state is CollisionLevel.NONE
    assert strength == 0


def test_judge_collision_warns_inside_warning_distance():
    state, strength = judge_collision(4.0, 0.9, 0.0, 0)
    assert state is CollisionLevel.WARN
    assert strength == 50


def test_judge_collision_detects_light_and_heavy_contact():
    light, light_strength = judge_collision(7.0, 0.4, 0.01, 3)
    heavy, heavy_strength = judge_collision(1.0, 0.4, 0.2, 3)
    assert light is CollisionLevel.LIGHT
    assert 10 <= light_strength < 60
    assert heavy is CollisionLevel.HEAVY
    assert heavy_strength >= 60


def test_collision_detector_requires_confirmed_contact_frames():
    detector = CollisionDetector(CollisionConfig(confirm_frames=3))

    assert detector.update(1.0, 0.4, 0.2, "L1", 1_000, 1) is None
    assert detector.update(1.0, 0.4, 0.2, "L1", 1_033, 2) is None
    event = detector.update(1.0, 0.4, 0.2, "L1", 1_066, 3)

    assert event is not None
    assert event.level == "heavy"
    assert event.node_id == "L1"
    assert event.frame_seq == 3

