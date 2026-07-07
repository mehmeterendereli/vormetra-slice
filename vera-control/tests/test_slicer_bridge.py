import struct

import pytest

from vera_control import config, slicer_bridge


def _write_cube_stl(path, sx=200, sy=200, sz=100):
    corners = [
        (0, 0, 0), (sx, 0, 0), (sx, sy, 0), (0, sy, 0),
        (0, 0, sz), (sx, 0, sz), (sx, sy, sz), (0, sy, sz),
    ]
    # All 6 faces (12 triangles) -- a real closed/manifold solid. Earlier this
    # only had the top+bottom faces, which produced an open, non-manifold
    # mesh that the slicer correctly refused to process (not a bridge bug).
    tris = [
        (0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
        (0, 1, 5), (0, 5, 4), (3, 6, 2), (3, 7, 6),
        (0, 4, 7), (0, 7, 3), (1, 2, 6), (1, 6, 5),
    ]
    with open(path, "wb") as f:
        f.write(b"x" * 80)
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            f.write(struct.pack("<3f", 0, 0, 1))
            for idx in (a, b, c):
                f.write(struct.pack("<3f", *corners[idx]))
            f.write(struct.pack("<H", 0))


def test_validate_model_fits_within_g1000_bed(tmp_path):
    stl_path = tmp_path / "small.stl"
    _write_cube_stl(stl_path, 200, 200, 100)

    result = slicer_bridge.validate_model(str(stl_path))

    assert result["fits"] is True
    assert result["problems"] == []
    assert result["bounding_box_mm"] == {"x": 200.0, "y": 200.0, "z": 100.0}


def test_validate_model_flags_oversized_object(tmp_path):
    stl_path = tmp_path / "too_big.stl"
    _write_cube_stl(stl_path, 1200, 200, 100)

    result = slicer_bridge.validate_model(str(stl_path))

    assert result["fits"] is False
    assert any("X boyutu" in p for p in result["problems"])


def test_list_filaments_matches_config():
    assert slicer_bridge.list_filaments() == sorted(config.FILAMENT_CHOICES.keys())


def test_slice_model_unknown_filament_raises(tmp_path):
    stl_path = tmp_path / "cube.stl"
    _write_cube_stl(stl_path)

    with pytest.raises(slicer_bridge.VeraSlicerError, match="unknown filament"):
        slicer_bridge.slice_model(str(stl_path), filament="titanium")


def test_slice_model_missing_stl_raises():
    with pytest.raises(slicer_bridge.VeraSlicerError, match="model not found"):
        slicer_bridge.slice_model("does-not-exist.stl")


def test_parse_header_extracts_known_fields():
    gcode = (
        "; HEADER_BLOCK_START\n"
        "; total layer number: 50\n"
        "; filament_density: 1.27\n"
        "; filament_diameter: 1.12838\n"
        "; max_z_height: 100.00\n"
        "; HEADER_BLOCK_END\n"
        "; EXECUTABLE_BLOCK_START\n"
        "G28\n"
        "; bed_shape = 0x0,1000x0,1000x1000,0x1000\n"
    )

    stats = slicer_bridge._parse_header(gcode)

    assert stats["total_layers"] == 50
    assert stats["filament_density"] == 1.27
    assert stats["filament_diameter"] == 1.12838
    assert stats["max_z_height_mm"] == 100.0
    assert stats["bed_shape"] == "0x0,1000x0,1000x1000,0x1000"


@pytest.mark.skipif(
    not config.SLICER_BIN.exists(),
    reason="no slicer binary at VERA_SLICER_BIN -- set it to run the real integration test",
)
def test_slice_model_real_binary_end_to_end():
    # Deliberately not pytest's tmp_path: the underlying CLI has shown path-
    # sensitivity before (see resources/profiles/VORMETRA/README.md) and
    # config.DATA_DIR is the same real, already-proven-working location the
    # bridge uses by default.
    work_dir = config.DATA_DIR / "test-fixtures"
    work_dir.mkdir(parents=True, exist_ok=True)
    stl_path = work_dir / "cube.stl"
    _write_cube_stl(stl_path, 200, 200, 100)

    result = slicer_bridge.slice_model(str(stl_path), filament="petg", output_dir=work_dir / "out")

    assert result.gcode_3mf_path.exists()
    assert result.stats["total_layers"] == 50
    assert result.stats["filament_diameter"] == pytest.approx(1.12838, abs=1e-4)
    assert result.stats["bed_shape"] == "0x0,1000x0,1000x1000,0x1000"
