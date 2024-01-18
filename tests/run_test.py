#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of edge-detection package.
#
#  All rights reserved.
#
from pathlib import Path

import numpy as np
from geoh5py import Workspace
from geoh5py.objects import Grid2D

from edge_detection.driver import EdgeDetectionDriver
from edge_detection.params import Parameters


def setup_example(workspace: Workspace):
    with workspace.open(mode="r+"):
        grid = Grid2D.create(
            workspace,
            origin=[128, 64, 32],
            u_cell_size=8.0,
            v_cell_size=8.0,
            u_count=128,
            v_count=64,
            dip=45.0,
            rotation=60.0,
        )

        model = np.ones((128, 64)) * 2.0
        model[16:32, 8:24] = 1.0
        model[64:72, 40:48] = 3.0
        model[120:, 40:] = np.nan
        data = grid.add_data({"values": {"values": model.flatten(order="F")}})

    return grid, data


def test_driver(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_edge_detection.geoh5")

    grid, data = setup_example(workspace)
    params = Parameters.parse_input(
        {
            "geoh5": workspace,
            "objects": grid,
            "data": data,
            "line_length": 12,
            "line_gap": 1,
            "sigma": 1,
            "export_as": "square",
        }
    )

    driver = EdgeDetectionDriver(params)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("square")[0]

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
