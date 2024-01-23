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


from curve_apps import __version__

default_ui_json = {
    "version": __version__,
    "title": "Parts Connection",
    "geoh5": "",
    "workspace_geoh5": "",
    "run_command": "curve_apps.edge_detection.driver",
    "monitoring_directory": "",
    "conda_environment": "curve_apps",
    "conda_environment_boolean": False,
    "objects": {
        "group": "Data Selection",
        "meshType": ["{48f5054a-1c5c-4ca4-9048-80f36dc60a06}"],
        "main": True,
        "label": "Object",
        "value": None,
    },
    "data": {
        "group": "Data Selection",
        "main": True,
        "association": ["Vertex"],
        "optional": True,
        "enabled": False,
        "dataType": "Float",
        "label": "Data",
        "parent": "objects",
        "value": None,
    },
    "min_edges": {
        "group": "Parameters",
        "main": True,
        "label": "Minimum edges",
        "min": 1,
        "max": 100,
        "value": 1,
    },
    "max_distance": {
        "group": "Parameters",
        "main": True,
        "optional": True,
        "enabled": False,
        "label": "Maximum distance:",
        "min": 1,
        "max": 100,
        "value": 1,
    },
    "damping": {
        "group": "Parameters",
        "main": True,
        "label": "Damping factor:",
        "value": 0.0,
        "min": 0.0,
        "precision": 1,
        "lineEdit": True,
        "max": 1.0,
    },
    "export_as": {
        "main": True,
        "optional": True,
        "enabled": False,
        "label": "Save as",
        "value": "",
        "group": "Python run preferences",
    },
    "out_group": {
        "main": True,
        "optional": True,
        "enabled": False,
        "label": "Group",
        "value": "",
        "group": "Python run preferences",
    },
}
