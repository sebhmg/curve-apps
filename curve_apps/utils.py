#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of edge-detection package.
#
#  All rights reserved.
#

from __future__ import annotations

import numpy as np
from scipy.spatial import Delaunay

from curve_apps.trend_lines.params import DetectionParameters


def find_curves(
    vertices: np.ndarray,
    parts: np.ndarray,
    params: DetectionParameters = DetectionParameters(),
) -> list[list[list[float]]]:
    """
    Find curves in a set of points.

    :param vertices: Vertices for points.
    :param parts: Identifier for points belong to common parts.
    :param params: Trend line detection parameters.

    :return: List of curves.
    """
    tri = Delaunay(vertices, qhull_options="QJ")
    if tri.simplices is None:  # pylint: disable=no-member
        return []

    simplices: np.ndarray = tri.simplices  # pylint: disable=no-member

    edges = np.vstack(
        (
            simplices[:, :2],
            simplices[:, 1:],
            simplices[:, ::2],
        )
    )
    edges = np.sort(edges, axis=1)
    edges = np.unique(edges, axis=0)
    distances = np.linalg.norm(vertices[edges[:, 0]] - vertices[edges[:, 1]], axis=1)
    distance_sort = np.argsort(distances)
    edges, distances = edges[distance_sort, :], distances[distance_sort]

    if params.max_distance is not None:
        edges = edges[distances <= params.max_distance, :]

    # Reject edges with same vertices id
    edge_parts = parts[edges]
    edges = edges[edge_parts[:, 0] != edge_parts[:, 1]]

    if params.azimuth is not None and params.azimuth_tol is not None:
        ind = filter_segments_orientation(
            vertices, edges, params.azimuth, params.azimuth_tol
        )
        edges = edges[ind]

    # Walk edges until no more edges can be added
    mask = np.ones(vertices.shape[0], dtype=bool)
    out_curves = []

    for ind in range(edges.shape[0]):
        if not np.any(mask[edges[ind]]):
            continue

        mask[edges[ind]] = False
        path = [edges[ind]]
        path, mask = walk_edges(
            path, edges[ind], edges, vertices, params.damping, mask=mask
        )
        path, mask = walk_edges(
            path, edges[ind][::-1], edges, vertices, params.damping, mask=mask
        )
        if len(path) < params.min_edges:
            continue

        out_curves.append(path)

    return out_curves


def walk_edges(  # pylint: disable=too-many-arguments
    path: list,
    incoming: list,
    edges: np.ndarray,
    vertices: np.ndarray,
    damping: float = 0.0,
    mask: np.ndarray | None = None,
) -> tuple[list, np.ndarray]:
    """
    Find all edges connected to a point.

    :param path: Current list of edges forming a path.
    :param incoming: Incoming edge.
    :param edges: All edges.
    :param vertices: Direction of the edges.
    :param damping: Damping factor between [0, 1] for the path roughness.
    :param mask: Mask for nodes that have already been visited.

    :return: Edges connected to point.
    """
    if mask is None:
        mask = np.ones(edges.max() + 1, dtype=bool)
        mask[np.hstack(path).flatten()] = False

    if damping < 0 or damping > 1:
        raise ValueError("Damping must be between 0 and 1.")

    neighbours = np.where(
        np.any(edges == incoming[1], axis=1) & np.any(mask[edges], axis=1)
    )[0]

    if len(neighbours) == 0:
        return path, mask

    # Outgoing candidate nodes
    candidates = edges[neighbours][edges[neighbours] != incoming[1]]

    vectors = vertices[candidates, :] - vertices[incoming[1], :]
    in_vec = np.diff(vertices[incoming, :], axis=0).flatten()
    dot = np.dot(in_vec, vectors.T)

    if not np.any(dot > 0):
        return path, mask

    # Remove backward vectors
    vectors = vectors[dot > 0, :]
    candidates = candidates[dot > 0]
    dot = dot[dot > 0]

    # Compute the angle between the incoming vector and the outgoing vectors
    vec_lengths = np.linalg.norm(vectors, axis=1)
    angle = np.arccos(dot / (np.linalg.norm(in_vec) * vec_lengths) - 1e-10)

    # Minimize the torque
    sub_ind = np.argmin(angle ** (1 - damping) * vec_lengths)
    outgoing = [incoming[1], candidates[sub_ind]]
    mask[candidates[sub_ind]] = False
    path.append(outgoing)

    # Continue walking
    path, mask = walk_edges(path, outgoing, edges, vertices, damping, mask=mask)

    return path, mask


def filter_segments_orientation(
    vertices: np.ndarray, edges: np.ndarray, azimuth: float, azimuth_tol: float
):
    """
    Filter segments orientation.

    :param vertices: Vertices for points.
    :param edges: Edges for points.
    :param azimuth: Filter angle (degree) on segments orientation, clockwise from North.
    :param azimuth_tol: Tolerance (degree) on the azimuth.

    :return: Array of boolean.
    """
    vectors = vertices[edges[:, 1], :] - vertices[edges[:, 0], :]
    test_vector = np.array([np.sin(np.deg2rad(azimuth)), np.cos(np.deg2rad(azimuth))])

    angles = np.arccos(np.dot(vectors, test_vector) / np.linalg.norm(vectors, axis=1))

    return np.logical_or(
        np.abs(angles) < np.deg2rad(azimuth_tol),
        np.abs(angles - np.pi) < np.deg2rad(azimuth_tol),
    )
