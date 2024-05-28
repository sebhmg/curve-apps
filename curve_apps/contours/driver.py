# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024 Mira Geoscience Ltd.                                     '
#                                                                              '
#  This file is part of geoapps.                                               '
#                                                                              '
#  geoapps is distributed under the terms and conditions of the MIT License    '
#  (see LICENSE file at the root of this source code package).                 '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from __future__ import annotations

import logging
import sys

import matplotlib.pyplot as plt
from geoapps.utils.formatters import string_name
from geoh5py.groups import ContainerGroup
from geoh5py.objects import Grid2D
from geoh5py.ui_json import InputFile, utils

from curve_apps.contours.params import ContourParameters
from curve_apps.driver import BaseCurveDriver
from curve_apps.utils import contours_to_curve

logger = logging.getLogger(__name__)


class ContoursDriver(BaseCurveDriver):
    """
    Driver for the detection of contours within geoh5py objects.

    :param parameters: Application parameters.
    """

    _parameter_class = ContourParameters
    _default_name = "Contours"

    def __init__(self, parameters: ContourParameters | InputFile):
        super().__init__(parameters)

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

    def create_output(self, name, parent: ContainerGroup | None = None):
        """
        Run the application for extracting and creating contours from input object.

        :param name: Name of the output object.
        :param parent: Optional parent group.
        """

        with utils.fetch_active_workspace(self.workspace) as workspace:

            logger.info("Generating contours ...")
            contours = ContoursDriver.get_contours(self.params)
            curve = contours_to_curve(contours, self.params)
            out_entity = curve
            if self.params.output.out_group is not None:
                out_entity = ContainerGroup.create(
                    workspace, name=string_name(self.params.output.out_group)
                )
                curve.parent = out_entity

            self.update_monitoring_directory(out_entity)


if __name__ == "__main__":
    file = sys.argv[1]
    ifile = InputFile.read_ui_json(file)

    driver = ContoursDriver(ifile)
    driver.run()
