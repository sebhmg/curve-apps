Edge Detection
==============

With this application, users can create lines along edges (lineaments)
from gridded data in a semi-automated fashion. The application uses
machine vision algorithms from the
`Scikit-Image <https://scikit-image.org/>`__ open-source package. Edges are exported to `Geoscience ANALYST <https://mirageoscience.com/mining-industry-software/geoscience-analyst/>`__
for viewing and editing.


New user? Visit the `Getting Started <getting_started>`_ page.

Application
-----------

The following sections provide details on the different parameters exposed in the ``ui.json``.

.. figure:: ./images/edge_detection/edge_detection_ui.png
            :align: center
            :width: 300

Data Selection
^^^^^^^^^^^^^^

 - **Object**: Select the target ``Grid2D`` object from the dropdown list.
 - **Data**: Select the data attribute to use for edge detection.


Detection Parameters
^^^^^^^^^^^^^^^^^^^^

`Scikit-Image.feature.Canny <https://scikit-image.org/docs/dev/auto_examples/edges/plot_canny.html#sphx-glr-auto-examples-edges-plot-canny-py>`__
 - **Sigma**: Standard deviation of the Gaussian filter used to smooth the input data. Increase the parameter to detect fewer edges in noisy data.

`Scikit-Image.transform.probabilistic_hough_line <https://scikit-image.org/docs/dev/api/skimage.transform.html#probabilistic-hough-line>`__
 - **Line length**: Filter for the minimum length (pixels) of detected lines. Increase the parameter to extract longer lines.
 - **Line gap**: Maximum gap between pixels to still form a line. Increase the parameter to merge broken lines more aggressively.
 - **Threshold**: Threshold parameter used in the Hough Line Transform.


**[Optionals]**

 - **Window size**: Size of the square window used to sub-divide the grid for processing. By default, the window size
    is set to the shortest side of the input grid. Smaller window sizes can be used to speed up computations but may result in
    more fragmented lines. Larger window sizes can be used to improve line continuity but may slow down computations.
 - **Merge length**: Merge lines within a specified distance (in meters) of each other. This parameter is useful for
    merging fragmented lines that are close to each other but not connected.


Output preferences
^^^^^^^^^^^^^^^^^^

 - **Save as**: Assign a specific name to the resulting ``Curve`` object.
 - **Group**: Create a ``Container Group`` entity to store the results.


.. _edge_methodology:

Methodology
-----------

The conversion from raster data to lines involves the following four
main processing steps.

.. figure:: ./images/edge_detection/edge_detection_algo.png
            :align: center
            :width: 500

1. The selected gridded data are normalized between [0, 1]

2. Normalized values are processed with the
   `Canny <#Canny-Edge-Parameters>`__ detection algorithm to extract a binary edge map.

3. The full grid is sub-divided into overlapping **square tiles** defined by
   the `window size <#Window-size>`__ parameter. Tiling is used to speed
   up computations but to also avoid skewing the detection of lines along the longest axis of the input grid.

4. For each tile, edges are converted to a line parametric form using
   the `Hough Line Transform <#Hough-Line-Parameters>`__.

[Optional] The resulting vertices defining the segments can be filtered to reduce the number of unique lines. Collocated
vertices are merged if they are within a specified distance of each other. This is controlled by the `merge length <#Merge-Length>`__ parameter.


Example
-------


.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - No merge
     - With 75 m merge length
   * - .. figure:: ./images/edge_detection/no_merge_length.png
            :align: center
            :width: 300
     - .. figure:: ./images/edge_detection/merge_length.png
            :align: center
            :width: 300


Need help? Contact us at support@mirageoscience.com
