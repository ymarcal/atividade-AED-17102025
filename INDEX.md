# 📚 Índice - Scripts de Automação CFD

## 🎯 Visão Geral

Este pacote completo automatiza estudos paramétricos de CFD usando GMSH e SU2.

---

## 📂 Organização dos Arquivos

### 🚀 Scripts Principais (Execute Nesta Ordem)

| # | Arquivo | Descrição | Quando Usar |
|---|---------|-----------|-------------|
| 1 | `find_executables.py` | Localiza GMSH e SU2 | **Sempre execute primeiro** |
| 2 | `run_parametric_study.py` | Workflow completo | **RECOMENDADO** para estudo completo |
| 3 | `analyze_results.py` | Análise de resultados | Após as simulações |
| 4 | `generate_report.py` | Relatório HTML | Para documentação final |

### 🔧 Scripts Alternativos

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| `generate_meshes.py` | Gera apenas malhas | Se quiser malhas sem rodar SU2 |
| `run_su2_batch.py` | Executa SU2 em lote | Se já tem malhas prontas |

### 📊 Script de Leitura VTU

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| `read_vtu.py` | Lê arquivos .vtu e converte para DataFrame pandas | Para análise programática dos resultados VTU |

### 📖 Documentação

| Arquivo | Conteúdo |
|---------|----------|
| `LEIA_ME.txt` | **Início Rápido** - Leia primeiro! |
| `README_scripts.md` | Documentação completa de cada script |
| `WORKFLOW_GUIDE.md` | Guia detalhado com exemplos de uso |
| `INDEX.md` | Este arquivo (índice geral) |

### ⚙️ Arquivos de Configuração

| Arquivo | Descrição |
|---------|-----------|
| `lam_flatplate.cfg` | Configuração do SU2 |
| `placa_mod.geo` | Template de geometria GMSH |
| `requirements.txt` | Dependências Python |

### 💻 Utilitários Windows

| Arquivo | Descrição |
|---------|-----------|
| `executar_estudo.bat` | Menu interativo para Windows |

---

## 🎓 Guia de Uso por Cenário

### Cenário 1: Primeira Vez Usando os Scripts

```bash
# Passo 1: Leia o guia rápido
Abra: LEIA_ME.txt

# Passo 2: Localize executáveis
python find_executables.py

# Passo 3: Ajuste caminhos (se necessário)
Edite GMSH_PATH e SU2_PATH nos scripts

# Passo 4: Execute estudo
python run_parametric_study.py

# Passo 5: Analise resultados
pip install matplotlib pandas
python analyze_results.py

# Passo 6: Gere relatório
python generate_report.py
```

**Alternativa Windows:**
```cmd
executar_estudo.bat
```

---

### Cenário 2: Já Tenho Malhas, Quero Apenas Simular

```bash
# Coloque as malhas no diretório (mesh_*.su2)
# Execute:
python run_su2_batch.py
```

---

### Cenário 3: Quero Apenas Gerar Malhas

```bash
python generate_meshes.py
```

---

### Cenário 4: Já Rodei Tudo, Quero Analisar

```bash
# Análise gráfica dos CSV
python analyze_results.py

# Relatório HTML
python generate_report.py
```

---

## 📊 Fluxo de Trabalho Típico

```
┌─────────────────┐
│ find_executables │ ← Execute uma vez
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ run_parametric_study │ ← Executa tudo
└────────┬─────────────┘
         │
         ├─→ Gera malhas
         ├─→ Simula no SU2  
         └─→ Organiza outputs (CSV + VTU)
         │
         ▼
┌─────────────────┐
│ analyze_results │ ← Gera gráficos
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│ generate_report  │ ← Relatório final
└──────────────────┘

Opcional: read_vtu.py para converter VTU → pandas DataFrame
```

---

## 🗂️ Estrutura de Saída

Após executar tudo, você terá:

