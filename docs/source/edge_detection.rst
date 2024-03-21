Edge Detection
==============

With this application, users can create lines along edges (lineaments)
from gridded data in a semi-automated fashion. The application uses
machine vision algorithms from the
`Scikit-Image <https://scikit-image.org/>`__ open-source package.

-  Currently available for Grid2D objects.
-  Edges can be exported to `Geoscience
   ANALYST <https://mirageoscience.com/mining-industry-software/geoscience-analyst/>`__
   for viewing and editing.
-  See the `Methodology <#Methodology>`__ section for algorithmic
   details

`Video tutorial available on Youtube <https://youtu.be/Lpn3xA7xlBs>`__

New user? Visit the `Getting Started <../installation.rst>`__ page.

Application
-----------

The following sections provide details on the different parameters
controlling the application. Interactive widgets shown below are for
demonstration purposes only.


Input Data
----------

Object and Data Selection
~~~~~~~~~~~~~~~~~~~~~~~~~

List of ``Grid2D`` objects available in the target ``geoh5`` project.


Window selection
~~~~~~~~~~~~~~~~


Canny Edge Parameters
---------------------

Parameters controlling the
`Scikit-Image.feature.Canny <https://scikit-image.org/docs/dev/auto_examples/edges/plot_canny.html#sphx-glr-auto-examples-edges-plot-canny-py>`__
edge detection routine.

Sigma
~~~~~

Standard deviation of the Gaussian filter used in the Canny algorithm.


Hough Line Parameters
---------------------

Parameters controlling the
`Scikit-Image.transform.probabilistic_hough_line <https://scikit-image.org/docs/dev/api/skimage.transform.html#probabilistic-hough-line>`__
routine.

Threshold
~~~~~~~~~

Detection threshold


Line Length
~~~~~~~~~~~

Filter for the minimum length (pixels) of detected lines.


Line Gap
~~~~~~~~

Maximum gap between pixels to still form a line.


See the `Output Panel <base_application.ipynb#Output-Panel>`__ page for
more details.

Methodology
-----------

The conversion from raster data to lines involves the following four
main processing steps.

1. The selected gridded data are normalized between [0, 1]

2. Normalized values are processed with the
   `Canny <#Canny-Edge-Parameters>`__ edge detection algorithm.

3. The full grid is sub-divided into overlapping square tiles defined by
   the `window size <#Window-size>`__ parameter. Tiling is used to speed
   up computations and reduce skews in the Hough line parametrization
   observed on grids with small aspect ratios.

4. For each tile, edges are converted to a line parametric form using
   the `Hough Line Transform <#Hough-Line-Parameters>`__.

Need help? Contact us at support@mirageoscience.com
