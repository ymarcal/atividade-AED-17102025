# Scripts de Automação - Estudo de Camada Limite Laminar

Este conjunto de scripts automatiza o workflow completo de análise CFD: geração de malhas (GMSH) → simulação (SU2) → resultados.

## 🚀 Início Rápido (Quick Start)

```bash
# Passo 1: Localizar executáveis
python find_executables.py

# Passo 2: Ajustar caminhos nos scripts (se necessário)
# Edite GMSH_PATH e SU2_PATH nos scripts

# Passo 3: Executar estudo paramétrico completo
python run_parametric_study.py

# Passo 4: Analisar resultados
pip install matplotlib pandas  # Instala dependências
python analyze_results.py
```

**Pronto!** Você terá malhas, simulações e gráficos prontos para análise.

## 📋 Scripts Disponíveis

### 0. `find_executables.py` - Localizar GMSH e SU2 🔍
**Execute primeiro!** Ajuda a encontrar os caminhos dos executáveis.

**Uso:**
```bash
python find_executables.py
```

**O que faz:**
- Procura GMSH e SU2 no sistema
- Verifica PATH e diretórios comuns
- Testa se os executáveis funcionam
- Fornece os caminhos corretos para usar nos outros scripts

---

### 1. `generate_meshes.py` - Geração de Malhas
Gera malhas parametricamente variando `d_inlet` e/ou `H_dom`.

**Uso:**
```bash
python generate_meshes.py
```

**Modos disponíveis:**
- Variar apenas `d_inlet` (altura fixa)
- Variar apenas `H_dom` (distância inlet fixa)
- Matriz completa (todos os parâmetros)
- Definição manual de casos

**Saída:** Arquivos `mesh_[ID].su2` (ex: `mesh_d016_H03.su2`)

---

### 2. `run_su2_batch.py` - Execução em Lote do SU2
Executa SU2 para todas as malhas existentes no diretório.

**Uso:**
```bash
python run_su2_batch.py
```

**O que faz:**
- Detecta automaticamente malhas com padrão `mesh_d*.su2`
- Para cada malha:
  - Modifica `lam_flatplate.cfg` temporariamente
  - Executa SU2
  - Renomeia outputs com ID da malha
- Restaura configuração original ao final

**Saída:** 
- `flow_[ID].vtu`
- `history_[ID].csv`
- `surface_flow_[ID].vtu`
- `restart_flow_[ID].dat`

---

### 3. `run_parametric_study.py` - Workflow Completo ⭐
**RECOMENDADO** - Executa todo o pipeline automaticamente.

**Uso:**
```bash
python run_parametric_study.py
```

**O que faz:**
1. Gera malha no GMSH com parâmetros especificados
2. Configura e executa SU2
3. Renomeia e organiza resultados
4. Gera relatório completo

**Ideal para:** Estudos paramétricos completos

---

### 4. `analyze_results.py` - Análise de Resultados 📊
Analisa e compara resultados das simulações.

**Uso:**
```bash
python analyze_results.py
```

**O que faz:**
- Gera gráficos de convergência individuais
- Compara diferentes casos
- Cria tabela resumo com Cd e Cl
- Exporta gráficos em PNG e tabela CSV

**Requer:** `matplotlib` e `pandas`
```bash
pip install matplotlib pandas
```

---

## 🔧 Configuração Inicial

