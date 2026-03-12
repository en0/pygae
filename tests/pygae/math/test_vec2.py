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


def test_normalized():
    v = Vec2(3, 4)
    assert v.normalized() == (0.6, 0.8)


def test_lerp_vec2():
    v1 = Vec2(3, 4)
    v2 = Vec2(9, 12)
    assert v1.lerp(v2, 0.5) == (6, 8)


def test_lerp_tuple():
    v1 = Vec2(3, 4)
    assert v1.lerp((9, 12), 0.5) == (6, 8)


def test_rotate():
    v1 = Vec2(5, 0).rotate(math.pi * 0.5)
    assert math.isclose(v1.x, 0.0, abs_tol=1e-9)
    assert math.isclose(v1.y, 5.0, abs_tol=1e-9)


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
