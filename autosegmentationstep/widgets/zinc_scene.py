
import os, re

from PySide import QtCore, QtOpenGL

from opencmiss.zinc.context import Context
from opencmiss.zinc.graphic import Graphic
from opencmiss.zinc.sceneviewer import SceneViewerInput, SceneViewer
from opencmiss.zinc.field import Field, FieldImage
from opencmiss.zinc.element import Element, ElementBasis

# Create a button map of Qt mouse buttons to Zinc input buttons
button_map = {QtCore.Qt.LeftButton: SceneViewerInput.INPUT_BUTTON_LEFT, QtCore.Qt.MiddleButton: SceneViewerInput.INPUT_BUTTON_MIDDLE, QtCore.Qt.RightButton: SceneViewerInput.INPUT_BUTTON_RIGHT}

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

class ZincScene(QtOpenGL.QGLWidget):
    
    # init start
    def __init__(self, parent = None):
        '''
        Call the super class init functions, create a Zinc context and set the scene viewer handle to None.
        '''
        
        QtOpenGL.QGLWidget.__init__(self, parent)
        # Create a Zinc context from which all other objects can be derived either directly or indirectly.
        self._context = Context("autosegmenter")
        self._scene_viewer = None
        self._imageDataLocation = None
        # init end

    def setImageDataLocation(self, imageDataLocation):
        self._imageDataLocation = imageDataLocation

    def getPointCloud(self):
        point_cloud = []
        field_module = self._point_cloud_region.getFieldModule()
        field_module.beginChange()
        field_cache = field_module.createCache()
        coordinate_field = field_module.findFieldByName('coordinates')
        nodeset = field_module.findNodesetByName('cmiss_nodes')
        template = nodeset.createNodeTemplate()
        template.defineField(coordinate_field)

        node_iterator = nodeset.createNodeIterator()
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
        self.updateGL()
        
    def setSegmentationVisibility(self, state):
        self._contour.setVisibilityFlag(state != 0)
        self.updateGL()
        
    def setPointCloudVisibility(self, state):
        self._point_cloud.setVisibilityFlag(state != 0)
        self.updateGL()
        
    # initializeGL start
    def initializeGL(self):
        '''
        Initialise the Zinc scene for drawing the axis glyph at a point.  
        '''
        
        # From the context get the default scene viewer module.
        scene_viewer_module = self._context.getDefaultSceneViewerModule()
        
        # From the scene viewer module we can create a scene viewer, we set up the scene viewer to have the same OpenGL properties as
        # the QGLWidget.
        self._scene_viewer = scene_viewer_module.createSceneViewer(SceneViewer.BUFFERING_MODE_DOUBLE, SceneViewer.STEREO_MODE_ANY)
        
        # Get a the root region to create the point in.  Every context has a default region called the root region.
        root_region = self._context.getDefaultRegion()
#        output_region = root_region.createChild('output')
        
        
        # Get the default graphics module from the context and enable renditions
        graphics_module = self._context.getDefaultGraphicsModule()
        graphics_module.enableRenditions(root_region)
        
        glyph_module = graphics_module.getGlyphModule()
        glyph_module.createStandardGlyphs()
        
        graphics_module.defineStandardMaterials()
        gold = graphics_module.findMaterialByName('gold')
                
        # Once the renditions have been enabled for a region tree you can get a valid 
        # handle for a rendition and create graphics for it.
        rendition = graphics_module.getRendition(root_region)
        tessellation_module = graphics_module.getTessellationModule()
        tessellation = tessellation_module.getDefaultTessellation()
        tessellation.setMinimumDivisions([100])
        tessellation_module.setDefaultTessellation(tessellation)
        
        # We use the beginChange and endChange to wrap any immediate changes and will
        # streamline the rendering of the scene.
        rendition.beginChange()
        
        # Visualise images 
        self.createFiniteElements(root_region)
        self.createMaterialUsingImageField()
        
        # Create a filter for visibility flags which will allow us to see our graphic.  By default graphics
        # are created with their visibility flags set to true.
        graphics_filter = graphics_module.createFilterVisibilityFlags()
        
        # Create a scene and set the region tree for it to show.  We also set the graphics filter for the scene
        # otherwise nothing will be visible.
        scene = graphics_module.createScene()
        scene.setRegion(root_region)
        scene.setFilter(graphics_filter)
        
        field_module = root_region.getFieldModule()
        xi_field = field_module.findFieldByName('xi')
        finite_element_field = field_module.findFieldByName('coordinates')
        self._segmented_image_field = field_module.createImageFromSource(xi_field, self._segmented_field)
        
        self._contour = rendition.createGraphicContours()
        self._contour.setCoordinateField(finite_element_field)
