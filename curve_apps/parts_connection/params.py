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

from pathlib import Path
from typing import Optional, Union

from geoh5py.data import Data, ReferencedData
from geoh5py.objects import Curve, Points
from geoh5py.ui_json import InputFile
from geoh5py.workspace import Workspace
from pydantic import BaseModel, ConfigDict


class Parameters(BaseModel):
    """
    Parts connection input parameters.

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
    def parse_input(cls, input_data: InputFile | dict) -> Parameters:
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

        out_dict.pop("input_file")
        return out_dict


class SourceParameters(BaseModel):
    """
    Source parameters expected by the ui.json file format.

    :param entity: A Grid2D source object.
    :param data: Data values to find edges on.
    :param parts: Optional parts to connect.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    entity: Union[Curve, Points]
    data: Optional[ReferencedData] = None
    parts: Optional[Data] = None


class DetectionParameters(BaseModel):
    """
    Detection parameters expected by the ui.json file format.

    :param min_edges: Minimum number of points in a curve.
    :param max_distance: Maximum distance between points in a curve.
    :param damping: Damping factor between [0, 1] for the path roughness.
    """

    min_edges: int = 1
    max_distance: Optional[float] = None
    damping: float = 0


class OutputParameters(BaseModel):
    """
    Output parameters expected by the ui.json file format.

    :param export_as: Name of the output entity.
    :param out_group: Name of the output group.
    """

    export_as: Optional[str] = None
    out_group: Optional[str] = None
