import pytest
import math
from pygae.math import vec2
from pygae.math.vec2 import Vec2


def test_can_construct_vec2():
    assert Vec2(2, 2)


def test_can_unpack_as_tuple():
    x, y = Vec2(1, 2)
    assert (x, y) == (1, 2)


def test_add_vec2s():
    v = Vec2(1, 2) + Vec2(3, 4)
    assert v == (4, 6)
    assert isinstance(v, Vec2)


def test_add_vec2_and_tuple():
    v = Vec2(1, 2) + (3, 4)
    assert v == (4, 6)
    assert isinstance(v, Vec2)


def test_add_tuple_and_vect2():
    v = (1, 2) + Vec2(3, 4)
    assert v == (4, 6)
    assert isinstance(v, Vec2)


def test_sub_vec2s():
    assert Vec2(5, 5) - Vec2(5, 5) == (0, 0)


def test_sub_vec2_tuple():
    assert Vec2(5, 5) - (5, 5) == (0, 0)


def test_sub_tuple_vec2():
    assert (5, 5) - Vec2(5, 5) == (0, 0)


def test_can_test_equality_with_tuple():
    v = Vec2(1, 2)
    assert v == (1, 2)


def test_can_mulitiply_vec2_with_scalar():
    v = Vec2(3, 5) * 3
    assert v == (9, 15)


def test_can_mulitiply_vec2_with_vec2():
    v = Vec2(3, 5) * Vec2(3, 2)
    assert v == (9, 10)


def test_can_mulitiply_vec2_with_tuple():
    v = Vec2(3, 5) * (3, 2)
    assert v == (9, 10)


def test_can_mulitiply_scalar_with_vec2():
    v = 3 * Vec2(3, 5)
    assert v == (9, 15)


def test_can_mulitiply_tuple_with_vec2():
    v = (3, 5) * Vec2(3, 2)
    assert v == (9, 10)


def test_dot_product_with_vec2():
    v1 = Vec2(2, 3)
    v2 = Vec2(5, 6)
    assert v1.dot(v2) == 28


def test_dot_product_with_tuple():
    v = Vec2(2, 3)
    assert v.dot((5, 6)) == 28


def test_cross_product_with_vec2():
    v1 = Vec2(2, 3)
    v2 = Vec2(5, 6)
    assert v1.cross(v2) == -3


def test_cross_product_with_tuple():
    v = Vec2(2, 3)
    assert v.cross((5, 6)) == -3


def test_magnitude():
    v = Vec2(3, 4)
    assert v.magnitude() == 5


def test_magnitude_of_zero_vector():
    v = Vec2.zero()
    assert v.magnitude() == 0


def test_normalized():
    v = Vec2(3, 4)
    assert v.normalized() == (0.6, 0.8)


def test_normalized_zero_vector():
    v = Vec2.zero()
    with pytest.raises(ZeroDivisionError):
        _ = v.normalized()


def test_lerp_vec2():
    v1 = Vec2(3, 4)
    v2 = Vec2(9, 12)
    assert v1.lerp(v2, 0.5) == (6, 8)


def test_lerp_tuple():
    v1 = Vec2(3, 4)
    assert v1.lerp((9, 12), 0.5) == (6, 8)


def test_rotate_90_deg():
    v = Vec2(5, 0).rotate(math.pi * 0.5)
    assert math.isclose(v.x, 0.0, abs_tol=1e-9)
    assert math.isclose(v.y, 5.0, abs_tol=1e-9)


def test_rotate_zero():
    v = Vec2(3, -4).rotate(0.0)
    assert math.isclose(v.x, 3.0, abs_tol=1e-9)
    assert math.isclose(v.y, -4.0, abs_tol=1e-9)


def test_rotate_180_deg():
    v = Vec2(2, -7).rotate(math.pi)
    assert math.isclose(v.x, -2.0, abs_tol=1e-9)
    assert math.isclose(v.y, 7.0, abs_tol=1e-9)


