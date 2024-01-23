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

from typing import Optional, Union

from geoh5py.data import Data, ReferencedData
from geoh5py.objects import Curve, Points
from pydantic import BaseModel, ConfigDict

from ..params import BaseParameters, OutputParameters


class Parameters(BaseParameters):
    """
    Parts connection input parameters.

    :param detection: Detection parameters expected for the parts connection.
    :param source: Parameters for the source object and data parameters.
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

    :param entity: A Curve or Points source object.
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
