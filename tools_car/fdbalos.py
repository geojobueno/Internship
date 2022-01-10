import processing
import os
from datetime import datetime
from qgis.core import *

def get_num(string):
    return [int(s) for s in string.split('_') if s.isdigit()][0]

def buffering(layer, path_out, distance=0.00022):
    id = 'native:buffer'
    params = {'INPUT': layer,
              'DISTANCE' : distance,  #default de 25m em graus
              'SEGMENTS' : 5,
              'END_CAP_STYLE' : 0,
              'JOIN_STYLE' : 0,
              'MITER_LIMIT' : 2,
              'DISSOLVE' : False,
              'OUTPUT' : os.path.join(path_out,'{}_buffer.shp'.format(layer.name()))}
    
    result = processing.run(id, params)
    
    return result['OUTPUT']

def rasterizar(layer, path_out, alos, burn=-15):
    id1 = 'gdal:rasterize'
    params = {'INPUT' : layer,
              'BURN' : burn,
              'UNITS' : 0,
              'WIDTH' : alos.width(),
              'HEIGHT' : alos.height(),
              'EXTENT' : alos.extent(),
              'DATA_TYPE': 1,
              'OUTPUT': os.path.join(path_out,'{}_toraster.tif'.format(layer.name()))}
              
    result = processing.run(id1, params)
    
    id2 = 'native:fillnodata'
    params2 = {'INPUT' : result['OUTPUT'],
               'BAND' : 1,
               'FILL_VALUE' : 0,
               'OUTPUT' : os.path.join(path_out,'{}_rasterfill.tif'.format(layer.name()))}
    
    result = processing.run(id2, params2)
    return result['OUTPUT']

def raster_sum(raster1, raster2, path_out):
    expression = '\"{}@1" + \"{}@1"'.format(raster1.name(), raster2.name())
    id = 'gdal:rastercalculator'
    params = { 'INPUT_A' : raster1, 
                'BAND_A' : 1,
                'INPUT_B' : raster2, 
                'BAND_B' : 1,
                'FORMULA': 'A + B',
                'RTYPE' : 1,
               'OUTPUT' : os.path.join(path_out,'{}_alosdig.tif'.format(raster1.name()))}
    
    result = processing.run(id, params)
    return result['OUTPUT']

def to_dig(layer, path_out, alos):
    primeiro = buffering(layer, path_out)
    layer = QgsVectorLayer(primeiro, layer.name()) #Nome: baciasn4_NUM

    segundo = rasterizar(layer, path_out, alos)
    rasterizado = QgsRasterLayer(segundo, layer.name()) #Nome: baciasn4_NUM

    terceiro = raster_sum(alos, rasterizado, path_out)
    alos_cavado = QgsRasterLayer(terceiro, alos.name()) #Nome: NUM
    
    return alos_cavado

def get_shapes(path):
    list = os.listdir(path)
    shapes = [arquivo for arquivo in list if arquivo[-4:] == '.shp']
    return shapes

def batch_alos(path, path_rasters, path_out):
    shapes = get_shapes(path)
    novos_alos = []
    
    for shp in shapes:
        layer = QgsVectorLayer(os.path.join(path,shp), shp[0:-4])
        num_bacia = str(get_num(layer.name()))
        
        path_raster = os.path.join(path_rasters, 'recorteestudo_{}.tif'.format(num_bacia))
        alos = QgsRasterLayer(path_raster, num_bacia) 
        novos_alos.append(to_dig(layer, path_out, alos))
        
    return novos_alos

def grass_streamextract(raster, path_out, limiar=2500, mexp=2, lenght=3,
                stream_raster= None):
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

path = r'D:\00_BASE_SIG\MG insumo\drenagens_bacias' #Caminho de onde estão as drenagens por bacia
path_out = r'D:\00_BASE_SIG\MG insumo\imagens' #Pasta para sair subprodutos
path_rasters = r'D:\01_BASE_RASTER\ALOS\ALOS_BACIA_N4\raster_alos_4674' #Pasta onde estão as imagens ALOS

arquivos = batch_alos(path, path_rasters, path_out)
path_out = r'D:\00_BASE_SIG\MG insumo\extract' #Caminho onde serão depositadas shapes de drenagem

for alos in arquivos:
    print(alos)
    grass_streamextract(alos, path_out)

print('fim')
#A partir daqui, é preciso usar o código auto_clip e a limpeza via ArcGis