def test_rotate_negative_angle():
    v = Vec2(0, 3).rotate(-math.pi * 0.5)
    assert math.isclose(v.x, 3.0, abs_tol=1e-9)
    assert math.isclose(v.y, 0.0, abs_tol=1e-9)


def test_rotate_full_circle():
    v = Vec2(-2, 9).rotate(2 * math.pi)
    assert math.isclose(v.x, -2.0, abs_tol=1e-9)
    assert math.isclose(v.y, 9.0, abs_tol=1e-9)


def test_rotate_zero_vector():
    v = Vec2(0, 0).rotate(1.234)
    assert math.isclose(v.x, 0.0, abs_tol=1e-9)
    assert math.isclose(v.y, 0.0, abs_tol=1e-9)


def test_reflect():
    v = Vec2(3, -4).reflect((0, 1))
    assert v == (3, 4)


def test_dist_vec2():
    v1 = Vec2(10, 10)
    v2 = Vec2(13, 14)
    assert v1.distance(v2) == 5


def test_dist_tuple():
    v = Vec2(10, 10)
    assert v.distance((13, 14)) == 5


def test_dist_sq_vec2():
    v1 = Vec2(10, 10)
    v2 = Vec2(13, 14)
    assert v1.distance_sq(v2) == 25


def test_dist_sq_tuple():
    v = Vec2(10, 10)
    assert v.distance_sq((13, 14)) == 25


def test_perpl():
    v = Vec2(0, 5)
    assert v.perpl() == (-5, 0)


def test_perpr():
    v = Vec2(0, 5)
    assert v.perpr() == (5, 0)


def test_project_vec2():
    v1 = Vec2(3, 4)
    v2 = Vec2(1, 0)
    assert v1.project(v2) == (3, 0)


def test_project_tuple():
    v = Vec2(3, 4)
    assert v.project((1, 0)) == (3, 0)


def test_snap():
    v = Vec2(3.3, 4.3)
    assert v.snap() == (3, 4)


def test_repr():
    assert str(Vec2(3.33333, 4.33333)) == "Vec2(x=3.333, y=4.333)"


def test_div_floor():
    v = Vec2(4 * 9.4, 4 * 23.1)
    assert v // 4 == (9, 23)


def test_div():
    v = Vec2(5 * 12.3, 5 * 45.6)
    assert v / 5 == (12.3, 45.6)


def test_swizzles():
    v = Vec2(2, 3)
    assert v.xy == (2, 3)
    assert v.yx == (3, 2)
    assert v.xx == (2, 2)
    assert v.yy == (3, 3)


def test_lt():
    assert Vec2(2, 2) < Vec2(3, 3)
    assert Vec2(2, 0) < Vec2(3, 0)
    assert Vec2(0, 2) < Vec2(0, 3)
    assert Vec2(-2, -2) < Vec2(3, 3)
    assert Vec2(2, 2) < Vec2(-3, -3)
    assert Vec2(-2, -2) < Vec2(-3, -3)
    assert Vec2(-2, 2) < Vec2(3, -3)
    assert not Vec2(3, 3) < Vec2(2, 2)
    assert not Vec2(3, 3) < Vec2(3, 3)


def test_le():
    assert Vec2(2, 2) <= Vec2(3, 3)
    assert Vec2(2, 0) <= Vec2(3, 0)
    assert Vec2(0, 2) <= Vec2(0, 3)
    assert Vec2(-2, -2) <= Vec2(3, 3)
    assert Vec2(2, 2) <= Vec2(-3, -3)
    assert Vec2(-2, -2) <= Vec2(-3, -3)
    assert Vec2(-2, 2) <= Vec2(3, -3)
    assert not Vec2(3, 3) <= Vec2(2, 2)
    assert Vec2(3, 3) <= Vec2(3, 3)


