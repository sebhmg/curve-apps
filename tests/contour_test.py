#  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024 Mira Geoscience Ltd.                                       '
#                                                                                '
#  All rights reserved.                                                          '
#                                                                                '
#  This file is part of curve-apps.                                              '
#                                                                                '
#  curve-apps is distributed under the terms and conditions of the MIT License   '
#  (see LICENSE file at the root of this source code package).                   '
#  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import numpy as np
from geoh5py import Workspace
from geoh5py.objects import Points

from curve_apps.contours.driver import ContoursDriver
from curve_apps.contours.params import ContourParameters


def get_contour_data(tmp_path):
    ws = Workspace(tmp_path / "test.geoh5")
    x = np.linspace(0, 11, 20)
    y = np.linspace(0, 11, 20)
    x_grid, y_grid = np.meshgrid(x, y)
    z_grid = np.ones_like(x_grid)
    z_grid[x_grid > 5] = 10
    values = z_grid.flatten()
    vertices = np.c_[x_grid.flatten(), y_grid.flatten(), np.zeros_like(values)]
    pts = Points.create(ws, name="my points", vertices=vertices)
    data = pts.add_data({"my data": {"values": values}})

    params_dict = {
        "geoh5": ws,
        "objects": pts,
        "data": data,
        "fixed_contours": [10.0],
        "export_as": "my curve",
    }
    params = ContourParameters.build(params_dict)
    contours = ContoursDriver.get_contours(params)

    return contours, params


def test_driver(tmp_path):
    _, params = get_contour_data(tmp_path)
    driver = ContoursDriver(params)
    driver.run()

    with params.geoh5.open():
        curve = params.geoh5.get_entity("my curve")[0]
        assert np.all(curve.vertices[:, 0] > 5)
