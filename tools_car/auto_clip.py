from qgis.utils import *
from qgis.core import *
import processing
import os 

#selecionar a bacia (feature) e cortar a drenagem (vetor de linha)
base_obh_n4 = r'D:\rios_simples_pilotoMT\bacias1.shp' #camada mascara
path_vetores = r'D:\00_BASE_SIG\MG insumo\extract' #CAMINHO PARA PASTA COM OS VETORES DE DRENAGEM
output = r'D:\00_BASE_SIG\MG insumo\clips'  #CAMINHO PARA PRODUTO FINAL
estado = 'MG'

def corte(path_drenagem, bacia, n, id, layer):
    num_bacia = str(n)
    drenagem = QgsVectorLayer(path_drenagem, num_bacia, "ogr")
    
    if not(drenagem.isValid()):
        print('ERRO: Drenagem nao e valida - BACIA {}'.format(num_bacia))
        return path_drenagem, num_bacia
    
    bacia.select(id)
    mask = QgsProcessingFeatureSourceDefinition(todas_bacias.source(),
                                                selectedFeaturesOnly=True)
    alg_params = {"INPUT": drenagem,
                  "OVERLAY": mask,
                  "OUTPUT": os.path.join(output, 'drenagem{}_clip.shp'.format(num_bacia))} #variavel global
    
    processing.run("native:clip", alg_params)
    bacia.removeSelection()
    del mask
    
    print('Bacia {} foi recortada.'.format(num_bacia))
    return alg_params["OUTPUT"]
    
todas_bacias = iface.activeLayer()
saidas = []

for bacia in todas_bacias.getFeatures():
    n = int(bacia['wts_pk'])
    path_drenagem = os.path.join(path_vetores, '{}fluxo.shp'.format(n))
    
    saida = corte(path_drenagem, todas_bacias, n, bacia.id(), todas_bacias) #recorta a partir da camada selecionada
    saidas.append(saida)


params = {'LAYERS': saidas,
          'CRS':  'EPSG:4674',
          'OUTPUT': os.path.join(output,'merged_{}.shp'.format(estado))}
res = processing.run('native:mergevectorlayers', params)

print('{} vetores de bacias foram mesclados'.format(len(saidas)))
print('Script encerrado!!')