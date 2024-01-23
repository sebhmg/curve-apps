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
from geoapps_utils.driver.driver import BaseDriver
from geoapps_utils.numerical import find_curves
from geoh5py.data import ReferencedData
from geoh5py.groups import ContainerGroup, Group
from geoh5py.objects import Curve, ObjectBase
from geoh5py.ui_json import InputFile

from .params import DetectionParameters, Parameters


class PartsConnectionDriver(BaseDriver):
    """
    Driver for the edge detection application.

    :param parameters: Application parameters.
    """

    def __init__(self, parameters: Parameters | InputFile):
        if isinstance(parameters, InputFile):
            parameters = Parameters.parse_input(parameters)

        # TODO need to re-type params in base class
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

            vertices, cells = PartsConnectionDriver.get_connections(
                self.params.source.objects,
                self.params.source.data,
                self.params.detection,
            )

            name = "Parts Connection"
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
    def get_connections(
        curve: Curve,
        data: ReferencedData | None,
        detection: DetectionParameters,
    ) -> tuple:
        """
        Find connections between curve parts.

        :params curve: A Curve object with parts.
        :params data: Input referenced data.
        :params detection: Detection parameters.

        :returns : n x 3 array. Vertices of connecting lines.
        :returns : list
            n x 2 float array. Cells of edges.

        """
        if curve.vertices is None or curve.parts is None:
            raise ValueError("Curve must have parts and vertices to find connections.")

        parts_id = curve.parts

        if data is not None and data.values is not None:
            values = data.values
        else:
            values = np.ones(curve.vertices.shape[0])

        # out_labels = np.zeros(curve.n_cells).astype("int32")

        for label in np.unique(values):
            ind = values == label

            path = find_curves(
                curve.vertices[ind, :2],
                parts_id[ind],
                detection.min_edges,
                detection.max_distance,
                detection.damping,
            )

        return curve.vertices, path

    @property
    def params(self) -> Parameters:
        """Application parameters."""
        return self._params

    @params.setter
    def params(self, val: Parameters):
        if not isinstance(val, Parameters):
            raise TypeError("Parameters must be of type Parameters.")
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
    ifile = InputFile.read_ui_json(file)

    driver = PartsConnectionDriver(ifile)
    driver.run()
