from qgis.core import *
from qgis.utils import *
import processing

class FlowDirection:
    '''
    PT/BR
    Classe para corrigir o sentido da drenagem (preferencialmente). Pode ser usada para outros tipos de rede.
    
    INPUT
        layer <QgsVectorLayer> : Camada de drenagem (camada ativa)
    '''

    def __init__(self, layer):
        '''
        self.layer : camada de linhas
        self.oks : lista com todas as feições conectadas
        self.flipped : lista com todas as feições que foram corrigidas
        '''
        self.layer = layer
        self.before = []
        self.oks = []
        self.flipped = []
        self.startoks = []
        self.endoks = []

    def flip_line(self, feature):
        '''
        Vira o sentido da feição de linha (input).
        '''
        line = feature.geometry().asPolyline()
        line.reverse()
        newgeom = QgsGeometry.fromPolylineXY(line)
        self.layer.changeGeometry(feature.id(),newgeom)


    def get_connected(self):
        '''
        Seleciona e obtem todas as linhas conectadas à linha selecionada.
        Retorna uma lista com todas as feições conectadas.
        '''
        for f in self.layer.selectedFeatures():
            self.oks.append(f.id())
            self.startoks.append(f.geometry().asPolyline()[0])
            self.endoks.append(f.geometry().asPolyline()[-1])
        param = {'INPUT': self.layer,
                'PREDICATE' : 0,
                'INTERSECT' : QgsProcessingFeatureSourceDefinition(self.layer.source(), True),
                'METHOD' : 0}


        processing.run("qgis:selectbylocation", param) #will get the connections on the current flow
        self.layer.deselect(self.oks)
        connected_lines = self.layer.selectedFeatures() #list with the connected features
        return connected_lines

    def flip_connected(self, connected_lines):
        '''
        Corrige o sentido de todo o ramo conectado na feição selecionada (deve ser a foz).
        '''
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

        self.startoks.clear() #testing 
        new_con = self.get_connected()
        if len(new_con) > 1: #lock to break the main loop
            self.flip_connected(new_con) #main loop to get all the tree

    def get_branch(self):
        '''
        Seleciona todo o ramo da feição selecionada (preferencialmente a foz).
        '''
        starts = self.get_connected()
        if len(starts) < 1:
            return 
        
        for branch in starts:
            self.get_branch()
        
        self.layer.select(self.oks)
        self.resetList()

    def resetList(self): #reset the ids inside the object
        '''
        Função para resetar lista de feições armazenadas no objeto
        '''
        self.oks.clear()
        self.startoks.clear()
        self.endoks.clear()
        self.flipped.clear()

    def run(self):
        '''
        Confere as condições de uso e executa a função flip_connected. Seleciona todos as feições que foram corrigidas.
        '''
        rmouth = self.layer.selectedFeatures() #line

        if len(rmouth) > 1:
            print('Selecione apenas 1 feição')
            return None #useful for stop the code and not break the qgis environment

        self.flip_connected(self.get_connected())
        self.layer.select(self.flipped) #select the flipped branchs
        print('finish')


'''
#get the selected line (should be the sink drain)
layer = iface.activeLayer()

f = FlowDirection(layer)
#f.get_branch()
f.run()
layer.select(f.oks)
for feat in layer.selectedFeatures():
    layer.changeAttributeValue(feat.id(), 1, 0)
    
print(len(f.oks))
'''