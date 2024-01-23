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

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

from geoh5py.ui_json import InputFile
from geoh5py.workspace import Workspace
from pydantic import BaseModel, ConfigDict


class BaseParameters(BaseModel, ABC):
    """
    Model surface input parameters.

    :param output: Optional parameters for the output.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    conda_environment: Optional[str] = "curve-apps"
    input_file: Optional[InputFile] = None
    geoh5: Workspace
    monitoring_directory: Optional[Union[str, Path]] = None
    output: OutputParameters
    run_command: str
    title: str
    workspace_geoh5: Optional[Workspace] = None

    @classmethod
    @abstractmethod
    def instantiate(cls, input_file: InputFile | dict) -> BaseParameters:
        """
        Instantiate the application.
        """

    @classmethod
    def _parse_input(cls, input_data: InputFile | dict) -> tuple:
        """
        Parse input parameter and values from ui.json data.

        :param input_data: Dictionary of parameters and values.

        :return: Dataclass of application parameters.
        """
        input_file = None
        if isinstance(input_data, InputFile) and input_data.data is not None:
            input_file = input_data
            data = input_data.data
        elif isinstance(input_data, dict):
            data = input_data
        else:
            raise TypeError("Input data must be a dictionary or InputFile.")

        return input_file, data

    def flatten(self) -> dict:
        """
        Flatten the parameters to a dictionary.

        :return: Dictionary of parameters.
        """
        param_dict = dict(self)
        out_dict = {}
        for key, value in param_dict.items():
            if isinstance(value, BaseModel):
                out_dict.update(dict(value))
            else:
                out_dict.update({key: value})

        out_dict.pop("input_file")
        return out_dict


class OutputParameters(BaseModel):
    """
    Output parameters expected by the ui.json file format.

    :param export_as: Name of the output entity.
    :param ga_group_name: Name of the output group.
    """

    export_as: Optional[str] = None
    out_group: Optional[str] = None
