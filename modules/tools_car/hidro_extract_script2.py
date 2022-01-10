"""
Author: Joao P. Bueno
Codigo para extrair drenagem em batch a partir de imagens ALOS
"""

import processing
import os
from datetime import datetime
from qgis.core import *

uf = "DF"
bacias = {"GO":["1350932","1350126","1350127","1351388",
                "1351389","1351390","1351393"],
                
          "MT":["1349179","1349180","1349181",
                "1349182","1349183","1349184","1349155",
                "1349166","1349169","1349170","1349171",
                "1349172","1349185","1349186","1349187",
                "1349188","1349189","1349190","1351457",
                "1351459","1351461","1351462","1351466",
                "1351467","1351468","1351469","1351470",
                "1351471","1351472","1351473","1351474"],

          
          "PI":["1350716","1350717",
                "1350718","1350719","1350720","1350721",
                "1350777","1350779","1350783","1350784",
                "1350754","1350755","1350757","1350876"],
          
          "TO":["1350128","1350129","1350130","1350308",
                "1350131","1350132","1350133","1350153",
                "1350160","1350201","1350182","1350183",
                "1350184","1350185","1350190","1350203",
                "1350204","1350205","1350206","1350207",
                "1350208","1350214","1350212","1350216",
                "1350218","1350221","1350222","1350223",
                "1350224","1350225","1350226","1350243",
                "1350244","1350229","1350230","1350231",
                "1350232","1350233","1350241","1350249",
                "1350250","1350251","1350259","1350261",
                "1350289","1350168","1350046","1350047",
                "1350049","1350083","1350084","1350186",
                "1350169","1350154","1350155","1350156",
                "1350157","1350158","1350170","1350171",
                "1350172","1350187","1350188","1350159",
                "1350161","1350162","1350163","1350213",
                "1350164","1350165","1350166","1350189",
                "1350191","1350192","1350194","1350196",
                "1350198","1350200","1350202","1350220",
                "1350211","1350215","1350217","1350219",
                "1350227","1350228","1350234","1350239",
                "1350240","1350242","1350258","1350260",
                "1350262","1350264","1350274","1350276",
                "1350277","1350286","1350288","1350290",
                "1350291","1350292","1350302","1350303",
                "1350304","1350305","1350306","1350307"],
          
          "MA":["1350552","1350639","1350661","1350662","1350663","1350664","1350665",
                "1350666","1350667","1350668","1350669","1350670","1350671","1350672",
                "1350684","1350686","1350654","1350655","1350656","1350657","1350658",
                "1350659","1350660","1350709","1350712","1350635","1350637","1350553",
                "1350554","1350555","1350556","1350559","1350640","1350641","1350642",
                "1350643","1350644","1350645","1350646","1350651","1350634","1350636",
                "1350638","1350652","1350653","1350673","1350674","1350675","1350676",
                "1350677","1350678","1350679","1350680","1350681","1350682","1350683",
                "1350685","1350695","1350696","1350697","1350698","1350699","1350700"],

          "MG": ["1350911","1350912",
                "1350913","1350914","1350915","1350916",
                "1350917","1350918","1350919","1350938",
                "1350939","1350995","1351008","1351015",
                "1351016","1351017","1351018","1351024",
                "1351010","1351012","1351013","1351014"],

          "BA":["1350893","1350894",
                "1350895","1350896","1350897","1350898",
                "1350899","1350902","1350903","1350904",
                "1350905","1350906","1350961","1350975",
                "1350979","1350980","1350981","1350982",
                "1350994","1350996","1350997","1351000",
                "1350871","1350873","1350874","1350875",
                "1350876","1350877","1350881","1350884",
                "1350885","1350886","1350887","1350888",
                "1350889","1350890","1350891","1350892"],

          "DF":["1350932","1350117","1350118","1350100","1351390"]}


inicial = datetime.now()
path_in = r'D:\ALOS\ALOS_BACIA_N4\raster_alos_4674'
name = os.listdir(path_in)[:] 

path_out = r'D:\rios_simples_pilotoPI\novo_alos'

if not(os.path.exists(path_out)):
    os.mkdir(path_out)
#
#else:
#    print('PASTA JA EXISTENTE, ERRO CAUSADO PROPOSITALMENTE:')
#    print(arrume_o_caminho)
processadas = []

parametros_extract =  {
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
            'elevation': None,  #RASTER DE ENTRADA
            'memory': 25000,
            'mexp': 2,
            'stream_length': 1,
            'stream_raster': None,
            'threshold': 2000,
            'stream_vector': None
        }

prioridade = bacias[uf]
prioridade = os.listdir(r'D:\rios_simples_pilotoPI\novo_alos')

log_file = open(os.path.join(path_out,'log.txt'), 'w')
log_file.write('R.STREAM.EXTRACT - PARÂMETROS ESTABELECIDOS: \n{} : {}\n{} : {}\n{} - {}\n'.format('threshold',parametros_extract['threshold'],'mexp'
                                                            ,parametros_extract['mexp'],'stream_length', parametros_extract['stream_length']))
log_file.write('PROCESSO INICIADO EM: {}\n'.format(str(datetime.now())))

for raster in prioridade:
#    raster = 'recorteestudo_{}'.format(raster)
#    
#    if int(raster[14:]) in processadas:
#        print('{} já foi processado'.format(raster))
#        #continue
    
    raster_path = os.path.join(r'D:\rios_simples_pilotoPI\novo_alos', raster)
    area = QgsRasterLayer(raster_path, raster[:7])
    
    if not(area.isValid()):
        print('problema na area')
        continue
        #adicionar esse caminho em um log
    
    tempo = datetime.now()
    log_file.write('{} - {}\n'.format(raster, str(datetime.now())))
    
    parametros_extract['stream_raster'] = os.path.join(path_out, raster+'fluxo.tif')
    parametros_extract['elevation'] = area
    parametros_extract['stream_vector'] = os.path.join(path_out, raster+'fluxo.gpkg')
   
    processing.run('grass7:r.stream.extract', parametros_extract)
    
    tempo = datetime.now() - tempo
    log_file.write('{} PROCESSADA EM {} - {}\n'.format(raster, tempo, str(datetime.now())))

    
    processing.run('gdal:convertformat',{'INPUT':parametros_extract['stream_vector']
        ,'POTIONS':'', 'OUTPUT':os.path.join(path_out, raster+'fluxo.shp')})


    print('{} processado'.format(raster))
    #colocar arquivo de log com sucesso

final = datetime.now() - inicial
log_file.write('-----SCRIPT ENCERRADO-----\n')
log_file.write('HORA ATUAL: {}          -TEMPO DE EXECUÇÃO: {}\n'.format(str(datetime.now()),str(final)))
log_file.write('=-='*25)
log_file.close()
print('FIM')
