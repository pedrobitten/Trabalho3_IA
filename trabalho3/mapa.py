class MapaInterno:

    def __init__(self, largura=59, altura=34):
        
        #Dimensoes
        self.largura = largura
        self.altura = altura

        #Mapa: mapea apenas as areas visitadas e inferidas
        self.celulas = {}

        #Locais nao visitados
        self.pontos_de_interesse = []

        #Lista de status possiveis para cada celula
        self.status_celula = {

            'Desconhecido' : 0,
            'Livre' : 1,
            'Obstaculo' : 2,
            'Poco_confirmado' : 3, 
            'Possivel_poco' : 4, 
            'Teletransporte_confirmado' : 5, 
            'Possivel_teletransporte' : 6, 
            'Inimigo_visto' : 7, 
            'Item_coletado': 8

        }

    #Retorna status de uma coordenada
    def getCelulaStatus(self, coord):

        return self.celulas.get(coord, self.status_celula['Desconhecido'])
    
    #Define o status de uma coordenada
    def setCelulaStatus(self, coord, status):

        self.celulas[coord] = self.status_celula[status]

    #Marca as 4 celulas adjacentes
    def marcaAdjacentesPorSensor(self, origem, status_inferido):

        coordenada_x, coordenada_y = origem

        adjacentes = [(coordenada_x + 1, coordenada_y), (coordenada_x - 1, coordenada_y), 
                      (coordenada_x, coordenada_y + 1), (coordenada_x, coordenada_y - 1)]
        
        for coord_adj in adjacentes:

            if self.getCelulaStatus(coord_adj) == self.status_celula['Desconhecido']:

                self.setCelulaStatus(coord_adj, status_inferido)

    def calculaCoordenadaAFrente(posicao_x, posicao_y, dir):

        if dir == 'norte':

            return posicao_x, posicao_y + 1
        
        if dir == 'sul':

            return posicao_x, posicao_y - 1
        
        if dir == 'leste':

            return posicao_x + 1, posicao_y
        
        if dir == 'oeste':

            return posicao_x - 1, posicao_y

    #Marca a celula a frente como Obstaculo
    def marcaBloqueioAFrente(self, origem, direcao):
        
        coordenada_x, coordenada_y = origem

        proximo_x, proximo_y = self.calculaCoordenadaAFrente(coordenada_x, coordenada_y, direcao)

        self.setCelulaStatus((proximo_x, proximo_y), 'Obstaculo')

    #Atualiza a posicao atual como livre
    def marcaComoLivreESeguro(self, coord):

        self.setCelulaStatus(coord, 'Livre')

    


