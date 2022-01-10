#Para rodar no console
import sys
sys.path.append(r'R:\03_TOOLS\CODIGOS_PY\tools_car')


import processing
import os
from funcoes import *
from datetime import datetime
from qgis.core import *    

class DigStream:
    '''
    PT/BR
    Classe criada para ser uma ferramenta automática para "escavar" imagens ALOS a partir
    de um vetor de drenagem (preferencialmente o centro do canal) e gerar um shapefile
    modelado a partir desta nova imagem.
    
    INPUT:
    Dicionário com o caminho para o vetor original, caminho de saída e o caminho dos rasters ALOS.
    {'PATH' : Pasta com drenagens <str>,
     'PATH_OUT' : Pasta de saída <str>,
     'PATH_RASTERS' : Pasta com DEMs <str>}
    '''
    
    def __init__(self, params):
        self.path = params['path']
        self.path_out = params['path_out']
        self.path_rasters = params['path_rasters']
    
        #Diretório temporário
        self.temporary = os.path.join(self.path_out,'temp')
        if not(os.path.exists(self.temporary)):
            os.mkdir(self.temporary)
            

    def buffering(self, layer, distance=0.00022):
        '''
        PT/BR
        Realiza Buffer em um vetor (prefencialmente linha)
        
        INPUT:
            layer <str:QgsVectorLayer> : Caminho para camada de entrada
            distance <float> : Distância para aplicar o buffer
        
        RETURN:
            path <str> : caminho da camada de saída
        '''
        
        id = 'native:buffer'
        params = {'INPUT': layer,
                  'DISTANCE' : distance,  #default de 25m em graus
                  'SEGMENTS' : 5,
                  'END_CAP_STYLE' : 0,
                  'JOIN_STYLE' : 0,
                  'MITER_LIMIT' : 2,
                  'DISSOLVE' : False,
                  'OUTPUT' : os.path.join(self.temporary,'{}_buffer.shp'.format(layer.name()))}
        
        result = processing.run(id, params)
        
        return result['OUTPUT']


    def rasterizar(self, layer, alos, burn=-15):
        '''
        PT/BR
        Rasteriza uma camada de vetor para uma resolução e um extent de camda
        já exitente.
        OBS.: Preenche valor NoData com "0".

        INPUT:
            layer <str:QgsVectorLayer> : Caminho para camada de entrada (ser raterizada)
            alos <str:QgsRasterLayer> : Caminho para imagem para seguir os parametos (alos da bacia)
            burn <int> : Valor para gravar a imagem (tamanho do vale)    DEFAULT:-15

        RETURN:
            path <str> : caminho de saída da imagem
        '''
        id1 = 'gdal:rasterize'
        params = {'INPUT' : layer,
                  'BURN' : burn,
                  'UNITS' : 0,
                  'WIDTH' : alos.width(),
                  'HEIGHT' : alos.height(),
                  'EXTENT' : alos.extent(),
                  'DATA_TYPE': 1,
                  'OUTPUT': os.path.join(self.temporary,'{}_toraster.tif'.format(layer.name()))}
                  
        result = processing.run(id1, params)
        
        id2 = 'native:fillnodata'
        params2 = {'INPUT' : result['OUTPUT'],
                   'BAND' : 1,
                   'FILL_VALUE' : 0,
                   'OUTPUT' : os.path.join(self.temporary,'{}_rasterfill.tif'.format(layer.name()))}
        
        result = processing.run(id2, params2)
        return result['OUTPUT']


    def raster_sum(self, raster1, raster2):
        '''
        PT/BR
        Soma dois rasters, a fim de gerar um vale no original.
        A ordem é indiferente.

        INPUT:
            raster1 <QgsRasterLayer>
            raster2 <QgsRasterLayer>
            path_out <str> : caminho de saída
        
        OUTPUT:
            path <str> : caminho de saída da imagem

        '''
        id = 'gdal:rastercalculator'
        params = { 'INPUT_A' : raster1, 
                    'BAND_A' : 1,
                    'INPUT_B' : raster2, 
                    'BAND_B' : 1,
                    'FORMULA': 'A + B',
                    'RTYPE' : 1,
                   'OUTPUT' : os.path.join(self.temporary,'{}_alosdig.tif'.format(raster1.name()))}
        
        result = processing.run(id, params)
        return result['OUTPUT']


    def to_dig(self, layer, alos):
        '''
        PT/BR
        Ferramenta para automatizar os processos:

        1) Buffer do vetor original
        2) Rasterizar resultado de (1)
        3) Somar a imagem original com (2).

        INPUT:
            layer <str:QgsVectorLayer> : Caminho para camada para cavar
            path_out <str> : Pasta para depositar o resultado e subprodutos
            alos <str:QgsRasterLayer> : Caminho para a imagem base (alos)
        
        OUTPUT:
            <QgsRasterLayer> : Imagem cavada 
        '''

        primeiro = self.buffering(layer)
        layer = QgsVectorLayer(primeiro, layer.name()) #Nome: baciasn4_NUM

        segundo = self.rasterizar(layer, alos)
        rasterizado = QgsRasterLayer(segundo, layer.name()) #Nome: baciasn4_NUM

        terceiro = self.raster_sum(alos, rasterizado)
        alos_cavado = QgsRasterLayer(terceiro, alos.name()) #Nome: NUM
        
        return alos_cavado


    def batch_alos(self):
        '''
        PT/BR
        Realiza a função to_dig() em lote, para todos os vetores e rasters de uma pasta
        OBS.: É preciso que o nome dos rasters estejam consistentes com o nome dos shapefiles.

        INPUT:
            path <str> : Caminho com os shapefiles
            path_rasters <str> : Caminho com os rasters para serem cavados
            path_out <str> : Caminho para depositar os resultados

        RETURN
            <list:QgsRasterLayer> : Lista com todos os rasters processados
        '''
        path = self.path
        path_rasters = self.path_rasters
        
        shapes = get_shapes(path)
        novos_alos = []
        
        for shp in shapes:
            layer = QgsVectorLayer(os.path.join(path,shp), shp[0:-4])
            num_bacia = str(get_num(layer.name()))
            
            path_raster = os.path.join(path_rasters, 'recorteestudo_{}.tif'.format(num_bacia))
            alos = QgsRasterLayer(path_raster, num_bacia) 
            novos_alos.append(self.to_dig(layer, alos))
            
        return novos_alos


    def run_unique(self):
        '''
        PT/BR
        Realiza o processo de "cavar" o modelo para um único arquivo
        e gera um shapefile com a drenagem utilizando os parametros oferecidos.
        
        RETURN:
            <str> : Caminho do shapefile de saída
        '''
        shp = get_shapes(self.path)[0]
        layer = QgsVectorLayer(os.path.join(self.path,shp), shp[0:-4])
        num_bacia = str(get_num(layer.name()))

        path_raster = os.path.join(self.path_rasters, 'recorteestudo_{}.tif'.format(num_bacia))
        alos = QgsRasterLayer(path_raster, num_bacia)
        
        alos_dig = self.to_dig(layer, alos)
        
        drain = grass_streamextract(alos_dig, self.path_out)
        
        return drain


    def run(self):
        '''
        PT/BR
        Realiza o processo de "cavar" o modelo para todos os arquivos na pasta de entrada.
        
        RETURN:
            <list> : Lista de caminho de todos os shapefiles de drenagem.
        '''

        self.arquivos = self.batch_alos()
        new_folder = os.path.join(self.path_out, 'drenagens')
        if not(os.path.exists(new_folder)):
            os.mkdir(new_folder)
        
        path_out_drenagens = new_folder
        results = []
        
        for alos in self.arquivos:
            results.append(grass_streamextract(alos, path_out_drenagens))
        #results.append(grass_streamextract(alos, path_out_drenagens) for alos in self.arquivos)
    
        return results


#A partir daqui, é preciso usar o código auto_clip e a limpeza via ArcGis