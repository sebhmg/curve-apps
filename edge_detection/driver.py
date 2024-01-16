#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

# pylint: disable=too-many-locals

from __future__ import annotations

import sys

import numpy as np
from geoapps_utils.driver.driver import BaseDriver
from geoh5py.data import FloatData
from geoh5py.groups import ContainerGroup, Group
from geoh5py.objects import Curve, Grid2D, ObjectBase
from geoh5py.ui_json import InputFile
from skimage.feature import canny
from skimage.transform import probabilistic_hough_line

from .params import ApplicationParameters, DetectionParameters


class EdgeDetectionDriver(BaseDriver):
    """
    Driver for the edge detection application.

    :param parameters: Application parameters.
    """

    def __init__(self, parameters: ApplicationParameters | InputFile):
        if isinstance(parameters, InputFile):
            if not isinstance(parameters.data, dict):
                raise TypeError("InputFile must have a 'data' dictionary.")

            parameters = ApplicationParameters.parse_input_data(parameters.data)

        super().__init__(parameters)

    def run(self):
        """
        Driver for Grid2D objects for the automated detection of line features.
        The application relies on the Canny and Hough transforms from the
        Scikit-Image library.
        """
        with self.workspace.open(mode="r+") as workspace:
            parent = None
            if self.params.output.out_group is not None:
                parent = ContainerGroup.create(
                    workspace=workspace,
                    name=self.params.output.ga_group_name,
                )

            vertices, cells = EdgeDetectionDriver.get_edges(
                self.params.source.objects,
                self.params.source.data,
                self.params.detection,
            )

            name = "Edge Detection"
            if self.params.output.export_as is not None:
                name = self.params.output.export_as

            edges = Curve.create(
                workspace=workspace,
                name=name,
                vertices=vertices,
                cells=cells,
                parent=parent,
            )

            if edges is not None:
                self.update_monitoring_directory(
                    parent if parent is not None else edges
                )

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
        if grid.centroids is None or grid.shape is None or data.values is None:
            return None, None

        x = grid.centroids[:, 0].reshape(grid.shape, order="F")
        y = grid.centroids[:, 1].reshape(grid.shape, order="F")
        z = grid.centroids[:, 2].reshape(grid.shape, order="F")
        grid_data = data.values.reshape(grid.shape, order="F")

        indices = np.ones_like(grid_data, dtype="bool")

        ind_x, ind_y = (
            np.any(indices, axis=1),
            np.any(indices, axis=0),
        )
        x = x[ind_x, :][:, ind_y]
        y = y[ind_x, :][:, ind_y]
        z = z[ind_x, :][:, ind_y]
        grid_data = grid_data[ind_x, :][:, ind_y]
        grid_data -= np.nanmin(grid_data)
        grid_data /= np.nanmax(grid_data)
        grid_data[np.isnan(grid_data)] = 0

        if not np.any(grid_data):
            return None, None

        # Find edges
        edges = canny(grid_data, sigma=detection.sigma, use_quantiles=True)

        shape = edges.shape

        # Cycle through tiles of square size
        if detection.window_size is None:
            window_size = np.inf
        else:
            window_size = detection.window_size

        max_l = np.min([window_size, shape[0], shape[1]])
        half = np.floor(max_l / 2)
        overlap = 1.25

        n_cell_y = (shape[0] - 2 * half) * overlap / max_l
        n_cell_x = (shape[1] - 2 * half) * overlap / max_l

        if n_cell_x > 0:
            cnt_x = np.linspace(
                half, shape[1] - half, 2 + int(np.round(n_cell_x)), dtype=int
            ).tolist()
            half_x = half
        else:
            cnt_x = [np.ceil(shape[1] / 2)]
            half_x = np.ceil(shape[1] / 2)

        if n_cell_y > 0:
            cnt_y = np.linspace(
                half, shape[0] - half, 2 + int(np.round(n_cell_y)), dtype=int
            ).tolist()
            half_y = half
        else:
            cnt_y = [np.ceil(shape[0] / 2)]
            half_y = np.ceil(shape[0] / 2)

        coords = []
        for cx in cnt_x:
            for cy in cnt_y:
                i_min, i_max = int(cy - half_y), int(cy + half_y)
                j_min, j_max = int(cx - half_x), int(cx + half_x)
                lines = probabilistic_hough_line(
                    edges[i_min:i_max, j_min:j_max],
                    line_length=detection.line_length,
                    threshold=detection.threshold,
                    line_gap=detection.line_gap,
                    seed=0,
                )

                if np.any(lines):
                    coord = np.vstack(lines)
                    coords.append(
                        np.c_[
                            x[i_min:i_max, j_min:j_max][coord[:, 1], coord[:, 0]],
                            y[i_min:i_max, j_min:j_max][coord[:, 1], coord[:, 0]],
                            z[i_min:i_max, j_min:j_max][coord[:, 1], coord[:, 0]],
                        ]
                    )

        if coords:
            vertices = np.vstack(coords)
            cells = np.arange(vertices.shape[0]).astype("uint32").reshape((-1, 2))
            return vertices, cells

        return None, None

    @property
    def params(self) -> ApplicationParameters:
        """Application parameters."""
        return self._params

    @params.setter
    def params(self, val: ApplicationParameters):
        if not isinstance(val, ApplicationParameters):
            raise TypeError("Parameters must be of type ApplicationParameters.")
        self._params = val

    def add_ui_json(self, entity: ObjectBase | Group):
        """
        Add ui.json file to entity.

        :param entity: Object to add ui.json file to.
        """
        if self.params.input_file is None:
            return

        param_dict = self.params.flatten()
        self.params.input_file.update_ui_values(param_dict)
        file_path = self.params.input_file.write_ui_json()
        entity.add_file(str(file_path))


if __name__ == "__main__":
    file = sys.argv[1]
    EdgeDetectionDriver.start(file)
