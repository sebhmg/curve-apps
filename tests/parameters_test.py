#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of edge-detection package.
#
#  All rights reserved.
#

import numpy as np
from geoh5py.objects import Grid2D
from geoh5py.ui_json import InputFile
from geoh5py.workspace import Workspace

from curve_apps.edge_detection.params import (
    DetectionParameters,
    OutputParameters,
    Parameters,
    SourceParameters,
)


def test_edge_detection_params(tmp_path):

    n_x, n_y = 10, 15
    with Workspace(tmp_path / "test.geoh5") as ws:
        grid = Grid2D.create(
            ws,
            origin=[0, 0, 0],
            u_cell_size=20.0,
            v_cell_size=30.0,
            u_count=n_x,
            v_count=n_y,
            name="my grid",
            allow_move=False,
        )
        data = grid.add_data({"my data": {"values": np.random.rand(n_x * n_y)}})

    source_params = SourceParameters(objects=grid, data=data)
    detection_params = DetectionParameters(line_length=2)
    output_params = OutputParameters()
    params = Parameters(
        geoh5=ws, source=source_params, detection=detection_params, output=output_params
    )
    assert params.title == "Edge Detection"
    assert params.run_command == "curve_apps.edge_detection.driver"

    params.write_ui_json(tmp_path / "validation.ui.json")

    ifile = InputFile.read_ui_json(tmp_path / "validation.ui.json")
    assert ifile.data["objects"].uid == grid.uid
    assert ifile.data["data"].uid == data.uid
    assert ifile.data["line_length"] == 2
    assert ifile.data["line_gap"] == 1
