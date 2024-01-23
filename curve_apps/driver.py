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

from abc import abstractmethod

from geoapps_utils.driver.driver import BaseDriver
from geoh5py.groups import Group
from geoh5py.objects import ObjectBase
from geoh5py.ui_json import InputFile

from .params import BaseParameters


class BaseCurveDriver(BaseDriver):
    """
    Driver for the edge detection application.

    :param parameters: Application parameters.
    """

    _parameter_class: type[BaseParameters]

    def __init__(self, parameters: BaseParameters | InputFile):
        if isinstance(parameters, InputFile):
            parameters = self._parameter_class.instantiate(parameters)

        # TODO need to re-type params in base class
        super().__init__(parameters)

    @abstractmethod
    def run(self):
        """
        Run method of the driver.
        """

    @property
    def params(self) -> BaseParameters:
        """Application parameters."""
        return self._params

    @params.setter
    def params(self, val: BaseParameters):
        if not isinstance(val, BaseParameters):
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
