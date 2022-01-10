import processing
from qgis.core import *
import numpy as np
import os

#Constantes
pi = np.pi

#Funções universais
def get_num(string, split='_'):
        '''
        PT/BR
        Retorna primeiro número dentro de uma string
        
        INPUT:
            string <str>
            split <str> : Onde cortar a string - Default: '_'
        
        RETURN:
            Primeiro número encontrado <int>
        '''
        
        return [int(s) for s in string.split(split) if s.isdigit()][0]


def get_shapes(path):
    '''
    PT/BR
    Retorna todos os shapefiles de uma pasta.
    INPUT:
        path <str> : Pasta com shapefiles
    RETURN:
        <list> : Lista com todos os shapes da pasta
    '''
    list = os.listdir(path)
    shapes = [arquivo for arquivo in list if arquivo[-4:] == '.shp']
    return shapes


def grass_streamextract(raster, path_out, limiar=2000, mexp=2, lenght=1,
                stream_raster= None):
    '''
    PT/BR
    Função para gerar a drenagem a partir de um DEM, usando a função GRASS:STREAMEXTRACT

    INPUT:
        raster <str:QgsRasterLayer> <QgsRasterLayer> : Modelo de elevação
        path_out <str> : Pasta de saída
        limiar <int> : Parâmetro para acumulação mínima de fluxo
        mexp <int> : Expoente de Montgomery
        --length <int> : Comprimento mínimo para gerar drenagem (pixels)
        --stream_raster <str> : Caminho para depositar raster de drenagem

    RETURN:
        <str> : Caminho do shapefile de saída
    '''
    id = 'grass7:r.stream.extract'
    params =  {
            'GRASS_OUTPUT_TYPE_PARAMETER': 2,
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'GRASS_VECTOR_DSCO': '',
            'GRASS_VECTOR_EXPORT_NOCAT': False,
            'GRASS_VECTOR_LCO': '',
            'accumulation': None,
            'd8cut': None,
            'depression': None,
            'elevation': raster,  #RASTER DE ENTRADA
            'memory': 25000,
            'mexp': mexp,
            'stream_length': lenght,
            'stream_raster': stream_raster,
            'threshold': limiar,
            'stream_vector': os.path.join(path_out, raster.name()+'fluxo.gpkg')
        }
    result = processing.run(id, params)
    
    id2 = 'gdal:convertformat'
    params2 = {'INPUT':params['stream_vector'],
                'POTIONS':'',
                'OUTPUT':os.path.join(path_out, raster.name()+'fluxo.shp')}
    result = processing.run(id2, params2)
    
    return result['OUTPUT']