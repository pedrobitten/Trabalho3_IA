## Integrantes do Grupo

Felipe Benevolo - 2110368
Pedro Bittencourt - 2111415
Lucas Rodrigues Pimentel - 1912905

## Implementação de GameAI
- A função GetObservations foi modificada de forma a lidar com asd observações capturadas. No caso de percepção de perigo, ou seja, ao perceber brisa ou  flash (e também no caso de bloqueio), adiciona-se o perigo a um conjunto, além de marcar a posição como perigosa na percepção de mundo do agente. No caso de perceber um ouro ou powerup, a posição é adicionada à lista de posições que contém ouro e powerup. Por fim, caso detecte-se um inimigo, marca-se a direção atual como tendo um inimigo.
- A função GetDecision implementa a lógica de decisão do agente. As principais prioridades são pegar ouro e powerup. Caso detecte-se algum perigo, opta-se por dar ré, e caso não dê para dar ré, vira-se para a direita. A terceira prioridade é atacar um inimigo, caso o mesmo esteja na reta do agente e seja possível atacar, e caso ouça-se passos mas o inimigo não esteja na reta, vira-se para a direita até encontrar o inimigo. A quarta prioridade é a exploração do mundo, sendo a principal indicação mover-se para células seguras e não visitadas. A quinta prioridade é mover-se para uma célula já visitada e que sabe-se que é segura. A sexta prioridade é mover-se para uma célula com perigo conhecido, e a última prioridade é escolher um movimento aleatório, caso todas as outras falhem. 