#        self._contour.setMaterial(self._material)
#        print(self._contour2.setTextureCoordinateField(xi_field))
        # set the yz scalar field to our isosurface
        self._contour.setIsoscalarField(self._segmented_image_field)
        self._contour.setMaterial(gold)
        # define the initial position of the isosurface on the texture block
        self._contour.setListIsovalues([0.2])  # Range(1, self.initial_positions[0], self.initial_positions[0])
        
        nodeset, output_coordinates = self.setupOutputRegion(root_region)
        
        rendition.convertToPointCloud(graphics_filter, nodeset, output_coordinates, 0.0, 0.0, 10000.0, 1.0)
        # Create a graphic point in our rendition and set it's glyph type to axes.
        # Set the scene to our scene viewer.
        self.createSurfaceGraphics(root_region)
        self._scene_viewer.setScene(scene)

        rendition.endChange()
        # Let the rendition render the scene.
        # initializeGL end
        
        self._scene_viewer.viewAll()
        
    def setupOutputRegion(self, root_region):
        self._point_cloud_region = root_region.createChild('output')
        field_module = self._point_cloud_region.getFieldModule()
        finite_element_field = field_module.createFiniteElement(3)
        # Set the name of the field, we give it label to help us understand it's purpose
        finite_element_field.setName('coordinates')
        # Set the attribute is managed to 1 so the field module will manage the field for us
        finite_element_field.setManaged(True)

        nodeset = field_module.findNodesetByDomainType(Field.DOMAIN_NODES)
        
        graphics_module = self._context.getDefaultGraphicsModule()
        rendition = graphics_module.getRendition(self._point_cloud_region)
        self._point_cloud = rendition.createGraphicPoints()
        self._point_cloud.setDomainType(Field.DOMAIN_NODES)
        self._point_cloud.setCoordinateField(finite_element_field)
        attributes = self._point_cloud.getPointAttributes()
        attributes.setGlyphType(Graphic.GLYPH_TYPE_SPHERE)
        attributes.setBaseSize([0.01])
        
        return (nodeset, finite_element_field)
        
    def createSurfaceGraphics(self, region):
        '''
        To visualize the 3D finite element that we have created for each _surface_region, we use a 
        surface graphic then set a _material for that surface to use.
        '''
        graphics_module = self._context.getDefaultGraphicsModule()
        # we iterate over the regions that we kept a handle to and use an index to get a
        # matching list of graphic _material names
        # for i, _surface_region in enumerate(self.regions_):
        rendition = graphics_module.getRendition(region)
        field_module = region.getFieldModule()

        finite_element_field = field_module.findFieldByName('coordinates')

        # Create three isosurface planes in the x, y and z directions whose positions in the texture block
        # can be altered using sliders
        # ## x component
        self._iso_graphic = rendition.createGraphicContours()
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
        graphics_module = self._context.getDefaultGraphicsModule()
        self._material = graphics_module.createMaterial()
        self._material.setName('texture_block')
#        self._material.setManaged(True)

        # Get a handle to the root _surface_region
        root_region = self._context.getDefaultRegion()

        # The field module allows us to create a field image to
        # store the image data into.
        field_module = root_region.getFieldModule()
        xi_field = field_module.findFieldByName('coordinates')
        # Create an image field. A temporary xi source field is created for us.
        self._image_field = field_module.createImageWithDomain(xi_field)
#        self._image_field.setName('image_field')
        self._image_field.setFilterMode(self._image_field.FILTER_LINEAR)

        # Create a stream information object that we can use to read the
        # image file from disk
        stream_information = self._image_field.createStreamInformation()
        # specify depth of texture block i.e. number of images
#        stream_information.setAttributeInteger(stream_information.IMAGE_ATTRIBUTE_, self.number_of_images)

        # Load images onto an invidual texture blocks.
        directory = self._imageDataLocation.location()
        files = os.listdir(directory)
        files.sort(key=alphanum_key)
        for filename in files:
            # We are reading in a file from the local disk so our resource is a file.
            string_name = str(os.path.join(directory, filename))
            stream_information.createResourceFile(string_name)

        # Actually read in the image file into the image field.
        self._image_field.setAttributeReal(FieldImage.IMAGE_ATTRIBUTE_PHYSICAL_WIDTH_PIXELS, 1)
        self._image_field.setAttributeReal(FieldImage.IMAGE_ATTRIBUTE_PHYSICAL_HEIGHT_PIXELS, 1)
        self._image_field.setAttributeReal(FieldImage.IMAGE_ATTRIBUTE_PHYSICAL_DEPTH_PIXELS, 1)
        self._image_field.read(stream_information)
        self._material.setImageField(1, self._image_field)
        
        self._smooth_field = field_module.createCurvatureAnisotropicDiffusionImageFilter(self._image_field, 0.0625, 2, 5)
        self._segmented_field = field_module.createConnectedThresholdImageFilter(self._smooth_field, 0.2, 1.0, 1, 1, [0.5, 0.6111, 0.3889])

    def setSliderValue(self, value):
        self._iso_graphic.setListIsovalues([value / 100.0])
        
        self.updateGL()
        
    def createFiniteElements(self, region):
        '''
        Create finite element meshes for each of the images
        '''
        # Define the coordinates for each 3D element
