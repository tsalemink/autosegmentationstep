Auto Segmentation Step
======================

The **Auto Segmentation** step is an interactive segmentation plugin for the MAP-Client.
The MAP Client is a workflow management application written in Python.
It can be found at https://github.com/MusculoskeletalAtlasProject/mapclient.

This tool takes a stack of images as an input and uses the contours of these images to generate a 3D *Zinc* surface mesh. Additionally, it
also has the ability to generate a *Zinc* point cloud over the surface of the mesh. The **Auto Segmentation** step outputs a *Zinc*
compatible EX file containing the generated mesh and point-cloud objects.

Please refer to the plugin documentation for details on how to set up and run this tool.
