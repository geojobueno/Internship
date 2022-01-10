from qgis.utils import *
from qgis.core import *
import os

class AutoGrid:
    '''
    Classe criada para cortar imagens da Planet, criando um grid regular e salvando cada
    corte na pasta de destino. Parametros recebidos via dicionario.
    '''
    def __init__(self, params):
        '''
        PT/BR
        Params <dict> : {raster <QgsRasterLayer> : Imagem
                         ij <tuple> : (linhas, colunas)
                         output <str> : Caminho de saída
                        }
        '''
        self.r = params['raster']
        self.nx, self.ny = params['ij']
        self.output = params['output']


    def make_grid(self):
        '''
        Cria um grid usando o extent de uma camada, com nx linhas e ny colunas.
        '''
        r = self.r
        nx,ny = self.nx, self.ny

        rect = r.extent()

        gridlayer = QgsVectorLayer('Polygon',f'GRID {r.name()}','memory')
        dp = gridlayer.dataProvider()
        dp.addAttributes([QgsField("i", QVariant.Int),
                        QgsField("j", QVariant.Int),
                        QgsField("ij", QVariant.String),
                        QgsField("size_gb", QVariant.Double)])
        gridlayer.updateFields()

        xmin = rect.xMinimum()
        xmax = rect.xMaximum()
        ymin = rect.yMinimum()
        ymax = rect.yMaximum()

        larg = xmax-xmin
        alt = ymax-ymin

        tx = larg/nx
        ty = alt/ny

        size = tx*ty*4.15

        feat = QgsFeature()

        x1, y1 = xmin, ymax

        for i in range(nx):
            
            for j in range(ny):
                p1 = QgsPointXY(x1,y1)
                p2 = QgsPointXY(x1+tx, y1-ty)
                g = QgsGeometry.fromRect(QgsRectangle(p1,p2))
                
                feat.setGeometry(g)
                feat.setAttributes([i,j,f'{i}{j}',size])
                dp.addFeature(feat)
                y1 = y1-ty
                
            x1 = x1+tx
            y1 = ymax

        gridlayer.updateExtents()
        QgsProject.instance().addMapLayer(gridlayer)
        
        return gridlayer

    def clip_by_grid(self, grid):
        '''
        Usa uma camada de vetor (grid) para cortar um raster, iterando cada feição.
        '''
        r = self.r
        output = self.output

        #iterar feições, selecionar cada uma, cortar raster na mascara da selcionada
        results = []
        for feat in grid.getFeatures():
            grid.select(feat.id())
            print(f'Clipping grid: {feat["ij"]}')
            mask = QgsProcessingFeatureSourceDefinition(grid.source(),
                                                        selectedFeaturesOnly=True)
            id = 'gdal:cliprasterbymasklayer'
            alg_params = {"INPUT": r,
                        "MASK": mask,
                        'KEEP_RESOLUTION': True,
                        'DATA_TYPE' : 0,
                        "OUTPUT": os.path.join(output, f'{r.name()}_{feat["ij"]}.tif')} #variavel global
            
            results.append(processing.run(id, alg_params))
            grid.removeSelection()
        
        return results
        

    def run_autogrid(self):
        '''
        Cria um grid e recorta o raster a partir dele automaticamente.
        '''
    
        grid = self.make_grid()
        self.clip_by_grid(grid)



