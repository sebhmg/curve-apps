#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of edge-detection package.
#
#  All rights reserved.
#
#
#  This file is part of curve-apps.
#
#  curve-apps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from geoapps_utils.driver.data import BaseData
from geoh5py.data import FloatData
from geoh5py.objects import Grid2D
from pydantic import BaseModel, ConfigDict

from curve_apps import assets_path


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
    :param merge_length: Minimum length between nodes that should be merged.
    """

    line_length: int = 1
    line_gap: int = 1
    sigma: float = 10
    threshold: int = 1
    window_size: int | None = None
    merge_length: float | None = None


class OutputParameters(BaseModel):
    """
    Output parameters expected by the ui.json file format.

    :param export_as: Name of the output entity.
    :param out_group: Name of the output group.
    """

    export_as: str | None = "edges"
    out_group: str | None = "detections"


class Parameters(BaseData):
    """
    Edge detection input parameters.

    :param detection: Detection parameters expected for the edge detection.
    :param source: Parameters for the source object and data.
    """

    name: ClassVar[str] = "edge_detection"
    default_ui_json: ClassVar[Path] = assets_path() / "uijson/edge_detection.ui.json"
    title: ClassVar[str] = "Edge Detection"
    run_command: ClassVar[str] = "curve_apps.edge_detection.driver"

    source: SourceParameters
    detection: DetectionParameters
    output: OutputParameters
