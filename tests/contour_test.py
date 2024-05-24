#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of edge-detection package.
#
#  All rights reserved.
#

import numpy as np
from geoh5py import Workspace
from geoh5py.objects import Points

from curve_apps.contours.driver import ContoursDriver
from curve_apps.contours.params import Parameters


def test_get_contours(tmp_path):

    ws = Workspace(tmp_path / "test.geoh5")
    x = np.linspace(0, 11, 20)
    y = np.linspace(0, 11, 20)
    X, Y = np.meshgrid(x, y)
    Z = np.ones_like(X)
    Z[X > 5] = 10
    values = Z.flatten()
    vertices = np.c_[X.flatten(), Y.flatten(), np.zeros_like(values)]
    pts = Points.create(ws, name="my points", vertices=vertices)
    data = pts.add_data({"my data": {"values": values}})

    params_dict = {
        "geoh5": ws,
        "objects": pts,
        "data": data,
        "fixed_contours": [10.0],
    }
    params = Parameters.build(params_dict)
    contours = ContoursDriver.get_contours(params)
    assert np.all(contours.allsegs[0][0][:, 0] > 5)
