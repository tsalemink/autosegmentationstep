import os, re

from PySide6 import QtCore, QtOpenGLWidgets

from opencmiss.zinc.context import Context
from opencmiss.zinc.sceneviewer import Sceneviewer, Sceneviewerevent
from opencmiss.zinc.sceneviewerinput import Sceneviewerinput
from opencmiss.zinc.field import Field, FieldImage
from opencmiss.zinc.element import Element, Elementbasis
from opencmiss.zinc.glyph import Glyph

# mapping from qt to zinc start
# Create a button map of Qt mouse buttons to Zinc input buttons
button_map = {QtCore.Qt.LeftButton: Sceneviewerinput.BUTTON_TYPE_LEFT,
              QtCore.Qt.MiddleButton: Sceneviewerinput.BUTTON_TYPE_MIDDLE,
              QtCore.Qt.RightButton: Sceneviewerinput.BUTTON_TYPE_RIGHT}


# Create a modifier map of Qt modifier keys to Zinc modifier keys
def modifier_map(qt_modifiers):
    '''
    Return a Zinc SceneViewerInput modifiers object that is created from
    the Qt modifier flags passed in.
    '''
    modifiers = Sceneviewerinput.MODIFIER_FLAG_NONE
    if qt_modifiers & QtCore.Qt.SHIFT:
        modifiers = modifiers | Sceneviewerinput.MODIFIER_FLAG_SHIFT

    return modifiers


# mapping from qt to zinc end


def tryint(s):
    try:
        return int(s)
    except:
        return s


def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [tryint(c) for c in re.split('([0-9]+)', s)]


