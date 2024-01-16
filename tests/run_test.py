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
from edge_detection.params import ApplicationParameters


def setup_example(workspace: Workspace):
    with workspace.open(mode="r+"):
        grid = Grid2D.create(
            workspace,
            origin=[0, 0, 0],
            u_cell_size=8.0,
            v_cell_size=8.0,
            u_count=64,
            v_count=64,
        )

        model = np.zeros((64, 64))
        model[16:32, 8:24] = 1.0
        data = grid.add_data({"values": {"values": model.flatten()}})

    return grid, data


def test_driver(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_edge_detection.geoh5")

    grid, data = setup_example(workspace)
    params = ApplicationParameters.parse_input(
        {
            "geoh5": workspace,
            "objects": grid,
            "data": data,
            "line_length": 12,
            "line_gap": 8,
            "sigma": 1,
            "export_as": "square",
        }
    )

    driver = EdgeDetectionDriver(params)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("square")[0]

        assert len(edges.cells) == 4
