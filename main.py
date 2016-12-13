import sys
import os
from PyQt4 import QtCore, QtGui
import gabbs.maps
from gabbs.MapUtils import iface

INSTALLDIR = os.path.realpath(__file__)
DATADIR = os.path.join(os.path.dirname(INSTALLDIR), 'ref')


class MapWidget(QtGui.QWidget):
    def __init__(self):

        super(MapWidget,self).__init__()

        self.initUI()


    def initUI(self):

        self.resize(900, 600)
        self.setWindowTitle("Pymaplib Tutorial Tool")
        grid = QtGui.QGridLayout()
        self.setLayout(grid)


        # Build map container, which will contain base map(OSM) and other layers
        # We can set map control widgets and other useful tools here.
        self.mapContainer = gabbs.maps.MapContainer()
        self.mapContainer.setLayerControl(True)
        self.mapContainer.setPanControl(True)
        self.mapContainer.setZoomControl(True, size = "CUSTOM",
            options = "ZOOMIN, ZOOMOUT, ZOOMHOME, ZOOMFULL, ZOOMLAYER")
        self.mapContainer.setSelectControl(True, size = "CUSTOM",
            options = "SINGLE, RECTANGLE, POLYGON, FREEHAND, RADIUS")
        self.mapContainer.setPlugin("drawingtool")
        self.mapContainer.setCaptureTool(True)

        # Add canvas as a widget to the layout
        grid.addWidget(self.mapContainer,0,0)

        # Create a base map object
        self.map = gabbs.maps.Map("Open_Street_Map")
        self.map.setMapCenter(-86, 40.5)
        self.map.setMapZoom(7)
        self.map.setMapScale(5, 10)
        self.mapContainer.addLayer(self.map)

        # Add vector layer to the map container (json format)

        jsonfp = os.path.join(DATADIR, 'distJSON.json')
        borderfp = os.path.join(DATADIR, 'border.qml')
        self.polygon1 = gabbs.maps.Vector(jsonfp, "IN_District_Vector_json")
        self.polygon1.setCustomStyle(borderfp)
        self.polygon1.setCustomScale([5,8])
        self.mapContainer.addLayer(self.polygon1)

        # Also, we set the event handler to be called when this vector layer is selected.
        # Check the function doSomething() below to see how to get selected layer's information
        self.polygon1.getLayer().selectionChanged.connect(self.doSomething)


        # Create / Add a Vector object to the map container (shape file format)
        countiesfp = os.path.join(DATADIR, 'Counties.shp')
        self.polygon2 = gabbs.maps.Vector(countiesfp, "MI_Counties_Vector_shp")
        self.customStyleAtt = {"useSystemStyle": True,
                               "styleName":      "SIMPLE_FILL_LAND",
                               "visible":        True,
                               "opacity":        0.7}
        self.polygon2.setLayerProperty(self.customStyleAtt)
        self.mapContainer.addLayer(self.polygon2)


        # Create / Add a Raster object to the map container (tif format)
        lc8fp = os.path.join(DATADIR, 'LC8_20130524.tif')
        self.raster1 = gabbs.maps.Raster(lc8fp, "Lafayette_Raster_tif")
        self.mapContainer.addLayer(self.raster1)


        # Create / Add a Raster object to the map container (from geoserver)
        self.uri = "http://geoserver.rcac.purdue.edu:8081/geoserver/geoshare/ows?" \
                   + "service=WFS&version=1.0.0" \
                   + "&request=GetFeature" \
                   + "&typeName=geoshare:stjoewater_boundary_1004" \
                   + "&maxFeatures=50" \
                   + "&srsname=EPSG:4326"
        self.polygon3 = gabbs.maps.Vector(self.uri, "GeoServer_Vector_WFS", "WFS")
        self.mapContainer.addLayer(self.polygon3)


        QtCore.QObject.connect(
            iface.mainWindow.plugins["drawingtool"].tool, \
            QtCore.SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), \
            self.printValues)


        self.printLabel = QtGui.QLabel(self.mapContainer)
        self.printLabel.setGeometry(QtCore.QRect(42, 10, 600, 24))
        self.printLabel.setObjectName("infoLabel")


    def printValues(self):

        # QgsRectangle
        lonFrom = gabbs.maps.gbsGetDrawingBounds().topLeft().x()
        latFrom = gabbs.maps.gbsGetDrawingBounds().topLeft().y()
        lonTo = gabbs.maps.gbsGetDrawingBounds().bottomRight().x()
        latTo = gabbs.maps.gbsGetDrawingBounds().bottomRight().y()

        line = "({0:.2f}, {1:.2f}) / ({2:.2f}, {3:.2f})"\
                .format(lonFrom,latFrom,lonTo,latTo)

        if line == "(0.00, 0.00) / (0.00, 0.00)":
            line = ""
        self.printLabel.setText(line)


    def doSomething(self):
        # gabbs.maps.gbsGetSelectedAttributes() will return all the
        # values related to the selected information.
        line = gabbs.maps.gbsGetSelectedAttributes()

        if len(line) == 0:
            line = ""
        else:
            line = str(line)
        self.printLabel.setText(line)


def main():
    # create Qt application
    app = QtGui.QApplication(sys.argv)

    # Initialize gabbs maps libraries
    gabbs.maps.gbsLoadLibrary()

    # create main window
    wnd = MapWidget()

    wnd.show()

    # run!
    retval = app.exec_()

    # Exit gabbs maps libraries
    gabbs.maps.gbsUnloadLibrary()

    sys.exit(retval)


if __name__ == "__main__":
    main()