class ZincScene(QtOpenGLWidgets.QOpenGLWidget):

    # init start
    def __init__(self, parent=None):
        '''
        Call the super class init functions, create a Zinc context and set the scene viewer handle to None.
        '''

        QtOpenGLWidgets.QOpenGLWidget.__init__(self, parent)
        # Create a Zinc context from which all other objects can be derived either directly or indirectly.
        self._context = Context("autosegmenter")
        self._sceneviewer = None
        self._imageDataLocation = None
        # init end

    def setImageDataLocation(self, imageDataLocation):
        self._imageDataLocation = imageDataLocation

    def getPointCloud(self):
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

    def setImagePlaneVisibility(self, state):
        self._iso_graphic.setVisibilityFlag(state != 0)

    def setSegmentationVisibility(self, state):
        self._contour.setVisibilityFlag(state != 0)

    def setPointCloudVisibility(self, state):
        self._point_cloud.setVisibilityFlag(state != 0)

    # initializeGL start
    def initializeGL(self):
        '''
        Initialise the Zinc scene for drawing the axis glyph at a point.  
        '''
        if self._sceneviewer is None:
            # From the context get the default scene viewer module.
            scene_viewer_module = self._context.getSceneviewermodule()

            # From the scene viewer module we can create a scene viewer, we set up the scene viewer to have the same OpenGL properties as
            # the QGLWidget.
            self._sceneviewer = scene_viewer_module.createSceneviewer(Sceneviewer.BUFFERING_MODE_DOUBLE,
                                                                      Sceneviewer.STEREO_MODE_MONO)
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)

            # Create a filter for visibility flags which will allow us to see our graphic.
            filter_module = self._context.getScenefiltermodule()
            # By default graphics are created with their visibility flags set to on (or true).
            graphics_filter = filter_module.createScenefilterVisibilityFlags()

            # Set the graphics filter for the scene viewer otherwise nothing will be visible.
            self._sceneviewer.setScenefilter(graphics_filter)
            root_region = self._context.getDefaultRegion()
            scene = root_region.getScene()

            glyph_module = self._context.getGlyphmodule()
            glyph_module.defineStandardGlyphs()

            material_module = self._context.getMaterialmodule()
            material_module.defineStandardMaterials()
            gold = material_module.findMaterialByName('gold')

            # Once the renditions have been enabled for a region tree you can get a valid
            # handle for a rendition and create graphics for it.
            tessellation_module = self._context.getTessellationmodule()
            tessellation = tessellation_module.createTessellation()
            tessellation.setMinimumDivisions([64])
            #             tessellation_module.setDefaultTessellation(tessellation)

            # We use the beginChange and endChange to wrap any immediate changes and will
            # streamline the rendering of the scene.
            scene.beginChange()

            # Visualise images
            self.createFiniteElements(root_region)
            self.createMaterialUsingImageField()

            field_module = root_region.getFieldmodule()
            #             xi_field = field_module.findFieldByName('xi')
            finite_element_field = field_module.findFieldByName('coordinates')
            self._segmented_image_field = field_module.createFieldImageFromSource(self._segmented_field)

            self._contour = scene.createGraphicsContours()
            self._contour.setCoordinateField(finite_element_field)
            self._contour.setTessellation(tessellation)
            #             self._contour.setMaterial(self._material)
            #             print(self._contour2.setTextureCoordinateField(xi_field))
            # set the yz scalar field to our isosurface
            self._contour.setIsoscalarField(self._segmented_image_field)
            self._contour.setMaterial(gold)
            # define the initial position of the isosurface on the texture block
            self._contour.setListIsovalues([0.2])  # Range(1, self.initial_positions[0], self.initial_positions[0])

            nodeset, output_coordinates = self.setupOutputRegion(root_region)

            scene.convertToPointCloud(graphics_filter, nodeset, output_coordinates, 0.0, 0.0, 10000.0, 1.0)
            # Create a graphic point in our rendition and set it's glyph type to axes.
            # Set the scene to our scene viewer.
            self.createSurfaceGraphics(root_region)
            self._sceneviewer.setScene(scene)

            scene.endChange()
            # Let the rendition render the scene.
            # initializeGL end

            self._sceneviewer.viewAll()

            self._sceneviewernotifier = self._sceneviewer.createSceneviewernotifier()
            self._sceneviewernotifier.setCallback(self._zincSceneviewerEvent)

    def setupOutputRegion(self, root_region):
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

        return (nodeset, finite_element_field)

    def createSurfaceGraphics(self, region):
        '''
        To visualize the 3D finite element that we have created for each _surface_region, we use a 
        surface graphic then set a _material for that surface to use.
        '''
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

    def createMaterialUsingImageField(self):
        ''' 
        Use an image field in a grpahics material to create a n OpenGL texture
        '''
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
        self._image_field.setWrapMode(FieldImage.WRAP_MODE_REPEAT)

        # Create a stream information object that we can use to read the
        # image file from disk
        stream_information = self._image_field.createStreaminformationImage()
        # specify depth of texture block i.e. number of images
        #        stream_information.setAttributeInteger(stream_information.IMAGE_ATTRIBUTE_, self.number_of_images)

        # Load images onto an invidual texture blocks.
        directory = self._imageDataLocation.location()
        files = os.listdir(directory)
        files.sort(key=alphanum_key)
        for filename in files:
            if filename not in ['.hg', 'annotation.rdf']:
                # We are reading in a file from the local disk so our resource is a file.
                string_name = str(os.path.join(directory, filename))
                stream_information.createStreamresourceFile(string_name)

        # Actually read in the image file into the image field.
        #         self._image_field.setAttributeReal(FieldImage.IMAGE_ATTRIBUTE_PHYSICAL_WIDTH_PIXELS, 1)
        #         self._image_field.setAttributeReal(FieldImage.IMAGE_ATTRIBUTE_PHYSICAL_HEIGHT_PIXELS, 1)
        #         self._image_field.setAttributeReal(FieldImage.IMAGE_ATTRIBUTE_PHYSICAL_DEPTH_PIXELS, 1)
        self._image_field.read(stream_information)
        self._material.setTextureField(1, self._image_field)

        self._smooth_field = field_module.createFieldImagefilterCurvatureAnisotropicDiffusion(self._image_field, 0.0625,
                                                                                              2, 5)
        self._segmented_field = field_module.createFieldImagefilterConnectedThreshold(self._smooth_field, 0.2, 1.0, 1,
                                                                                      1, [0.5, 0.6111, 0.3889])

    def _zincSceneviewerEvent(self, event):
        '''
        Process a scene viewer event.  The updateGL() method is called for a
        repaint required event all other events are ignored.
        '''
        if event.getChangeFlags() & Sceneviewerevent.CHANGE_FLAG_REPAINT_REQUIRED:
            QtCore.QTimer.singleShot(0, self.updateGL)

    def setSliderValue(self, value):
        self._iso_graphic.setListIsovalues([value / 100.0])

    #         self.updateGL()

    def createFiniteElements(self, region):
        '''
        Create finite element meshes for each of the images
        '''
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
        create3DFiniteElement(field_module, finite_element_field, node_coordinate_set)

        self._scalar_field = field_module.createFieldComponent(finite_element_field, 3)

        field_module.defineAllFaces()

        field_module.endChange()

    def paintGL(self):
        '''
        Render the scene for this scene viewer.  The QGLWidget has already set up the
        correct OpenGL buffer for us so all we need do is render into it.  The scene viewer
        will clear the background so any OpenGL drawing of your own needs to go after this
        API call.
        '''
        self._sceneviewer.renderScene()
        # paintGL end

    # resizeGL start
    def resizeGL(self, width, height):
        '''
        Respond to widget resize events.
        '''
        self._sceneviewer.setViewportSize(width, height)
        # resizeGL end

    def mousePressEvent(self, event):
        '''
        Inform the scene viewer of a mouse press event.
        '''
        scene_input = self._sceneviewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_PRESS)
        scene_input.setButtonType(button_map[event.button()])
        scene_input.setModifierFlags(modifier_map(event.modifiers()))

        self._sceneviewer.processSceneviewerinput(scene_input)

        self._handle_mouse_events = True

    def mouseReleaseEvent(self, event):
        '''
        Inform the scene viewer of a mouse release event.
        '''
        scene_input = self._sceneviewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
        scene_input.setButtonType(button_map[event.button()])

        self._sceneviewer.processSceneviewerinput(scene_input)

    def mouseMoveEvent(self, event):
        '''
        Inform the scene viewer of a mouse move event and update the OpenGL scene to reflect this
        change to the viewport.
        '''

        scene_input = self._sceneviewer.createSceneviewerinput()
        scene_input.setPosition(event.x(), event.y())
        scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_MOTION_NOTIFY)
        if event.type() == QtCore.QEvent.Leave:
            scene_input.setPosition(-1, -1)

        self._sceneviewer.processSceneviewerinput(scene_input)


def create3DFiniteElement(fieldmodule, finite_element_field, node_coordinate_set):
    '''
    Create a single finite element using the supplied 
    finite element field and node coordinate set.
    '''
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
