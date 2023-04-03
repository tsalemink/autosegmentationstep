import os
import re

from PySide6 import QtCore, QtOpenGLWidgets

from opencmiss.zinc.context import Context
from opencmiss.zinc.sceneviewer import Sceneviewer, Sceneviewerevent
from opencmiss.zinc.sceneviewerinput import Sceneviewerinput
from opencmiss.zinc.field import Field, FieldImage
from opencmiss.zinc.element import Element, Elementbasis
from opencmiss.zinc.glyph import Glyph


button_map = {
    QtCore.Qt.MouseButton.LeftButton: Sceneviewerinput.BUTTON_TYPE_LEFT,
    QtCore.Qt.MouseButton.MiddleButton: Sceneviewerinput.BUTTON_TYPE_MIDDLE,
    QtCore.Qt.MouseButton.RightButton: Sceneviewerinput.BUTTON_TYPE_RIGHT
}


def modifier_map(qt_modifiers):
    """
    Return a Zinc SceneViewerInput modifiers object that is created from the Qt modifier flags passed in.
    """
    modifiers = Sceneviewerinput.MODIFIER_FLAG_NONE
    if qt_modifiers & QtCore.Qt.KeyboardModifier.ShiftModifier:
        modifiers = modifiers | Sceneviewerinput.MODIFIER_FLAG_SHIFT

    return modifiers


