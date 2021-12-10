from qgis.core import *
from qgis.utils import *
import processing
#get the selected line (should be the sink drain)
layer = iface.activeLayer()
rmouth = layer.selectedFeatures() #line

if len(rmouth) > 1:
    print('Selecione apenas 1 feição')
    forcedstop #useful for stop the code and not break the qgis environment
else:
    rmouth = rmouth[0]


featureList = list(layer.getFeatures()) #all features

class flow_direction:
    def __init__(self, layer):
        self.layer = layer
        self.before = []
        self.oks = []
        self.flipped = []
        self.startoks = []
        self.endoks = []

    def flip_line(self, feature):
        line = feature.geometry().asPolyline()
        line.reverse()
        newgeom = QgsGeometry.fromPolylineXY(line)
        layer.changeGeometry(feature.id(),newgeom)


    def get_connected(self):
        for f in layer.selectedFeatures():
            self.oks.append(f.id())
            self.startoks.append(f.geometry().asPolyline()[0])
            self.endoks.append(f.geometry().asPolyline()[-1])
        param = {'INPUT': layer,
                'PREDICATE' : 0,
                'INTERSECT' : QgsProcessingFeatureSourceDefinition(layer.source(), True),
                'METHOD' : 0}


        processing.run("qgis:selectbylocation", param) #will get the connections on the current flow
        layer.deselect(self.oks)
        connected_lines = layer.selectedFeatures() #list with the connected features
        return connected_lines

    def flip_connected(self, connected_lines):
        self.layer.startEditing()
        for line in connected_lines:
            line_points = line.geometry().asPolyline()
            
            #check the branch
            startline = line_points[0]
            endline = line_points[-1]

            #check the flow
            if (startline in self.startoks):
                self.flip_line(line)
                self.flipped.append(line.id())
                #print(f'flip {line.id()}')

        
        new_con = self.get_connected()
        if len(new_con) > 1: #lock to break the main loop
            self.flip_connected(new_con) #main loop to get all the tree

    def get_branch(self):
        starts = self.get_connected()
        if len(starts) < 1:
            return
        
        for branch in starts:
            self.get_branch()
        
        self.layer.select(f.oks)
        self.resetList()

    def resetList(self): #reset the ids inside the object
        self.oks.clear()
        self.startoks.clear()
        self.endoks.clear()
        self.flipped.clear()

    def run(self):
        f.flip_connected(f.get_connected())
        self.layer.select(f.flipped) #select the flipped branchs
        print('finish')

f = flow_direction(layer)
#f.run()
