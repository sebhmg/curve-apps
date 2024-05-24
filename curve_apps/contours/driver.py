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

import numpy as np
from geoapps.utils.formatters import string_name
from geoapps.utils.plotting import plot_plan_data_selection
from geoh5py.groups import ContainerGroup
from geoh5py.objects import Grid2D
from geoh5py.ui_json import InputFile, utils
from matplotlib.pyplot import axes
import matplotlib.pyplot as plt

from curve_apps.contours.params import Parameters
from curve_apps.driver import BaseCurveDriver
from curve_apps.utils import contours_to_curve

logger = logging.getLogger(__name__)


class ContoursDriver(BaseCurveDriver):
    """
    Driver for the detection of contours withing geoh5py objects.

    :param parameters: Application parameters.
    """

    _parameter_class = Parameters
    _default_name = "Contours"

    def __init__(self, parameters: Parameters | InputFile):
        super().__init__(parameters)

    @staticmethod
    def get_contours(params: Parameters):

        entity = params.source.objects
        data = params.source.data
        locations = getattr(entity, "vertices", None) or entity.centroids
        x, y = locations[:, :2].T
        axis = plt.axes()
        if isinstance(entity, Grid2D):
            contours = axis.contour(
                x, y, data.values, levels=params.detection.contours
            )
        else:
            contours = axis.tricontour(
                x, y, data.values,levels=params.detection.contours,
            )
        return contours


    def create_output(self, name, parent: ContainerGroup | None = None):
        """
        Run the application for extracting and creating contours from input object.

        :param name: Name of the output object.
        :param parent: Optional parent group.
        """

        with utils.fetch_active_workspace(self.workspace) as workspace:
            entity = self.params.source.objects

            print("Generating contours . . .")
            contours = ContoursDriver.get_contours(self.params)

            if contours is not None:
                curve, values = contours_to_curve(entity, contours, self.params.output)
                out_entity = curve
                if len(self.params.ga_group_name) > 0:
                    out_entity = ContainerGroup.create(
                        workspace, name=string_name(self.params.ga_group_name)
                    )
                    curve.parent = out_entity

                curve.add_data(
                    {self.params.detection.contour_string: {"values": np.hstack(values)}}
                )
                self.update_monitoring_directory(out_entity)


# class ContoursDriver(BaseDriver):
#     _params_class = ContoursParams
#     _validations = validations
#
#     def __init__(self, params: ContoursParams):
#         super().__init__(params)
#         self.params: ContoursParams = params
#         self._unique_object = {}
#
#     def run(self):
#         workspace = self.params.geoh5
#         entity = self.params.objects
#         data = self.params.data
#
#         contours = get_contours(
#             self.params.interval_min,
#             self.params.interval_max,
#             self.params.interval_spacing,
#             self.params.fixed_contours,
#         )
#
#         print("Generating contours . . .")
#         _, _, _, _, contour_set = plot_plan_data_selection(
#             entity,
#             data,
#             axis=axes(),
#             resolution=self.params.resolution,
#             window=self.params.window,
#             contours=contours,
#         )
#
#         if contour_set is not None:
#             vertices, cells, values = [], [], []
#             count = 0
#             for segs, level in zip(contour_set.allsegs, contour_set.levels):
#                 for poly in segs:
#                     n_v = len(poly)
#                     vertices.append(poly)
#                     cells.append(
#                         np.c_[
#                             np.arange(count, count + n_v - 1),
#                             np.arange(count + 1, count + n_v),
#                         ]
#                     )
#                     values.append(np.ones(n_v) * level)
#                     count += n_v
#             if vertices:
#                 vertices = np.vstack(vertices)
#                 if self.params.z_value:
#                     vertices = np.c_[vertices, np.hstack(values)]
#                 else:
#                     if isinstance(entity, (Points, Curve, Surface)):
#                         z_interp = LinearNDInterpolator(
#                             entity.vertices[:, :2], entity.vertices[:, 2]
#                         )
#                         vertices = np.c_[vertices, z_interp(vertices)]
#                     else:
#                         vertices = np.c_[
#                             vertices,
#                             np.ones(vertices.shape[0]) * entity.origin["z"],
#                         ]
#
#             curve = Curve.create(
#                 workspace,
#                 name=string_name(self.params.export_as),
#                 vertices=vertices,
#                 cells=np.vstack(cells).astype("uint32"),
#             )
#             out_entity = curve
#             if len(self.params.ga_group_name) > 0:
#                 out_entity = ContainerGroup.create(
#                     workspace, name=string_name(self.params.ga_group_name)
#                 )
#                 curve.parent = out_entity
#
#             curve.add_data(
#                 {
#                     self.get_contour_string(
#                         self.params.interval_min,
#                         self.params.interval_max,
#                         self.params.interval_spacing,
#                         self.params.fixed_contours,
#                     ): {"values": np.hstack(values)}
#                 }
#             )
#             self.update_monitoring_directory(out_entity)
#             workspace.close()
#
#     @staticmethod
#     def get_contour_string(min_val, max_val, step, fixed_contours):
#         if type(fixed_contours) is list:
#             fixed_contours = str(fixed_contours).replace("[", "").replace("]", "")
#
#         contour_string = str(min_val) + ":" + str(max_val) + ":" + str(step)
#
#         if fixed_contours is not None:
#             contour_string += "," + str(fixed_contours.replace(" ", ""))
#
#         return contour_string


if __name__ == "__main__":
    file = sys.argv[1]
    ifile = InputFile.read_ui_json(file)

    driver = ContoursDriver(ifile)
    driver.run()