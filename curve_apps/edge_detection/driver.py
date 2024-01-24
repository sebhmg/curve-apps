#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of edge-detection package.
#
#  All rights reserved.
#
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).


from __future__ import annotations

import sys

import numpy as np
from geoapps_utils.locations import get_overlapping_limits, map_indices_to_coordinates
from geoh5py.data import FloatData
from geoh5py.groups import ContainerGroup
from geoh5py.objects import Curve, Grid2D
from geoh5py.ui_json import InputFile, utils
from skimage.feature import canny
from skimage.transform import probabilistic_hough_line

from ..driver import BaseCurveDriver
from .params import DetectionParameters, Parameters


class EdgeDetectionDriver(BaseCurveDriver):
    """
    Driver for the edge detection application.

    :param parameters: Application parameters.
    """

    _parameter_class = Parameters

    def __init__(self, parameters: Parameters | InputFile):
        super().__init__(parameters)

    def create_output(self, name, parent: ContainerGroup | None = None):
        """
        Driver for Grid2D objects for the automated detection of line features.
        The application relies on the Canny and Hough transforms from the
        Scikit-Image library.

        :param name: Name of the output object.
        :param parent: Optional parent group.
        """
        with utils.fetch_active_workspace(self.workspace) as workspace:
            vertices, cells = EdgeDetectionDriver.get_edges(
                self.params.source.objects,
                self.params.source.data,
                self.params.detection,
            )
            edges = Curve.create(
                workspace=workspace,
                name=name,
                vertices=vertices,
                cells=cells,
                parent=parent,
            )

        return edges

    @staticmethod
    def get_edges(
        grid: Grid2D,
        data: FloatData,
        detection: DetectionParameters,
    ) -> tuple:
        """
        Find edges in gridded data.

        :params grid: A Grid2D object.
        :params data: Input data.
        :params detection: Detection parameters.

        :returns : n x 3 array. Vertices of edges.
        :returns : list
            n x 2 float array. Cells of edges.

        """
        if grid.shape is None or data.values is None:
            return None, None

        grid_data = data.values.reshape(grid.shape, order="F")

        if np.all(np.isnan(grid_data)):
            return None, None

        # Find edges
        edges = canny(
            grid_data,
            sigma=detection.sigma,
            use_quantiles=True,
            mask=~np.isnan(grid_data),
            mode="reflect",
        )
        grid.add_data({"canny filter": {"values": edges.flatten(order="F")}})

        # Find lines
        indices = EdgeDetectionDriver.get_line_indices(
            edges,
            detection.line_length,
            detection.line_gap,
            detection.threshold,
            detection.window_size,
        )

        if len(indices) == 0:
            return None, None

        u_ind, r_ind = np.unique(np.vstack(indices), axis=0, return_inverse=True)
        vertices = map_indices_to_coordinates(grid, u_ind)
        cells = r_ind.reshape((-1, 2))
        return vertices, cells

    @staticmethod
    def get_line_indices(
        canny_image: np.ndarray,
        line_length: int = 1,
        line_gap: int = 1,
        threshold: int = 1,
        window_size: int | None = None,
    ) -> list:
        """
        Get indices forming lines on a canny image.

        The process is done over tiles of square size. The tiles overlap by 25%.

        :param canny_image: Edges.
        :param line_length: Minimum accepted pixel length of detected lines. (Hough)
        :param line_gap: Maximum gap between pixels to still form a line. (Hough)
        :param threshold: Value threshold. (Hough)

        :returns: List of indices.
        """
        # Cycle through tiles of square size
        width = np.min(canny_image.shape)
        if window_size is not None:
            width = np.min([window_size, width])

        x_limits = get_overlapping_limits(canny_image.shape[0], width)
        y_limits = get_overlapping_limits(canny_image.shape[1], width)

        # TODO: Loop in parallel
        indices = []
        for x_lim in x_limits:
            for y_lim in y_limits:
                lines = probabilistic_hough_line(
                    canny_image[x_lim[0] : x_lim[1], y_lim[0] : y_lim[1]],
                    line_length=line_length,
                    threshold=threshold,
                    line_gap=line_gap,
                    seed=0,
                )

                if np.any(lines):
                    # Add the limits of the tile to the indices
                    lines = np.vstack(lines)[:, ::-1] + np.c_[x_lim[0], y_lim[0]]
                    indices.append(lines)

        return indices


if __name__ == "__main__":
    file = sys.argv[1]
    ifile = InputFile.read_ui_json(file)

    driver = EdgeDetectionDriver(ifile)
    driver.run()
