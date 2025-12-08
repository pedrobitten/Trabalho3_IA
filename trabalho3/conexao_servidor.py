class ConexaServidor:

    def __init__(self, host, port):

        #Parametros de conexao
        self.host = host
        self.port = port
        self.socket = None
        self.conectado = False

        #Conexao
        self.conectar()

        self.ultima_observacao = []

    #Estabelece conexao com o servidor
    def conectar(self):

        try:

            print(f"Tentando conectar a {self.host} : {self.port}...")

            self.conectado = True
            print("Conectado com sucesso!")

        except Exception as e:

            print(f"Erro de conexao: {e}")
            self.conectado = False

    #Envia um comando de texto ao servidor e espera pela resposta
    def enviar_comando(self, comando):

        if not self.conectado:

            print("Erro: Nao conectado ao servidor")
            return None
        
        comando_formatado = f"{comando}\n"

        return comando_formatado.strip()
    
    #Anda para frente
    def sendForward(self):

        return self.enviar_comando("W")
    
    #Vira a esquerda
    def sendTurnLeft(self):

        return self.enviar_comando("A")
    
    #Atira
    def sendShoot(self):

        return self.enviar_comando("E")
    
    #Pega item
    def sendGetItem(self):

        return self.enviar_comando("T")
    
    # --- Comandos de observacao e Status ---

    #Recebe as informacoes do mundo ao redor
    def sendRequestObservation(self):

        raw_obs = self.enviar_comando("O")
        
        if raw_obs:

            return raw_obs.lower().split(";")
        
        return []
    
    #Recebe status do agente
    def sendRequestUserStatus(self):

        return self.enviar_comando("P")

    #Desconecta do jogo
    def sendGoodbye(self):

        self.enviar_comando("QUIT")