def try_int(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return s


def alphanum_key(s):
    """
    Turn a string into a list of string and number chunks.
    "z23a" -> ["z", 23, "a"]
    """
    return [try_int(c) for c in re.split('([0-9]+)', s)]


class ZincScene(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        """
        Call the super class init functions, create a Zinc context and set the scene viewer handle to None.
        """
        QtOpenGLWidgets.QOpenGLWidget.__init__(self, parent)

        self._context = Context("autosegmenter")

        self._scene_viewer = None
        self._scene_viewer_notifier = None
        self._image_data_location = None

        self._image_field = None
        self._segmented_field = None
        self._segmented_image_field = None
        self._smooth_field = None
        self._scalar_field = None

        self._material = None
        self._segmentation_contour = None
        self._point_cloud = None
        self._point_cloud_region = None
        self._iso_graphic = None

        self._node_set = None
        self._output_coordinates = None
        self._graphics_filter = None

    def set_image_data_location(self, image_data_location):
        self._image_data_location = image_data_location

    def get_point_cloud(self):
        point_cloud = []
        field_module = self._point_cloud_region.getFieldmodule()
        field_module.beginChange()
        field_cache = field_module.createFieldcache()
        coordinate_field = field_module.findFieldByName('coordinates')
        nodeset = field_module.findNodesetByName('nodes')
        template = nodeset.createNodetemplate()
        template.defineField(coordinate_field)

        node_iterator = nodeset.createNodeiterator()
        node = node_iterator.next()
        while node.isValid():
            field_cache.setNode(node)
            position = coordinate_field.evaluateReal(field_cache, 3)[1]
            node = node_iterator.next()
            point_cloud.append(position)

        field_module.endChange()

        return point_cloud

    def set_image_plane_visibility(self, state):
        self._iso_graphic.setVisibilityFlag(state != 0)

    def set_segmentation_visibility(self, state):
        self._segmentation_contour.setVisibilityFlag(state != 0)

    def set_point_cloud_visibility(self, state):
        self._point_cloud.setVisibilityFlag(state != 0)

    def initializeGL(self):
        if self._scene_viewer is None:
            # From the context get the default scene viewer module.
            scene_viewer_module = self._context.getSceneviewermodule()
            self._scene_viewer = scene_viewer_module.createSceneviewer(Sceneviewer.BUFFERING_MODE_DOUBLE, Sceneviewer.STEREO_MODE_MONO)

            # Create a filter for visibility flags which will allow us to see our graphic.
            self._graphics_filter = self._context.getScenefiltermodule().createScenefilterVisibilityFlags()
            self._scene_viewer.setScenefilter(self._graphics_filter)
            root_region = self._context.getDefaultRegion()
            scene = root_region.getScene()

            self.define_standard_glyphs()
            self.define_standard_materials()

            # Once the renditions have been enabled for a region tree you can get a valid
            # handle for a rendition and create graphics for it.
            tessellation_module = self._context.getTessellationmodule()
            tessellation = tessellation_module.createTessellation()
            tessellation.setMinimumDivisions([64])
            #             tessellation_module.setDefaultTessellation(tessellation)

            # We use the beginChange and endChange to wrap any immediate changes and streamline the rendering of the scene.
            scene.beginChange()

            # Visualise images
            self.create_finite_elements(root_region)
            self.create_material_using_image_field()

            field_module = root_region.getFieldmodule()
            xi_field = field_module.findFieldByName('xi')
            finite_element_field = field_module.findFieldByName('coordinates')
            self._segmented_image_field = field_module.createFieldImageFromSource(self._segmented_field)

            # Visualise the outline.
            self._create_outline_graphics(scene, finite_element_field)

            self._segmentation_contour = scene.createGraphicsContours()
            self._segmentation_contour.setCoordinateField(xi_field)
            self._segmentation_contour.setTessellation(tessellation)

            self._segmentation_contour.setIsoscalarField(self._image_field)
            self._segmentation_contour.setListIsovalues([0.0])

            self._node_set, self._output_coordinates = self.setup_output_region(root_region)

            # Set the scene to our scene viewer.
            self.create_surface_graphics(root_region)
            self._scene_viewer.setScene(scene)

            scene.endChange()

            self._scene_viewer.viewAll()

            self._scene_viewer_notifier = self._scene_viewer.createSceneviewernotifier()
            self._scene_viewer_notifier.setCallback(self._zinc_scene_viewer_event)

    def define_standard_glyphs(self):
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()

    def define_standard_materials(self):
        material_module = self._context.getMaterialmodule()
        material_module.defineStandardMaterials()

    def _create_outline_graphics(self, scene, finite_element_field):
        scene.beginChange()
        outline = scene.createGraphicsLines()
        outline.setCoordinateField(finite_element_field)
        outline.setName('element_outline')
        scene.endChange()

        return outline

    def setup_output_region(self, root_region):
        self._point_cloud_region = root_region.createChild('output')
        field_module = self._point_cloud_region.getFieldmodule()
        finite_element_field = field_module.createFieldFiniteElement(3)
        # Set the name of the field, we give it label to help us understand it's purpose
        finite_element_field.setName('coordinates')
        # Set the attribute is managed to 1 so the field module will manage the field for us
        finite_element_field.setManaged(True)

        nodeset = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)

        scene = self._point_cloud_region.getScene()
        self._point_cloud = scene.createGraphicsPoints()
        self._point_cloud.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        self._point_cloud.setCoordinateField(finite_element_field)
        attributes = self._point_cloud.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize([0.01])

        return nodeset, finite_element_field

    def generate_points(self):
        self._node_set.destroyAllNodes()
        self.set_image_plane_visibility(0)
        scene = self._context.getDefaultRegion().getScene()
        scene.convertToPointCloud(self._graphics_filter, self._node_set, self._output_coordinates, 0.0, 0.0, 10000.0, 1.0)
        self.set_image_plane_visibility(1)

    def create_surface_graphics(self, region):
        """
        To visualize the 3D finite element that we have created for each _surface_region, we use a
        surface graphic then set a _material for that surface to use.
        """
        scene = region.getScene()
        # we iterate over the regions that we kept a handle to and use an index to get a
        # matching list of graphic _material names
        # for i, _surface_region in enumerate(self.regions_):
        field_module = region.getFieldmodule()

        finite_element_field = field_module.findFieldByName('coordinates')

        # Create three isosurface planes in the x, y and z directions whose positions in the texture block
        # can be altered using sliders
        # ## x component
        self._iso_graphic = scene.createGraphicsContours()
        self._iso_graphic.setCoordinateField(finite_element_field)
        self._iso_graphic.setMaterial(self._material)
        xi_field = field_module.findFieldByName('xi')
        self._iso_graphic.setTextureCoordinateField(xi_field)
        # set the yz scalar field to our isosurface
        self._iso_graphic.setIsoscalarField(self._scalar_field)
        # define the initial position of the isosurface on the texture block
        self._iso_graphic.setListIsovalues([0.0])

    def create_material_using_image_field(self):
        """
        Use an image field in a grpahics material to create a n OpenGL texture
        """
        # create a graphics material from the graphics module, assign it a name
        # and set flag to true
        material_module = self._context.getMaterialmodule()
        self._material = material_module.createMaterial()
        self._material.setName('texture_block')
        #        self._material.setManaged(True)

        # Get a handle to the root _surface_region
        root_region = self._context.getDefaultRegion()

        # The field module allows us to create a field image to
        # store the image data into.
        field_module = root_region.getFieldmodule()
        #         xi_field = field_module.findFieldByName('coordinates')
        # Create an image field. A temporary xi source field is created for us.
        self._image_field = field_module.createFieldImage()  # FromSource(xi_field)
        #        self._image_field.setName('image_field')

        self._image_field.setFilterMode(FieldImage.FILTER_MODE_LINEAR)
        self._image_field.setWrapMode(FieldImage.WRAP_MODE_CLAMP)

        # Create a stream information object that we can use to read the
        # image file from disk
        stream_information = self._image_field.createStreaminformationImage()
        # specify depth of texture block i.e. number of images
        #        stream_information.setAttributeInteger(stream_information.IMAGE_ATTRIBUTE_, self.number_of_images)

        # Load images onto an invidual texture blocks.
        directory = self._image_data_location.location()
        files = os.listdir(directory)
        files.sort(key=alphanum_key)
        for filename in files:
            if filename not in ['.hg', 'annotation.rdf']:
                # We are reading in a file from the local disk so our resource is a file.
                string_name = str(os.path.join(directory, filename))
                stream_information.createStreamresourceFile(string_name)

        # Actually read in the image file into the image field.
        self._image_field.read(stream_information)
        self._material.setTextureField(1, self._image_field)

        self._smooth_field = field_module.createFieldImagefilterCurvatureAnisotropicDiffusion(self._image_field, 0.0625,
                                                                                              2, 5)
        self._segmented_field = field_module.createFieldImagefilterConnectedThreshold(self._smooth_field, 0.2, 1.0, 1,
                                                                                      1, [0.5, 0.6111, 0.3889])

    def _zinc_scene_viewer_event(self, event):
        """
        Process a scene viewer event.  The updateGL() method is called for a
        repaint required event all other events are ignored.
        """
        if event.getChangeFlags() & Sceneviewerevent.CHANGE_FLAG_REPAINT_REQUIRED:
            QtCore.QTimer.singleShot(0, self.update)

    def set_slider_value(self, value):
        self._iso_graphic.setListIsovalues([value / 100.0])

    def set_segmentation_value(self, value):
        self._segmentation_contour.setListIsovalues([value / 10000.0])

    def create_finite_elements(self, region):
        """
        Create finite element meshes for each of the images
        """
        # Define the coordinates for each 3D element
        #        node_coordinate_set = [[0, 0, 0], [101, 0, 0], [0, 0, 52.0], [101, 0, 52.0], [0, 109, 0], [101, 109, 0], [0, 109, 52.0], [101, 109, 52.0]]
        #        a , b, c = 53.192, 49.288, 36.4
        #        node_coordinate_set = [[a, 0, 0], [a, 0, c], [0, 0, 0], [0, 0, c], [a, b, 0], [a, b, c], [0, b, 0], [0, b, c]]
        #        a , b, c = 101, 109, 52
        field_module = region.getFieldmodule()
        field_module.beginChange()

        # Create a finite element field with 3 components to represent 3 dimensions
        finite_element_field = field_module.createFieldFiniteElement(3)

        # Set the name of the field
        finite_element_field.setName('coordinates')
        # Set the attribute is managed to 1 so the field module will manage the field for us
        finite_element_field.setManaged(True)
        finite_element_field.setTypeCoordinate(True)

        a, b, c = 1, 1, 1
        node_coordinate_set = [[0, 0, 0], [a, 0, 0], [0, b, 0], [a, b, 0], [0, 0, c], [a, 0, c], [0, b, c], [a, b, c]]
        create_3d_finite_element(field_module, finite_element_field, node_coordinate_set)

        self._scalar_field = field_module.createFieldComponent(finite_element_field, 3)

        field_module.defineAllFaces()

        field_module.endChange()

    def paintGL(self):
        """
        Render the scene for this scene viewer.  The QGLWidget has already set up the
        correct OpenGL buffer for us so all we need do is render into it.  The scene viewer
        will clear the background so any OpenGL drawing of your own needs to go after this
        API call.
        """
        self._scene_viewer.renderScene()
        # paintGL end

    # resizeGL start
    def resizeGL(self, width, height):
        """
        Respond to widget resize events.
        """
        self._scene_viewer.setViewportSize(width, height)
        # resizeGL end

    def mousePressEvent(self, event):
        """
        Inform the scene viewer of a mouse press event.
        """
        scene_input = self._scene_viewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_PRESS)
        scene_input.setButtonType(button_map[event.button()])
        scene_input.setModifierFlags(modifier_map(event.modifiers()))

        self._scene_viewer.processSceneviewerinput(scene_input)

    def mouseReleaseEvent(self, event):
        """
        Inform the scene viewer of a mouse release event.
        """
        scene_input = self._scene_viewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
        scene_input.setButtonType(button_map[event.button()])

        self._scene_viewer.processSceneviewerinput(scene_input)

    def mouseMoveEvent(self, event):
        """
        Inform the scene viewer of a mouse move event and update the OpenGL scene to reflect this
        change to the viewport.
        """

        scene_input = self._scene_viewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_MOTION_NOTIFY)
        if event.type() == QtCore.QEvent.Type.Leave:
            scene_input.setPosition(-1, -1)

        self._scene_viewer.processSceneviewerinput(scene_input)