### Pré-requisitos
- Python 3.x
- GMSH instalado ([download](https://gmsh.info/))
- SU2 instalado ([download](https://su2code.github.io/))

### Ajustar Caminhos

Edite os caminhos nos scripts se necessário:

```python
# No início de cada script
GMSH_PATH = r"C:\Program Files\gmsh-4.11.1-Windows64\gmsh.exe"
SU2_PATH = r"C:\Users\ymarc\OneDrive\Documents\SU2-v8.3.0-win64\win64\bin\SU2_CFD.exe"
```

---

## 📊 Exemplos de Uso

### Exemplo 1: Estudar efeito da distância do inlet
```bash
python run_parametric_study.py
# Escolha opção 1
# Variar d_inlet: -0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14, -0.16
# H_dom fixo: 0.03
```

**Resultado:** 8 malhas e simulações com diferentes distâncias de inlet

### Exemplo 2: Estudar efeito da altura do domínio
```bash
python run_parametric_study.py
# Escolha opção 2
# d_inlet fixo: -0.16
# Variar H_dom: 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10
```

**Resultado:** 8 malhas e simulações com diferentes alturas

### Exemplo 3: Processar malhas já existentes
```bash
python run_su2_batch.py
# Processa todas as malhas mesh_d*.su2 já criadas
```

---

## 📁 Estrutura de Arquivos

### Antes da Execução
```
Lab9_Atividade1710/
├── lam_flatplate.cfg         # Configuração do SU2
├── placa_mod.geo              # Template da geometria
├── generate_meshes.py         # Script 1
├── run_su2_batch.py          # Script 2
└── run_parametric_study.py   # Script 3
```

### Após Execução
```
Lab9_Atividade1710/
├── mesh_d002_H03.su2          # Malhas geradas
├── mesh_d004_H03.su2
├── ...
├── flow_d002_H03.vtu          # Resultados SU2
├── flow_d004_H03.vtu
├── ...
├── history_d002_H03.csv       # Históricos
├── history_d004_H03.csv
└── ...
```

---

## 🎯 Convenção de Nomenclatura

**Formato:** `mesh_d[XXX]_H[YY].su2`

- `d[XXX]`: Distância do inlet × 100 (ex: d016 = -0.16 m)
- `H[YY]`: Altura do domínio × 100 (ex: H03 = 0.03 m)

**Exemplos:**
- `mesh_d016_H03.su2` → d_inlet = -0.16, H_dom = 0.03
- `mesh_d008_H05.su2` → d_inlet = -0.08, H_dom = 0.05

---

## 📈 Análise de Resultados

### Abrir no VISIT
1. Abra o VISIT
2. `File → Open` → Selecione `flow_*.vtu`
3. Adicione plots (pressão, velocidade, etc.)

### Análise de Convergência
Abra os arquivos `history_[ID].csv` no Excel/Python para verificar convergência.

**Exemplo em Python:**
```python
import pandas as pd
import matplotlib.pyplot as plt

# Carrega histórico
df = pd.read_csv('history_d016_H03.csv')

# Plota convergência
plt.semilogy(df['Inner_Iter'], df['rms_Density'])
plt.xlabel('Iteração')
plt.ylabel('Resíduo (Densidade)')
plt.title('Convergência - d016_H03')
plt.grid()
plt.show()
```

---

## ⚠️ Observações Importantes

1. **Tempo de execução:** Cada simulação pode levar vários minutos
2. **Espaço em disco:** Cada caso gera ~50-100 MB de dados
3. **Interrupção:** Use `Ctrl+C` para parar (config será restaurada)
4. **Arquivos temporários:** Scripts limpam automaticamente arquivos `.geo` temporários

---

## 🐛 Troubleshooting

### "GMSH não encontrado"
→ Instale GMSH ou corrija o caminho `GMSH_PATH` no script

### "SU2 não encontrado"
→ Corrija o caminho `SU2_PATH` no script

### "Simulação não converge"
→ Verifique malha, condições de contorno e parâmetros no `lam_flatplate.cfg`

### "Erro de memória"
→ Reduza número de iterações (`ITER` no .cfg) ou use malha mais grossa

---

## 📚 Referências

- [Documentação SU2](https://su2code.github.io/docs_v7/home/)
- [Documentação GMSH](https://gmsh.info/doc/texinfo/gmsh.html)
- [Tutorial Camada Limite](https://su2code.github.io/tutorials/Laminar_Flat_Plate/)

---

## 👨‍💻 Autor

Scripts desenvolvidos para a disciplina AED-26 (ITA)  
Problema: Camada Limite Laminar sobre Placa Plana

