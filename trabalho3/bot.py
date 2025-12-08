from conexao_servidor import ConexaServidor
from mapa import MapaInterno


class Bot():

    def __init__(self):
        
        #Caracteristicas do bot
        #self.cor
        self.nome = "BOT 6767"

        #Conexao ao servidor
        self.conexao = ConexaServidor("atari.icad.puc-rio.br", 8888)

        #Estado do agente
        self.energia = 100
        self.pontuacao = 0
        self.direcao = 'Norte'
        self.posicao_estimada = (0, 0) #Mudar a posicao depois

        self.mapa = MapaInterno()
        self.perigos_conhecidos = {}

        #Máquinas de estados
        self.estado_atual = 'Exploracao'
        self.meta_atual = None

    #Controle do agente
    def executar(self):

        while self.conexao.conectado:

            #Observar
            observacoes = self.conexao.sendRequestObservation()

            #Atualizar estado interno
            self.atualizar_mapa(observacoes)
            self.atualizar_status_agente()

            #Tomada de decisao
            acao = self.decidir_acao()

            #Executar acao
            self.conexao.enviar_comando(acao)

    #Processa as observacoes dos sensores para construir/atualizar o mapa
    def atualizarMapa(self, observacoes):

        if 'breeze' in observacoes:

            self.mapa.marcaAdjacentesPorSensor(self.posicao_estimada, 'Poco')

        if 'flash' in observacoes:

            self.mapa.marcaAdjacentesPorSensor(self.posicao_estimada, 'Teletransporte')

        if 'blocked' in observacoes:

            self.mapa.marcaBloqueioAFrente(self.posicao_estimada, self.direcao)


    #Lógica central: transição de estados e escolha de ação.
    def decidir_acao(self):
        
        observacoes = self.conexao.ultima_observacao
        
        # --- 1. Lógica de Transição de Estados (Prioridade) ---
        
        # Prioridade 1: PERIGO (evitar poços e teletransportes)
        if 'breeze' in observacoes or 'flash' in observacoes: 
            self.estado_atual = 'FUGINDO'
        
        # Prioridade 2: COMBATE (inimigo visível ou próximo)
        elif 'enemy' in observacoes or 'steps' in observacoes: 
            self.estado_atual = 'COMBATE'
             
        # Prioridade 3: COLETA (item na posição atual)
        elif 'blueLight' in observacoes or 'redLight' in observacoes: 
             self.estado_atual = 'COLETA'
        
        # Prioridade 4: EXPLORAÇÃO (Estado padrão se não houver emergências)
        elif self.estado_atual != 'FUGINDO' and self.estado_atual != 'COMBATE':
             self.estado_atual = 'EXPLORACAO'
             
        # --- 2. Escolha da Ação baseada no Estado ---
        
        if self.estado_atual == 'FUGINDO':
            # Volta para a célula anterior segura ou usa Busca A* para uma área livre de perigo.
            return self.fugir_do_perigo() 
            
        elif self.estado_atual == 'COMBATE':
            # Resposta à sua pergunta: Não, você não deve substituir por sendShoot() diretamente. 
            # Você precisa de lógica: atirar (se na mira) ou virar (se apenas próximo).
            return self.luta_e_fuga()

        elif self.estado_atual == 'COLETA':
            # Ação: Pegar o item
            return self.conexao.sendGetItem() 
            
        elif self.estado_atual == 'EXPLORACAO':
            # Usa A* para encontrar o caminho para o próximo ponto de exploração.
            destino = self.mapa.proximo_ponto_desconhecido()
            
            # Se a Busca A* falhar ou não houver destino conhecido (início de jogo), move-se aleatoriamente
            if destino is None:
                return self.mover_aleatorio_seguro()
            
            return self.planejar_e_mover_AStar(destino=destino)
        
        # Retorno de segurança
        return self.conexao.sendRequestObservation() # Se nada for decidido, apenas observe.
    
    #Terminar decidir acao
    #Fazer classe A*