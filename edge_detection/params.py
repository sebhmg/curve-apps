#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from __future__ import annotations

from pathlib import Path

from geoh5py.data import FloatData
from geoh5py.objects import Grid2D
from geoh5py.workspace import Workspace
from pydantic import BaseModel


class ApplicationParameters(BaseModel):
    """
    Model surface input parameters.

    :param core: Core parameters expected by the ui.json file format.
    :param detection: Detection parameters expected for the edge detection.
    :param output: Optional parameters for the output.
    :param source: Parameters for the source object and data.
    """

    core: UIJsonParameters
    detection: DetectionParameters
    output: OutputParameters
    source: SourceParameters

    @classmethod
    def parse_input_data(cls, data: dict) -> ApplicationParameters:
        """
        Parse input parameter and values from ui.json data.

        :param data: Dictionary of parameters and values.

        :return: Dataclass of application parameters.
        """
        workspace = data.get("geoh5")

        if workspace is None:
            raise UserWarning("No workspace found in input data.")

        parameters = cls(
            core=UIJsonParameters(**data),
            detection=DetectionParameters(**data),
            output=OutputParameters(**data),
            source=SourceParameters(**data),
        )

        return parameters


class UIJsonParameters(BaseModel):
    """
    Core parameters expected by the ui.json file format.

    :param conda_environment: Conda environment used to run run_command.
    :param geoh5: Current workspace path.
    :param monitoring_directory: Path to monitoring directory, where .geoh5 files
        are automatically processed by GA.
    :param run_command: Command to run the application through GA.
    :param title: Application title.
    :param workspace_geoh5: Path of the source .geoh5 file where the ui.json was created.
    """

    monitoring_directory: str | Path | None = None
    workspace_geoh5: Workspace | None = None
    geoh5: Workspace
    title: str = "Model from surfaces"
    run_command: str = "geomodpy.model_from_surfaces"
    conda_environment: str | None = "geomodpy"


class SourceParameters(BaseModel):
    """
    Source parameters expected by the ui.json file format.

    :param objects: A Grid2D source object.
    :param data: Data values to find edges on.
    """

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

    line_length: int
    line_gap: int
    sigma: float
    threshold: int
    window_size: int | None = None


class OutputParameters(BaseModel):
    """
    Output parameters expected by the ui.json file format.

    :param export_as: Name of the output entity.
    :param ga_group_name: Name of the output group.
    """

    export_as: str | None
    out_group: str | None