#        node_coordinate_set = [[0, 0, 0], [101, 0, 0], [0, 0, 52.0], [101, 0, 52.0], [0, 109, 0], [101, 109, 0], [0, 109, 52.0], [101, 109, 52.0]]
#        a , b, c = 53.192, 49.288, 36.4
#        node_coordinate_set = [[a, 0, 0], [a, 0, c], [0, 0, 0], [0, 0, c], [a, b, 0], [a, b, c], [0, b, 0], [0, b, c]]
#        a , b, c = 101, 109, 52
        field_module = region.getFieldModule()
        field_module.beginChange()

        # Create a finite element field with 3 components to represent 3 dimensions
        finite_element_field = field_module.createFiniteElement(3)

        # Set the name of the field
        finite_element_field.setName('coordinates')
        # Set the attribute is managed to 1 so the field module will manage the field for us
        finite_element_field.setManaged(True)
        finite_element_field.setAttributeInteger(Field.ATTRIBUTE_IS_COORDINATE, 1)

        a, b, c = 1, 1, 1
        node_coordinate_set = [[0, 0, 0], [a, 0, 0], [0, b, 0], [a, b, 0], [0, 0, c], [a, 0, c], [0, b, c], [a, b, c]]
        self.create3DFiniteElement(field_module, finite_element_field, node_coordinate_set)

        self._scalar_field = field_module.createComponent(finite_element_field, 3)

        field_module.defineAllFaces()
        
        field_module.endChange()

    def create3DFiniteElement(self, field_module, finite_element_field, node_coordinate_set):
        '''
        Create finite element from a template
        '''
        # Find a special node set named 'cmiss_nodes'
        nodeset = field_module.findNodesetByName('cmiss_nodes')
        node_template = nodeset.createNodeTemplate()

        # Set the finite element coordinate field for the nodes to use
        node_template.defineField(finite_element_field)
        field_cache = field_module.createCache()

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
        mesh = field_module.findMeshByDimension(3)
        element_template = mesh.createElementTemplate()
        element_template.setShapeType(Element.SHAPE_CUBE)
        element_node_count = 8
        element_template.setNumberOfNodes(element_node_count)
        # Specify the dimension and the interpolation function for the element basis function
        linear_basis = field_module.createElementBasis(3, ElementBasis.FUNCTION_LINEAR_LAGRANGE)
        # the indecies of the nodes in the node template we want to use.
        node_indexes = [1, 2, 3, 4, 5, 6, 7, 8]


        # Define a nodally interpolated element field or field component in the
        # element_template
        element_template.defineFieldSimpleNodal(finite_element_field, -1, linear_basis, node_indexes)

        for i, node_identifier in enumerate(node_identifiers):
            node = nodeset.findNodeByIdentifier(node_identifier)
            element_template.setNode(i + 1, node)

        mesh.defineElement(-1, element_template)

    # paintGL start
    def paintGL(self):
        '''
        Render the scene for this scene viewer.  The QGLWidget has already set up the
        correct OpenGL buffer for us so all we need do is render into it.  The scene viewer
        will clear the background so any OpenGL drawing of your own needs to go after this
        API call.
        '''
        self._scene_viewer.renderScene()
        # paintGL end

    # resizeGL start
    def resizeGL(self, width, height):
        '''
        Respond to widget resize events.
        '''
        self._scene_viewer.setViewportSize(width, height)
        # resizeGL end

    def mousePressEvent(self, mouseevent):
        '''
        Inform the scene viewer of a mouse press event.
        '''
        scene_input = self._scene_viewer.getInput()
        scene_input.setPosition(mouseevent.x(), mouseevent.y())
        scene_input.setType(SceneViewerInput.INPUT_EVENT_TYPE_BUTTON_PRESS)
        scene_input.setButton(button_map[mouseevent.button()])
            
        self._scene_viewer.processInput(scene_input)
        
    def mouseReleaseEvent(self, mouseevent):
        '''
        Inform the scene viewer of a mouse release event.
        '''
        scene_input = self._scene_viewer.getInput()
        scene_input.setPosition(mouseevent.x(), mouseevent.y())
        scene_input.setType(SceneViewerInput.INPUT_EVENT_TYPE_BUTTON_RELEASE)
        scene_input.setButton(button_map[mouseevent.button()])
            
        self._scene_viewer.processInput(scene_input)
        
    def mouseMoveEvent(self, mouseevent):
        '''
        Inform the scene viewer of a mouse move event and update the OpenGL scene to reflect this
        change to the viewport.
        '''
        scene_input = self._scene_viewer.getInput()
        scene_input.setPosition(mouseevent.x(), mouseevent.y())
        scene_input.setType(SceneViewerInput.INPUT_EVENT_TYPE_MOTION_NOTIFY)
        if mouseevent.type() == QtCore.QEvent.Leave:
            scene_input.setPosition(-1, -1)
        
        self._scene_viewer.processInput(scene_input)
        
        # The viewport has been changed so update the OpenGL scene.
        self.updateGL()


