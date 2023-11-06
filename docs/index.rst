Auto Segmentation Step
======================

Overview
--------

The **Auto Segmentation** step is an interactive segmentation plugin for the MAP-Client.

This tool takes a stack of images as an input and uses the contours of these images to generate a set of 3D `Zinc` surface meshes.
Additionally, it also has the ability to generate a `Zinc` point cloud over the surface of the meshes. The **Auto Segmentation** step
outputs two `Zinc` compatible EX files corresponding with the generated meshes and point-cloud objects respectively.

Specification
-------------

Information on this plugin's specifications is available :ref:`here <mcp-autosegmentation-specification>`.

Configuration
-------------

Information on this plugin's configuration is available :ref:`here <mcp-autosegmentation-configuration>`.

Workflow Setup
--------------

Information on setting up a workflow with this plugin can be found :ref:`here <mcp-autosegmentation-workflow-setup>`.

Instructions
------------

When the tool loads for the first time you should see something like the image displayed in :numref:`fig-auto-segmentation-initial`.

.. _fig-auto-segmentation-initial:

.. figure:: _images/auto-segmentation-initial.png
   :figwidth: 100%
   :align: center

   **Auto Segmentation** user interface just after loading.

The view window visualises a box outlining the dimensions of the image stack. In this box you should see a plane showing the image at the
current level in the image stack, and a 3D surface showing the contours of the segmented image data.

The `Image Plane Level` slider can be used to cycle through the input images and can be helpful for determining a satisfactory threshold for
the segmentation contour graphics. The `Segmentation Contour Threshold` slider is used to set the image intensity threshold that the
segmentation contour graphics are created at. If the segmentation graphics look angular or rough, or if they are not initially visible, try
experimenting with the `Segmentation Contour Threshold` slider to adjust the shape of the surface:

.. _fig-auto-segmentation-threshold:

.. figure:: _images/auto-segmentation-threshold.png
   :figwidth: 100%
   :align: center

   Segmentation graphics after adjusting the `Segmentation Contour Threshold` slider.

You can further smooth out the surface graphics by adjusting the `Segmentation Tessellation Divisions`. This changes the number of
triangular elements that are created over the surface of the mesh, making it more or less smooth. Note that significantly increasing the
tessellation divisions will slow down the generation and visualisation of the surface graphics, so it is recommended that you only try this
after setting an adequate threshold value. Increasing the tessellation divisions beyond the dimensions of the image stack is not recommended
and is unlikely to improve the quality of the graphics.

Once you are satisfied with the shape of the segmentation mesh click `Generate Points` to generate a point cloud over its surface.

.. _fig-auto-segmentation-points:

.. figure:: _images/auto-segmentation-points.png
   :figwidth: 100%
   :align: center

   Points generated over the surface of the segmentation contour graphics.


You may adjust the segmentation settings and re-generate the point cloud as many time as necessary to achieve a result you are satisfied
with.

All user interface settings and generated graphics are saved and will be re-loaded the next time you start the **Auto Segmentation** tool.

Clicking the `Done` button will output the mesh and point cloud each to a `Zinc` EX file and will execute any additional workflow steps
connected to the **Auto Segmentation** step.
