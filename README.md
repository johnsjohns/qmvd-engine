# QMVD Engine

> **Que Merda Vai Dar?**

O **QMVD Engine** é um projeto experimental de simulação cujo objetivo é começar com um universo extremamente simples, adicionar gradualmente regras de física, química, biologia e outras áreas e observar **que merda vai dar**.

A ideia não é programar diretamente comportamentos complexos.

Em vez disso, queremos criar regras simples e permitir que comportamentos mais complexos apareçam como consequência dessas regras.

O projeto começa propositalmente pequeno: partículas se movimentando em um mundo bidimensional e uma interface de linha de comando.

A partir daí, novas regras serão adicionadas gradualmente.

---

# Objetivo

A ideia geral do projeto é construir, aos poucos, um pequeno universo computacional.

Em vez de escrever algo como:

```python
create_atom()
create_molecule()
create_cell()
```

queremos tentar chegar a estruturas mais complexas através das interações entre elementos mais simples.

O plano de longo prazo pode envolver conceitos de:

- mecânica clássica;
- termodinâmica;
- química;
- eletromagnetismo;
- mecânica quântica;
- biologia;
- microbiologia;
- evolução;
- ecossistemas;
- e qualquer outra coisa que pareça interessante colocar no universo.

Não existe garantia de que o projeto chegará a todos esses pontos.

A filosofia é:

**implementar → simular → medir → descobrir que merda aconteceu → melhorar.**

---

# Estado atual

Atualmente o QMVD Engine possui:

- mundo bidimensional;
- partículas;
- posição;
- velocidade;
- massa;
- raio;
- tipos diferentes de partículas;
- geração determinística através de seed;
- colisões entre partículas;
- colisões com as paredes;
- conservação de momento em colisões elásticas;
- forças de atração e repulsão;
- energia cinética;
- energia potencial;
- energia total;
- medição de drift energético;
- integração temporal com Velocity Verlet;
- passo de tempo configurável;
- contador de colisões;
- interface por linha de comando;
- histórico de comandos;
- barra de progresso para simulações longas;
- visualizador gráfico experimental usando Pygame.

---

# Instalação

Clone o repositório:

```bash
git clone https://github.com/johnsjohns/qmvd-engine.git
cd qmvd-engine
```

Crie um ambiente virtual:

```bash
python3 -m venv .venv
```

Ative:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

# Executando

## Interface de linha de comando

Execute:

```bash
python main.py
```

O QMVD deverá iniciar:

```text
QMVD ENGINE v0.1
"Que Merda Vai Dar?"

Digite 'help' para ver os comandos.

QMVD >
```

Alguns comandos disponíveis:

```text
status
list
inspect 3
run 100
run 10000
exit
```

### `status`

Mostra informações gerais sobre o universo.

Exemplo:

```text
=== QMVD ENGINE ===
Seed: 666
Time: 10000 ticks
Time step: 0.05
Simulation time: 500.000
World: 100 x 100
Particles: 100
Collisions: 1487
Kinetic energy:   58.415898527
Potential energy: -0.009186556
Total energy:     58.406711970
Energy drift:     -3.819310370e-03
Types: A=60, B=25, C=15
```

### `run`

Avança o universo uma determinada quantidade de ticks.

```text
run 10000
```

Durante execuções maiores, uma barra de progresso mostra o andamento e a velocidade aproximada da simulação.

### `list`

Lista as partículas existentes no universo.

### `inspect`

Mostra informações sobre uma partícula específica.

```text
inspect 3
```

---

# Visualizador gráfico

Também existe um visualizador experimental usando Pygame.

Execute:

```bash
python viewer.py
```

O visualizador mostra as partículas se movimentando pelo universo em tempo real.

Controles:

```text
ESPAÇO    Pausar / continuar
↑         Aumentar ticks por frame
↓         Diminuir ticks por frame
R         Reiniciar a simulação
```

O visualizador é separado do motor físico.

Isso é proposital.

```text
                 Universe
                    │
           ┌────────┴────────┐
           │                 │
        main.py           viewer.py
        terminal           gráfico
```

Tanto a interface gráfica quanto o terminal utilizam o mesmo universo e as mesmas regras físicas.

---

# Conceitos

## Particle

Uma **partícula** é atualmente a menor entidade existente no universo do QMVD.

Cada partícula possui propriedades como:

```text
posição
velocidade
aceleração
massa
raio
tipo
```

---

## Tick

Um **tick** é uma etapa de cálculo da simulação.

Um tick não representa necessariamente uma unidade inteira de tempo físico.

O tempo efetivamente simulado depende do `TIME_STEP`.

---

## Time Step / Δt

`TIME_STEP`, também chamado de `dt` ou **Δt**, determina quanto tempo simulado passa durante cada tick.

Atualmente:

```text
TIME_STEP = 0.05
```

Portanto:

```text
1 tick       = 0.05 unidades de tempo
100 ticks    = 5
1.000 ticks  = 50
10.000 ticks = 500
```

Passos menores normalmente aumentam a precisão numérica, mas exigem mais cálculos para simular o mesmo intervalo físico.

---

## Seed

