#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of edge-detection package.
#
#  All rights reserved.
#

import numpy as np
from geoh5py import Workspace
from geoh5py.objects import Points

from curve_apps.contours.params import ContourParameters, Parameters, SourceParameters


def test_update_input_file(tmp_path):
    ws = Workspace(tmp_path / "test.geoh5")
    vertices = np.random.rand(100, 3)
    pts = Points.create(ws, vertices=vertices, name="my points")
    data = pts.add_data({"my data": {"values": np.random.rand(100)}})

    params = Parameters(
        geoh5=ws,
        source=SourceParameters(objects=pts, data=data),
        contours=ContourParameters(fixed_contours=[0.1]),
    )

    assert params.input_file.data["fixed_contours"] == [0.1]
