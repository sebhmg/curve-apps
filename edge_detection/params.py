#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from geoh5py.data import FloatData
from geoh5py.objects import Grid2D
from geoh5py.ui_json import InputFile
from geoh5py.workspace import Workspace
from pydantic import BaseModel, ConfigDict


class ApplicationParameters(BaseModel):
    """
    Model surface input parameters.

    :param core: Core parameters expected by the ui.json file format.
    :param detection: Detection parameters expected for the edge detection.
    :param output: Optional parameters for the output.
    :param source: Parameters for the source object and data.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    conda_environment: Optional[str] = "curve-apps"
    detection: DetectionParameters
    input_file: Optional[InputFile] = None
    geoh5: Workspace
    monitoring_directory: Optional[Union[str, Path]] = None
    output: OutputParameters
    run_command: str = "geomodpy.model_from_surfaces"
    source: SourceParameters
    title: str = "Model from surfaces"
    workspace_geoh5: Optional[Workspace] = None

    @classmethod
    def parse_input(cls, input_data: InputFile | dict) -> ApplicationParameters:
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

        parameters = cls(
            **data,
            input_file=input_file,
            detection=DetectionParameters(**data),
            output=OutputParameters(**data),
            source=SourceParameters(**data),
        )

        return parameters

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

        return out_dict


class SourceParameters(BaseModel):
    """
    Source parameters expected by the ui.json file format.

    :param objects: A Grid2D source object.
    :param data: Data values to find edges on.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    objects: Grid2D
    data: FloatData


class DetectionParameters(BaseModel):
    """
    Detection parameters expected by the ui.json file format.

    :param line_length: Minimum accepted pixel length of detected lines. (Hough)
    :param line_gap: Maximum gap between pixels to still form a line. (Hough)
    :param sigma: Standard deviation of the Gaussian filter. (Canny)
    :param threshold: Value threshold. (Hough)
    :param window_size: Size of the window to search for lines.
    """

    line_length: int = 1
    line_gap: int = 1
    sigma: float = 10
    threshold: int = 1
    window_size: Optional[int] = None


class OutputParameters(BaseModel):
    """
    Output parameters expected by the ui.json file format.

    :param export_as: Name of the output entity.
    :param ga_group_name: Name of the output group.
    """

    export_as: Optional[str] = None
    out_group: Optional[str] = None