A **seed** é o número usado para iniciar o gerador de números pseudoaleatórios.

Imagine que o computador possui um enorme livro de números aparentemente aleatórios.

A seed diz:

> "Comece a ler o livro daqui."

Se executarmos o QMVD várias vezes usando:

```text
Seed: 666
```

o universo começa sempre da mesma maneira.

As mesmas partículas aparecem nos mesmos lugares, com os mesmos tipos e velocidades iniciais.

Isso é extremamente importante para experimentos.

Podemos alterar uma regra física e executar novamente a mesma seed para comparar o resultado.

---

## Energia cinética

É a energia relacionada ao movimento de uma partícula.

Simplificadamente:

```text
Ec = 1/2 × massa × velocidade²
```

Quanto maior a massa ou a velocidade, maior a energia cinética.

---

## Energia potencial

É energia associada à posição e às interações entre partículas.

No QMVD, partículas podem atrair ou repelir umas às outras dependendo do tipo e da distância.

Essas interações possuem energia potencial associada.

---

## Energia total

Atualmente:

```text
Energia total =
    energia cinética
    +
    energia potencial
```

Em um sistema ideal e fechado, esperamos que essa energia permaneça aproximadamente constante.

---

## Energy Drift

Computadores não trabalham com física contínua.

Eles calculam:

```text
estado 1
estado 2
estado 3
estado 4
...
```

Isso introduz erros numéricos.

O QMVD mede a diferença entre a energia total atual e a energia total inicial.

Essa diferença é chamada aqui de:

```text
Energy drift
```

Quanto mais próximo de zero, melhor.

---

## Momento

O momento linear é:

```text
p = massa × velocidade
```

Em um sistema isolado, o momento total também deve obedecer às leis de conservação.

Acompanhar o momento ajuda a encontrar erros nas regras físicas da simulação.

---

## Velocity Verlet

Inicialmente o QMVD utilizava uma integração extremamente simples:

```text
calcular força
↓
alterar velocidade
↓
alterar posição
```

Isso provocava perda significativa de energia durante simulações longas.

O projeto passou então a utilizar uma versão do método **Velocity Verlet**.

Simplificadamente:

```text
calcular aceleração
↓
atualizar posição
↓
aplicar metade da atualização da velocidade
↓
recalcular aceleração
↓
completar atualização da velocidade
```

Esse método apresentou melhor conservação de energia durante os experimentos.

---

# Experimentos realizados

Uma parte importante do desenvolvimento do QMVD é não simplesmente corrigir comportamentos estranhos, mas criar experimentos para descobrir sua origem.

## Vazamento de energia

Com 100 partículas e integração inicial, uma simulação de 100.000 ticks apresentou:

```text
Energy drift: -6.702956629
```

Isso era uma perda significativa de energia.

Introduzimos:

```text
TIME_STEP = 0.1
```

e o drift caiu para aproximadamente:

```text
-0.0819
```

Depois:

```text
TIME_STEP = 0.05
```

reduziu ainda mais o erro.

Isso indicou que boa parte do problema estava relacionada à integração numérica.

---

## Velocity Verlet

Depois da implementação do Velocity Verlet, executamos novamente a simulação.

Em 10.000 ticks com:

```text
TIME_STEP = 0.05
```

obtivemos aproximadamente:

```text
Energy drift: -0.003828
```

uma melhora significativa em relação ao integrador anterior.

---

## Investigação das colisões

Mesmo com Velocity Verlet, ainda existia drift energético.

Para investigar, as colisões foram temporariamente desativadas.

Com colisões:

```text
Energy drift: -0.003828
```

Sem colisões:

```text
Energy drift: +0.000618
```

Isso indicou que boa parte do erro restante estava relacionada ao sistema de colisões.

A correção de sobreposição das partículas passou a ser um dos principais suspeitos.

---

# Filosofia de desenvolvimento

O QMVD não pretende começar tentando simular o universo real inteiro.

Isso seria impraticável.

Em vez disso:

```text
regra simples
    ↓
teste
    ↓
medição
    ↓
resultado estranho
    ↓
investigação
    ↓
nova regra
```

Sempre que possível, mudanças devem ser testadas usando a mesma seed e os mesmos parâmetros.

Assim podemos comparar versões diferentes da física usando exatamente as mesmas condições iniciais.

---

# Próximos passos

Algumas ideias atualmente consideradas:

- melhorar o sistema de colisões;
- substituir colisões rígidas por repulsão de curto alcance;
- investigar distâncias estáveis entre partículas;
- identificar agrupamentos;
- visualizar o alcance das interações;
- clicar em partículas no visualizador para inspecioná-las;
- medir desempenho em ticks por segundo;
- melhorar ferramentas de experimentação;
- salvar e carregar universos;
- criar logs de experimentos;
- começar modelos mais sofisticados de interação entre partículas.

A longo prazo, o objetivo é permitir que estruturas cada vez mais complexas possam surgir das regras mais simples.

---

# Por que "QMVD"?

Porque existe uma pergunta fundamental por trás de toda simulação:

> **Que merda vai dar?**

Só existe uma maneira de descobrir.

Rodar.