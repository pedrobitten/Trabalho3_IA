#!/usr/bin/env python

"""GameAI.py: INF1771 GameAI File - Where Decisions are made."""
#############################################################
#Copyright 2020 Augusto Baffa
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#############################################################
__author__      = "Augusto Baffa"
__copyright__   = "Copyright 2020, Rio de janeiro, Brazil"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "abaffa@inf.puc-rio.br"
#############################################################

import random
from Map.Position import Position
from enum import Enum
from typing import List, Dict
import csv

# <summary>
# Game AI Example
# </summary>
class GameAI():

    player = Position()
    state = "ready"
    dir = "north"
    score = 0
    energy = 0

    observacoes_atuais = []
    estado_atual = 'Exploracao'
    mundo = {}

    #Sequencia de ataques
    attack_streak = 0
    max_attack_streak = 3  

    caminho = []
    visitado = set()
    perigo = set()
    posicoes_ouro_power_up = []

    log_path = "game_log.csv"
    turn_counter = 1

    # <summary>
    # Refresh player status
    # </summary>
    # <param name="x">player position x</param>
    # <param name="y">player position y</param>
    # <param name="dir">player direction</param>
    # <param name="state">player state</param>
    # <param name="score">player score</param>
    # <param name="energy">player energy</param>
    def SetStatus(self, x: int, y: int, dir: str, state: str, score: int, energy: int):
        
        self.SetPlayerPosition(x, y)
        self.dir = dir.lower()

        self.state = state
        self.score = score
        self.energy = energy


    # <summary>
    # Get list of observable adjacent positions
    # </summary>
    # <returns>List of observable adjacent positions</returns>
    def GetCurrentObservableAdjacentPositions(self) -> List[Position]:
        return self.GetObservableAdjacentPositions(self.player)
        
    def GetObservableAdjacentPositions(self, pos):
        ret = []

        ret.append(Position(pos.x - 1, pos.y))
        ret.append(Position(pos.x + 1, pos.y))
        ret.append(Position(pos.x, pos.y - 1))
        ret.append(Position(pos.x, pos.y + 1))

        return ret


    # <summary>
    # Get list of all adjacent positions (including diagonal)
    # </summary>
    # <returns>List of all adjacent positions (including diagonal)</returns>
    def GetAllAdjacentPositions(self):
    
        ret = []

        ret.append(Position(self.player.x - 1, self.player.y - 1))
        ret.append(Position(self.player.x, self.player.y - 1))
        ret.append(Position(self.player.x + 1, self.player.y - 1))

        ret.append(Position(self.player.x - 1, self.player.y))
        ret.append(Position(self.player.x + 1, self.player.y))

        ret.append(Position(self.player.x - 1, self.player.y + 1))
        ret.append(Position(self.player.x, self.player.y + 1))
        ret.append(Position(self.player.x + 1, self.player.y + 1))

        return ret

    def NextPositionAhead(self, steps):
        ret = None
        if self.dir == "north":
            ret = Position(self.player.x, self.player.y - steps)
        elif self.dir == "east":
            ret = Position(self.player.x + steps, self.player.y)
        elif self.dir == "south":
            ret = Position(self.player.x, self.player.y + steps)
        elif self.dir == "west":
            ret = Position(self.player.x - steps, self.player.y)
        return ret

    # <summary>
    # Get next forward position
    # </summary>
    # <returns>next forward position</returns>
    def NextPosition(self) -> Position:
        return self.NextPositionAhead(1)
        
    def NextPosition(self):
    
        ret = None
        
        if self.dir == "north":
            ret = Position(self.player.x, self.player.y - 1)
                
        elif self.dir == "east":
                ret = Position(self.player.x + 1, self.player.y)
                
        elif self.dir == "south":
                ret = Position(self.player.x, self.player.y + 1)
                
        elif self.dir == "west":
                ret = Position(self.player.x - 1, self.player.y)

        return ret
    

    # <summary>
    # Player position
    # </summary>
    # <returns>player position</returns>
    def GetPlayerPosition(self):
        return Position(self.player.x, self.player.y)


    # <summary>
    # Set player position
    # </summary>
    # <param name="x">x position</param>
    # <param name="y">y position</param>
    def SetPlayerPosition(self, x: int, y: int):
        self.player.x = x
        self.player.y = y
    

    # <summary>
    # Observations received
    # </summary>
    # <param name="o">list of observations</param>
    def GetObservations(self, o: List[str]):
        """
        Processa as observações sensoriais recebidas e atualiza a Base de Conhecimento (self.world).
        """
        # Garante que as observações são tratadas como lista (o or [] para evitar None)
        self.observacoes_atuais = o or []
        
        # Zera a sequência de ataque se houver confirmação de acerto de tiro.
        if any(s == 'hit' or s.startswith('hit') for s in self.observacoes_atuais):
            self.attack_streak = 0

        # Posição atual do agente
        pos_x = self.player.x
        pos_y = self.player.y
        pos_atual = (pos_x, pos_y)

        # 1. Inicializa/Atualiza a Célula Atual no Mundo
        # Define os valores padrão se a célula for nova (setdefault)
        tile = self.mundo.setdefault(pos_atual, {
            'visited': True, 'danger': None, 'treasure': False, 'powerup': False, 'enemy': None
        })
        tile['visited'] = True

        # 2. Interpreta as Observações e Realiza Inferências
        for s in self.observacoes_atuais:
            s_lower = s.lower()
            
            # --- Inferência de Perigos Adjacentes (Brisa e Flash) ---
            if s_lower == "breeze":
                # Brisa indica Poço (Pit) adjacente
                for adj in self.GetObservableAdjacentPositions(self.player):
                    pos = (adj.x, adj.y)
                    self.perigo.add(pos) # Adiciona à lista geral de perigos
                    self.mundo.setdefault(pos, {})['danger'] = 'pit'
                    
            elif s_lower == "flash":
                # Flash indica Teletransporte (Teleport) adjacente
                for adj in self.GetObservableAdjacentPositions(self.player):
                    pos = (adj.x, adj.y)
                    self.perigo.add(pos)
                    self.mundo.setdefault(pos, {})['danger'] = 'teleport'
                    
            # --- Confirmação de Obstáculo ---
            elif s_lower == "blocked":
                # Movimento bloqueado, marca a célula à frente como 'blocked'
                next_pos = self.NextPosition()
                if next_pos is not None:
                    next_coord = (next_pos.x, next_pos.y)
                    self.perigo.add(next_coord)
                    self.mundo.setdefault(next_coord, {})['danger'] = 'blocked'
                    
            # --- Detecção de Itens (na célula atual) ---
            elif s_lower == "bluelight":
                # Azul indica Tesouro/Ouro
                tile['treasure'] = True
                if pos_atual not in self.posicoes_ouro_power_up:
                    self.posicoes_ouro_power_up.append(pos_atual)
                    
            elif s_lower == "redlight":
                # Vermelho indica Power-up
                tile['powerup'] = True
                if pos_atual not in self.posicoes_ouro_power_up:
                    self.posicoes_ouro_power_up.append(pos_atual)
                    
            # --- Detecção de Inimigo ---
            elif s_lower.startswith("enemy#") or s_lower == "enemy":
                # Marca presença de inimigo na direção atual (Inimigo na mira)
                tile['enemy'] = self.dir
                
            # --- Outras Observações (steps, damage, hit, etc.) ---
            # (As outras observações como 'steps', 'damage', 'hit' podem ser processadas aqui
            # mas apenas o 'hit' requer uma ação interna (resetar attack_streak), que já foi tratada acima.)
        
        # Opcional: Aqui, você pode remover a marcação de 'danger' de células adjacentes
        # se o agente tiver certeza de que não há perigo ali (lógica de Wumpus World).


    # <summary>
    # No observations received
    # </summary>
    def GetObservationsClean(self):
    
        self.observacoes_atuais = []
    

    # <summary>
    # Get Decision
    # </summary>
    # <returns>command string to new decision</returns>
    def GetDecision(self) -> str:
        """
        Decide a próxima ação com base na Máquina de Estados de Prioridade.
        """
        pos_x = self.player.x
        pos_y = self.player.y

        # --- PRIORIDADE 1: COLETA (Item na célula atual) ---
        
        # Ouro/Tesouro
        if self.mundo.get((pos_x, pos_y), {}).get('treasure'):
            # self.mundo[(x, y)]['treasure'] = False # Não deve ser responsabilidade do GetDecision, mas mantenho por consistência com o código do usuário
            return self._log_and_return("pegar_ouro")
            
        # Powerup
        if self.mundo.get((pos_x, pos_y), {}).get('powerup'):
            # self.mundo[(x, y)]['powerup'] = False # Não deve ser responsabilidade do GetDecision
            return self._log_and_return("pegar_powerup")
        
        # --- PRIORIDADE 2: FUGINDO (Evitar Poços/Teletransportes) ---
        # Se sentir um perigo (breeze/flash) na célula atual, o movimento mais seguro é recuar ou virar.
        if 'breeze' in self.observacoes_atuais or 'flash' in self.observacoes_atuais:
            # Tenta recuar (andar_re) para sair do perigo inferido nas adjacências
            if 'blocked' not in self.observacoes_atuais:
                return self._log_and_return("andar_re")
            # Se não puder recuar (por estar bloqueado), apenas vira para reavaliar a situação
            return self._log_and_return("virar_direita")
            
        # --- PRIORIDADE 3: COMBATE (Atirar se na mira) ---
        enemy_on_sight = any(s.startswith("enemy") for s in self.observacoes_atuais)
        
        if enemy_on_sight and self.attack_streak < self.max_attack_streak:
            self.attack_streak += 1
            return self._log_and_return("atacar")
            
        # Se ouvir passos, mas não ver o inimigo, vira para tentar colocá-lo na mira.
        if 'steps' in self.observacoes_atuais and not enemy_on_sight:
            return self._log_and_return("virar_direita")


        # --- PRIORIDADE 4: EXPLORAÇÃO (Mover para célula segura e não visitada) ---
        
        # Encontra todos os movimentos adjacentes seguros e não visitados
        safe_unvisited_moves = []
        for adj in self.GetObservableAdjacentPositions(self.player):
            pos = (adj.x, adj.y)
            danger = self.mundo.get(pos, {}).get('danger')
            
            # Condição de segurança: não visitado E perigo NÃO é poço, teletransporte ou bloqueio
            if pos not in self.visitado and danger not in ('pit', 'teleport', 'blocked'):
                 # Adiciona a adjacência à lista de movimentos seguros
                safe_unvisited_moves.append(adj)
                
        if safe_unvisited_moves:
            # Escolhe um movimento seguro aleatoriamente
            adj = random.choice(safe_unvisited_moves)
            self.caminho.append((pos_x, pos_y)) # Adiciona a posição atual ao histórico para backtracking
            
            # Converte a posição alvo na ação de movimento necessária (andar, virar, etc.)
            acao = self.move_direction_to(adj)
            return self._log_and_return(acao)

        # --- PRIORIDADE 5: BACKTRACKING (Se não houver movimento seguro à vista) ---
        
        if self.caminho:
            # Pega o nó anterior e remove do path (retorna)
            prev = self.caminho.pop() 
            
            # Move-se para a posição anterior
            acao = self.move_direction_to(Position(prev[0], prev[1]))
            return self._log_and_return(acao)

        # --- PRIORIDADE 6: EXPLORAÇÃO ARRISCADA (Tentar células com perigo conhecido) ---
        
        risky_unvisited_moves = []
        for adj in self.GetObservableAdjacentPositions(self.player):
            pos = (adj.x, adj.y)
            danger = self.mundo.get(pos, {}).get('danger')
            
            # Condição: não visitado E perigo NÃO é bloqueio. Assumimos o risco de poço/teletransporte.
            if pos not in self.visitado and danger not in ('blocked',):
                risky_unvisited_moves.append(adj)
                
        if risky_unvisited_moves:
            adj = random.choice(risky_unvisited_moves)
            self.caminho.append((pos_x, pos_y))
            acao = self.move_direction_to(adj)
            return self._log_and_return(acao)

        # --- PRIORIDADE 7: MOVIMENTO ALEATÓRIO (Último Recurso) ---
        
        # Totalmente preso, apenas vira ou anda de forma aleatória
        acao = random.choice(["virar_direita", "virar_esquerda", "andar"])
        return self._log_and_return(acao)
    
    def move_direction_to(self, target_pos):
        # Calcula ação necessária para mover na direção de target_pos
        dx = target_pos.x - self.player.x
        dy = target_pos.y - self.player.y
        if dx == 1:
            return "andar" if self.dir == "east" else "virar_direita"
        if dx == -1:
            return "andar" if self.dir == "west" else "virar_esquerda"
        if dy == 1:
            return "andar" if self.dir == "south" else "virar_direita"
        if dy == -1:
            return "andar" if self.dir == "north" else "virar_esquerda"
        return "andar"

# Note: Esta função depende da importação 'import csv' no seu arquivo.
    def _log_and_return(self, action: str) -> str:
        """
        Registra a ação atual, observações e status do agente em um log CSV 
        e retorna a ação para execução.
        """
        
        # Formata as observações em uma única string separada por ponto e vírgula
        obs_str = ";".join(self.observacoes_atuais)
        
        # Dados a serem registrados no log
        log_data = [
            self.turn_counter,
            self.player.x,
            self.player.y,
            self.dir,
            self.energy,
            self.score,
            obs_str,
            action
        ]
        
        # Abre o arquivo de log no modo de anexação ('a')
        try:
            with open(self.log_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(log_data)
        except Exception as e:
            # Em caso de erro de arquivo, exibe no console para cumprir o requisito de log em tela
            print(f"ERRO DE LOG: Não foi possível escrever no arquivo {self.log_path}. Detalhe: {e}")
            
        # Incrementa o contador de turno para o próximo ciclo
        self.turn_counter += 1
        
        # Exibe o log em tela (cumprindo o requisito do INF1771)
        print(f"TURNO {self.turn_counter-1} | POS: ({self.player.x},{self.player.y}) | AÇÃO: {action} | OBS: {obs_str}")

        return action