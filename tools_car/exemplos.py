'''
Arquivo para guardar exemplos de como usar as classes do código

Síntaxe:

cod_exemplo_NOMEDACLASSE = """ """

'''


cod_exemplo_AutoGrid = '''
                        r = iface.activeLayer()  #raster para cortar
                        ij = (2,1)
                        output = r'C:\SSD-2T\02_RASTER\planet_2021_09\teste_recorte3'

                        params = {'raster' : r,
                                'ij' : ij,
                                'output' : output}

                        ag = AutoGrid(params) #Construção do objeto
                        AutoGrid.run_autogrid() #Fazer o grid e recortar automaticamente
                        #grid = ag.make_grid(r,nx,ny) #Fazer só o grid
                        #ag.clip_by_grid(grid) #Cortar a imagem por um grid qualquer
                       '''

cod_exemplo_DigStream = '''
                            #Dicionário de parâmetros
                            params = {
                                'path': r'R:\00_BASE_SIG\MG insumo\teste_classe\bacias',
                                'path_rasters' : r'R:\01_BASE_RASTER\ALOS\ALOS_BACIA_N4\raster_alos_4674',
                                'path_out': r'R:\00_BASE_SIG\MG insumo\teste_classe'
                            }

                            teste = DigStream(params) #Cria o objeto
                            teste.run() #Faz o processo de gerar drenagem cavada em batch


                            teste.batch_alos() #Apenas modifica o DEM
                        '''