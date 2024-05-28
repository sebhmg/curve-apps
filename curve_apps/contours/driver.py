#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of edge-detection package.
#
#  All rights reserved.
#
#
#  This file is part of curve-apps.
#
#  curve-apps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from __future__ import annotations

import logging
import sys

import matplotlib.pyplot as plt
import numpy as np
from geoapps.utils.formatters import string_name
from geoh5py.objects import Curve, Grid2D
from geoh5py.ui_json import InputFile, utils

from curve_apps.contours.params import ContourParameters
from curve_apps.driver import BaseCurveDriver
from curve_apps.utils import extract_data, set_vertices_height

logger = logging.getLogger(__name__)


class ContoursDriver(BaseCurveDriver):
    """
    Driver for the detection of contours within geoh5py objects.

    :param parameters: Application parameters.
    """

    _parameter_class = ContourParameters

    def __init__(self, parameters: ContourParameters | InputFile):
        super().__init__(parameters)

    def make_curve(self):
        """
        Make curve object from contours detected in source data.
        """

        with utils.fetch_active_workspace(self.workspace, mode="r+"):
            logger.info("Generating contours ...")
            contours = ContoursDriver.get_contours(self.params)
            vertices, cells, values = extract_data(contours)
            if vertices:
                locations = np.vstack(vertices)
                if self.params.output.z_value:
                    locations = np.c_[locations, np.hstack(values)]
                else:
                    locations = set_vertices_height(
                        locations, self.params.source.objects
                    )

            curve = Curve.create(
                self.workspace,
                name=string_name(self.params.output.export_as),
                vertices=locations,
                cells=np.vstack(cells).astype("uint32"),
                parent=self.out_group,
            )
            curve.add_data(
                {self.params.detection.contour_string: {"values": np.hstack(values)}}
            )

            return curve

    @staticmethod
    def get_contours(params: ContourParameters):

        entity = params.source.objects
        data = params.source.data
        locations = entity.locations
        x, y = locations[:, :2].T
        axis = plt.axes()
        if isinstance(entity, Grid2D):
            contours = axis.contour(
                x.reshape(entity.shape, order="F"),
                y.reshape(entity.shape, order="F"),
                data.values.reshape(entity.shape, order="F"),
                levels=params.detection.contours,
            )
        else:
            contours = axis.tricontour(
                x,
                y,
                data.values,
                levels=params.detection.contours,
            )
        return contours


if __name__ == "__main__":
    file = sys.argv[1]
    ifile = InputFile.read_ui_json(file)

    driver = ContoursDriver(ifile)
    driver.run()