def create_3d_finite_element(fieldmodule, finite_element_field, node_coordinate_set):
    """
    Create a single finite element using the supplied
    finite element field and node coordinate set.
    """
    # Find a special node set named 'nodes'
    nodeset = fieldmodule.findNodesetByName('nodes')
    node_template = nodeset.createNodetemplate()

    # Set the finite element coordinate field for the nodes to use
    node_template.defineField(finite_element_field)
    field_cache = fieldmodule.createFieldcache()

    node_identifiers = []
    # Create eight nodes to define a cube finite element
    for node_coordinate in node_coordinate_set:
        node = nodeset.createNode(-1, node_template)
        node_identifiers.append(node.getIdentifier())
        # Set the node coordinates, first set the field cache to use the current node
        field_cache.setNode(node)
        # Pass in floats as an array
        finite_element_field.assignReal(field_cache, node_coordinate)

    # Use a 3D mesh to to create the 3D finite element.
    mesh = fieldmodule.findMeshByDimension(3)
    element_template = mesh.createElementtemplate()
    element_template.setElementShapeType(Element.SHAPE_TYPE_CUBE)
    element_node_count = 8
    element_template.setNumberOfNodes(element_node_count)
    # Specify the dimension and the interpolation function for the element basis function
    linear_basis = fieldmodule.createElementbasis(3, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    # the indecies of the nodes in the node template we want to use.
    node_indexes = [1, 2, 3, 4, 5, 6, 7, 8]

    # Define a nodally interpolated element field or field component in the
    # element_template
    element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

    for i, node_identifier in enumerate(node_identifiers):
        node = nodeset.findNodeByIdentifier(node_identifier)
        element_template.setNode(i + 1, node)

    mesh.defineElement(-1, element_template)