def test_lt():
    assert Vec2(3, 3) > Vec2(2, 2)
    assert Vec2(3, 0) > Vec2(2, 0)
    assert Vec2(0, 3) > Vec2(0, 2)
    assert Vec2(3, 3) > Vec2(-2, -2)
    assert Vec2(-3, -3) > Vec2(2, 2)
    assert Vec2(-3, -3) > Vec2(-2, -2)
    assert Vec2(3, -3) > Vec2(-2, 2)
    assert not Vec2(2, 2) > Vec2(3, 3)
    assert not Vec2(3, 3) > Vec2(3, 3)


def test_le():
    assert Vec2(3, 3) >= Vec2(2, 2)
    assert Vec2(3, 0) >= Vec2(2, 0)
    assert Vec2(0, 3) >= Vec2(0, 2)
    assert Vec2(3, 3) >= Vec2(-2, -2)
    assert Vec2(-3, -3) >= Vec2(2, 2)
    assert Vec2(-3, -3) >= Vec2(-2, -2)
    assert Vec2(3, -3) >= Vec2(-2, 2)
    assert not Vec2(2, 2) >= Vec2(3, 3)
    assert Vec2(3, 3) >= Vec2(3, 3)


def test_to_angle():
    # orthogonal rotations
    assert math.isclose(Vec2(1, 0).angle_to((0, 1)), math.pi / 2)
    assert math.isclose(Vec2(0, 1).angle_to((1, 0)), -math.pi / 2)

    # identical vectors
    assert math.isclose(Vec2(1, 0).angle_to((1, 0)), 0.0)
    assert math.isclose(Vec2(1, 1).angle_to((1, 1)), 0.0)

    # opposite vectors
    assert math.isclose(Vec2(1, 0).angle_to((-1, 0)), math.pi)
    assert math.isclose(Vec2(0, 1).angle_to((0, -1)), math.pi)

    # 45 degree rotations
    assert math.isclose(Vec2(1, 0).angle_to((1, 1)), math.pi / 4)
    assert math.isclose(Vec2(1, 1).angle_to((1, 0)), -math.pi / 4)

    # quadrant transitions
    assert math.isclose(Vec2(1, 1).angle_to((-1, 1)), math.pi / 2)
    assert math.isclose(Vec2(-1, 1).angle_to((-1, -1)), math.pi / 2)
    assert math.isclose(Vec2(-1, -1).angle_to((1, -1)), math.pi / 2)
    assert math.isclose(Vec2(1, -1).angle_to((1, 1)), math.pi / 2)

    # arbitrary directions
    assert math.isclose(Vec2(-1, -1).angle_to((-1, 0)), -math.pi / 4)
    assert math.isclose(Vec2(-1, 0).angle_to((-1, -1)), math.pi / 4)

    # ensure range is [-π, π]
    assert -math.pi <= Vec2(1, 0).angle_to((-1, -0.0001)) <= math.pi


def test_from_angle():
    eps = 1e-7

    # 0 radians → (1,0)
    v = Vec2.from_angle(0)
    assert math.isclose(v.x, 1.0, abs_tol=eps)
    assert math.isclose(v.y, 0.0, abs_tol=eps)

    # π/2 → (0,1)
    v = Vec2.from_angle(math.pi / 2)
    assert math.isclose(v.x, 0.0, abs_tol=eps)
    assert math.isclose(v.y, 1.0, abs_tol=eps)

    # π → (-1,0)
    v = Vec2.from_angle(math.pi)
    assert math.isclose(v.x, -1.0, abs_tol=eps)
    assert math.isclose(v.y, 0.0, abs_tol=eps)

    # -π/2 → (0,-1)
    v = Vec2.from_angle(-math.pi / 2)
    assert math.isclose(v.x, 0.0, abs_tol=eps)
    assert math.isclose(v.y, -1.0, abs_tol=eps)

    # 45° → (√2/2, √2/2)
    v = Vec2.from_angle(math.pi / 4)
    sqrt2_2 = math.sqrt(2) / 2
    assert math.isclose(v.x, sqrt2_2, abs_tol=eps)
    assert math.isclose(v.y, sqrt2_2, abs_tol=eps)
