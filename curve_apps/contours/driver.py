#  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024 Mira Geoscience Ltd.                                       '
#                                                                                '
#  This file is part of contours package.                                        '
#                                                                                '
#  All rights reserved.                                                          '
#                                                                                '
#                                                                                '
#  This file is part of curve-apps.                                              '
#                                                                                '
#  curve-apps is distributed under the terms and conditions of the MIT License   '
#  (see LICENSE file at the root of this source code package).                   '
#  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from __future__ import annotations

import logging
import sys
from collections.abc import Callable

import numpy as np
from geoapps_utils.formatters import string_name
from geoh5py.objects import Curve
from geoh5py.ui_json import InputFile, utils
from scipy.interpolate import interp1d
from skimage import measure

from curve_apps.contours.params import ContourParameters
from curve_apps.driver import BaseCurveDriver
from curve_apps.utils import interp_to_grid, set_vertices_height

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
            grid, data = interp_to_grid(
                self.params.source.objects,
                self.params.source.data.values,
                self.params.detection.resolution,
                self.params.detection.max_distance,
            )

            vertices, edges, values = ContoursDriver.get_contours(
                grid, data, self.params.detection.contours
            )

            locations = vertices
            if self.params.output.z_value:
                locations = np.c_[locations, values]
            else:
                locations = set_vertices_height(locations, self.params.source.objects)

            curve = Curve.create(
                self.workspace,
                name=string_name(self.params.output.export_as),
                vertices=locations,
                cells=edges,
                parent=self.out_group,
            )
            curve.add_data(
                {
                    self.params.source.data.name: {
                        "association": "VERTEX",
                        "values": values,
                    }
                }
            )

            return curve

    @staticmethod
    def get_contours(
        grid: list[np.ndarray], data: np.ndarray, contour_list: list[float]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Return vertices, edges, and values for contours.

        :param grid: list of x and y grids.
        :param data: 2D array of data living in grid.
        :param contour_list: list of contour values.
        """

        interp = ContoursDriver.image_to_grid(data, grid)
        vertices, edges, values = [], [], []
        v0 = 0
        for contour in contour_list:

            coords = measure.find_contours(data, contour, fully_connected="low")
            if not coords:
                continue

            for coord in coords:
                segment_vertices = interp(coord[:, 1], coord[:, 0])
                nv = len(segment_vertices)
                segment_edges = np.c_[np.arange(nv - 1), np.arange(1, nv)] + v0
                vertices.append(segment_vertices)
                edges.append(segment_edges)
                values.append([contour] * nv)
                v0 += nv

        if not vertices:
            raise ValueError(
                "No contours detected. Check that the requested contour "
                "values are within the bounds of the data."
            )

        return (
            np.vstack(vertices),
            np.vstack(edges).astype("uint32"),
            np.hstack(values),
        )

    @staticmethod
    def image_to_grid(image, grid) -> Callable:
        """
        Returns a function to interpolate from image to grid coordinates.

        :param grid: list of x and y grids.
        """
        col = np.arange(image.shape[1])
        row = np.arange(image.shape[0])
        x_interp = interp1d(col, np.unique(grid[0]))
        y_interp = interp1d(row, np.unique(grid[1]))

        def interpolator(col, row):
            return np.c_[x_interp(col), y_interp(row)]

        return interpolator

    # @staticmethod
    # def get_contours(params: ContourParameters):
    #     """
    #     Calculate contour from source data.
    #
    #     :param params: Contour parameters
    #     """
    #
    #     entity = params.source.objects
    #     data = params.source.data
    #     locations = entity.locations
    #     x, y = locations[:, :2].T
    #     axis = plt.axes()
    #     if isinstance(entity, Grid2D):
    #         # TODO: Replace with scikit-image contour algorithm
    #         contours = axis.contour(
    #             x.reshape(entity.shape, order="F"),
    #             y.reshape(entity.shape, order="F"),
    #             data.values.reshape(entity.shape, order="F"),
    #             levels=params.detection.contours,
    #         )
    #     else:
    #         # TODO: Replace with scikit-image contour algorithm
    #         contours = axis.tricontour(
    #             x,
    #             y,
    #             data.values,
    #             levels=params.detection.contours,
    #         )
    #     return contours


if __name__ == "__main__":
    file = sys.argv[1]
    ifile = InputFile.read_ui_json(file)

    driver = ContoursDriver(ifile)
    driver.run()
