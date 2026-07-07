import struct

from vera_control.stl_utils import read_bounding_box


def _write_binary_cube(path, sx, sy, sz):
    corners = [
        (0, 0, 0), (sx, 0, 0), (sx, sy, 0), (0, sy, 0),
        (0, 0, sz), (sx, 0, sz), (sx, sy, sz), (0, sy, sz),
    ]
    tris = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7)]  # a few faces is enough
    with open(path, "wb") as f:
        f.write(b"x" * 80)
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            f.write(struct.pack("<3f", 0, 0, 1))
            for idx in (a, b, c):
                f.write(struct.pack("<3f", *corners[idx]))
            f.write(struct.pack("<H", 0))


def test_binary_stl_bounding_box(tmp_path):
    stl_path = tmp_path / "cube.stl"
    _write_binary_cube(stl_path, 200, 150, 80)

    bbox = read_bounding_box(str(stl_path))

    assert bbox.size_x == 200
    assert bbox.size_y == 150
    assert bbox.size_z == 80


def test_ascii_stl_bounding_box(tmp_path):
    stl_path = tmp_path / "cube.ascii.stl"
    stl_path.write_text(
        "solid test\n"
        "facet normal 0 0 1\n outer loop\n"
        "  vertex 0 0 0\n  vertex 10 0 0\n  vertex 10 10 5\n"
        " endloop\nendfacet\n"
        "endsolid test\n"
    )

    bbox = read_bounding_box(str(stl_path))

    assert bbox.size_x == 10
    assert bbox.size_y == 10
    assert bbox.size_z == 5
