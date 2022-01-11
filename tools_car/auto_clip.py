from qgis.utils import *
from qgis.core import *
import processing
import os 

class AutoClip:
    '''
    Classe usada após gerar drenagens.
    '''
    def __init__(self, params):
        '''
        path : pasta com vetores a serem cortados
        mask : Camada do vetor de mascara
        output : pasta de saída dos vetores
        '''
        self.path = params['path']
        self.mask = params['mask']
        self.output = params['output']


    def run(self, uf, merge=True, campo='wts_pk'):
        '''
        Função para cortar vetores distintos utlizando uma mascara e no final, mesclando-os.
        Retorna uma lista de vetores cortados ou o vetor final mesclado.
        '''
        clipped_shapes = []

        for feature in self.mask.getFeatures():
            nb = str(int(feature[campo])) #pegar o numero da bacia
            drenagem = QgsVectorLayer(os.path.join(self.path, f'{nb}fluxo.shp'))

            if not drenagem.isValid():
                print(f'ERRO: {nb} não válida')
                continue
            
            self.mask.select(feature.id())
            mask = QgsProcessingFeatureSourceDefinition(self.mask.source(),
                                                selectedFeaturesOnly=True)
            
            id = 'native:clip'
            alg_params = {"INPUT": drenagem,
                          "OVERLAY": mask,
                          "OUTPUT": os.path.join(self.output, f'drenagem{nb}_clip.shp')}
             
            result = processing.run(id, alg_params)
            self.mask.removeSelection()
            print(f'Bacia {nb} foi recortada.')

            clipped_shapes.append(result['OUTPUT'])

        if not(merge):
            return clipped_shapes
        
        id2 = 'native:mergevectorlayers'
        params = {'LAYERS': clipped_shapes,
                  'CRS':  'EPSG:4674',
                  'OUTPUT': os.path.join(self.output,f'merged_{uf}.shp')}
        res = processing.run(id2, params)
        print(f'{len(clipped_shapes)} vetores foram cortados e mesclados!')
        return res['OUTPUT']
