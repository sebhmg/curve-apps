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

from typing import Optional

from geoh5py.data import FloatData
from geoh5py.objects import Grid2D
from pydantic import BaseModel, ConfigDict

from ..params import BaseParameters, OutputParameters


class Parameters(BaseParameters):
    """
    Model surface input parameters.

    :param detection: Detection parameters expected for the edge detection.
    :param source: Parameters for the source object and data.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    detection: DetectionParameters
    run_command: str = "geomodpy.model_from_surfaces"
    source: SourceParameters
    title: str = "Model from surfaces"

    @classmethod
    def instantiate(cls, input_file) -> BaseParameters:
        """
        Instantiate the application.
        """
        input_file, data = cls._parse_input(input_file)
        parameters = cls(
            **data,
            input_file=input_file,
            detection=DetectionParameters(**data),
            output=OutputParameters(**data),
            source=SourceParameters(**data),
        )

        return parameters


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
