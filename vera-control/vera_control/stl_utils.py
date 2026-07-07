"""Minimal STL bounding-box reader (binary and ASCII) -- stdlib only.

Used to sanity-check a model against the G1000 build volume before bothering
to invoke the slicer at all.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass


@dataclass
class BoundingBox:
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float

    @property
    def size_x(self) -> float:
        return self.max_x - self.min_x

    @property
    def size_y(self) -> float:
        return self.max_y - self.min_y

    @property
    def size_z(self) -> float:
        return self.max_z - self.min_z


def _is_binary_stl(data: bytes) -> bool:
    if len(data) < 84:
        return False
    facet_count = struct.unpack_from("<I", data, 80)[0]
    expected_len = 84 + facet_count * 50
    return expected_len == len(data)


def read_bounding_box(stl_path: str) -> BoundingBox:
    with open(stl_path, "rb") as f:
        data = f.read()

    if _is_binary_stl(data):
        return _bbox_from_binary(data)
    return _bbox_from_ascii(data.decode("utf-8", errors="replace"))


def _bbox_from_binary(data: bytes) -> BoundingBox:
    facet_count = struct.unpack_from("<I", data, 80)[0]
    xs, ys, zs = [], [], []
    offset = 84
    for _ in range(facet_count):
        # normal (3 floats) + 3 vertices (3 floats each) + attr (uint16)
        for v in range(3):
            vx, vy, vz = struct.unpack_from("<3f", data, offset + 12 + v * 12)
            xs.append(vx)
            ys.append(vy)
            zs.append(vz)
        offset += 50
    return BoundingBox(min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))


def _bbox_from_ascii(text: str) -> BoundingBox:
    xs, ys, zs = [], [], []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("vertex"):
            _, x, y, z = line.split()
            xs.append(float(x))
            ys.append(float(y))
            zs.append(float(z))
    if not xs:
        raise ValueError("no vertices found in ASCII STL")
    return BoundingBox(min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
