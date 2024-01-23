#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of curve-apps package.
#
#  All rights reserved.
#
from pathlib import Path

import numpy as np
from geoh5py import Workspace
from geoh5py.data import FilenameData
from geoh5py.objects import Curve
from geoh5py.ui_json import InputFile

from curve_apps.parts_connection.constants import default_ui_json
from curve_apps.parts_connection.driver import PartsConnectionDriver
from curve_apps.parts_connection.params import Parameters


def setup_example(workspace: Workspace):
    with workspace.open(mode="r+"):
        y_array = np.linspace(0, 50, 10)
        curvey = 5 * np.sin(y_array) + 10
        oblique = 0.7 * y_array + 20
        straight = np.ones_like(y_array) * 30

        vertices = np.c_[
            np.r_[curvey, oblique, straight],
            np.r_[y_array, y_array, y_array],
            np.zeros(len(y_array) * 3),
        ]
        parts = np.tile(np.arange(len(y_array)), 3)
        values = np.kron(np.arange(1, 4), np.ones(len(y_array)))
        curve = Curve.create(workspace=workspace, vertices=vertices, parts=parts)
        data = curve.add_data(
            {
                "values": {
                    "values": values.flatten(order="F"),
                    "value_map": {1: "A", 2: "B", 3: "C"},
                    "type": "referenced",
                },
            }
        )

    return curve, data


def test_driver(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_parts_connection.geoh5")

    curve, data = setup_example(workspace)
    params = Parameters.parse_input(
        {
            "geoh5": workspace,
            "objects": curve,
            "data": data,
            "export_as": "test",
        }
    )

    driver = PartsConnectionDriver(params)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("test")[0]

        assert len(edges.cells) == 4

    # Repeat with different window size

    params.detection.window_size = 32
    params.detection.line_gap = 1
    params.detection.line_length = 4
    params.output.export_as = "square_32"
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("square_32")[0]

        assert len(edges.cells) == 22


def test_input_file(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_parts_connection.geoh5")

    grid, data = setup_example(workspace)
    ifile = InputFile(ui_json=default_ui_json)

    ifile.update_ui_values(
        {
            "geoh5": workspace,
            "objects": grid,
            "data": data,
            "export_as": "square",
        }
    )
    ifile.write_ui_json(str(tmp_path / "test_parts_connection"))
    driver = PartsConnectionDriver(ifile)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("square")[0]
        assert edges is not None

        assert any(child for child in edges.children if isinstance(child, FilenameData))