```
Lab9_Atividade1710/
│
├── 📜 Scripts (você já tem)
│   ├── run_parametric_study.py
│   ├── analyze_results.py
│   └── ...
│
├── 🔷 Malhas Geradas
│   ├── mesh_d002_H03.su2
│   ├── mesh_d004_H03.su2
│   └── ...
│
├── 📊 Resultados SU2
│   ├── flow_d002_H03.vtu
│   ├── history_d002_H03.csv
│   ├── surface_flow_d002_H03.vtu
│   └── ...
│
├── 📈 Gráficos
│   ├── convergence_d002_H03.png
│   ├── comparison_d_inlet.png
│   ├── comparison_H_dom.png
│   └── summary_results.csv
│
└── 📄 Relatório
    └── relatorio_estudo_parametrico.html
```

---

## 🎯 Objetivos do Estudo

Conforme o enunciado (Problem_Set_Laminar_Boundary_Layer_2025.pdf):

1. **Tarefa 1:** Estudar influência do tamanho do domínio
   - Variar distância do inlet até BA
   - Verificar distribuição de pressão
   - Verificar independência dos resultados

2. **Tarefa 2:** Estudo de refinamento de malha
   - Usar GCI de Roache
   - Analisar arrasto

3. **Tarefa 3:** Comparar Cd e δ com teoria de Blasius

---

## 💡 Dicas Importantes

### ✅ Faça

- Execute `find_executables.py` primeiro
- Leia `LEIA_ME.txt` para entender o fluxo
- Comece com 2-3 casos para testar
- Verifique convergência nos .csv
- Compare resultados com Blasius
- Use `read_vtu.py` para converter VTU em DataFrame pandas (se necessário)

### ❌ Evite

- Modificar `lam_flatplate.cfg` durante execução
- Deletar arquivos enquanto SU2 roda
- Executar múltiplas instâncias simultaneamente
- Ignorar mensagens de erro

---

## 🆘 Precisa de Ajuda?

1. **Erro com executáveis?**
   → `python find_executables.py`

2. **Não sabe por onde começar?**
   → Abra `LEIA_ME.txt`

3. **Quer entender o processo?**
   → Leia `WORKFLOW_GUIDE.md`

4. **Documentação detalhada?**
   → Veja `README_scripts.md`

5. **Erro técnico?**
   → Consulte seção "Troubleshooting" no README

---

## 📞 Links Úteis

- [SU2 Documentation](https://su2code.github.io/docs_v7/home/)
- [GMSH Documentation](https://gmsh.info/doc/texinfo/gmsh.html)
- [Tutorial Laminar Flat Plate](https://su2code.github.io/tutorials/Laminar_Flat_Plate/)
- [Blasius Solution](https://en.wikipedia.org/wiki/Blasius_boundary_layer)

---

## ✨ Recursos Especiais

### Geração de Relatório HTML

Cria um relatório interativo com:
- Tabela de todos os resultados
- Gráficos embutidos
- Comparação com Blasius
- Estatísticas do estudo

```bash
python generate_report.py
```

### Menu Interativo (Windows)

Interface amigável para quem prefere não usar linha de comando:

```cmd
executar_estudo.bat
```

### Conversão VTU para DataFrame

Para análise programática dos arquivos VTU:

```bash
python read_vtu.py arquivo.vtu
```

Ou use em seu próprio script:
```python
from read_vtu import read_vtu
df = read_vtu('flow_d002_H03.vtu')
print(df.head())
```

---

## 📋 Checklist Completo

### Antes de Começar
- [ ] Python 3.x instalado
- [ ] GMSH instalado
- [ ] SU2 instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)

### Durante Setup
- [ ] Executou `find_executables.py`
- [ ] Caminhos configurados corretamente
- [ ] Testou com 1-2 casos

### Execução
- [ ] Estudo paramétrico executado
- [ ] Todas simulações convergidas
- [ ] Arquivos .vtu gerados

### Análise
- [ ] Gráficos gerados (`analyze_results.py`)
- [ ] Relatório HTML criado (`generate_report.py`)
- [ ] Resultados visualizados no VISIT
- [ ] Comparação com Blasius feita

### Documentação
- [ ] Capturas de tela salvas
- [ ] Observações anotadas
- [ ] Relatório final escrito

---

## 🏆 Conclusão

Você agora tem um sistema completo de automação CFD!

**Próximo passo:** Abra `LEIA_ME.txt` e comece! 🚀

---

<p align="center">
  <strong>Desenvolvido para AED-26 (ITA) | 2025</strong><br>
  <em>Boa sorte com suas simulações!</em> ✨
</p>


