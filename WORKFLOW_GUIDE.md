# Guia de Workflow - Estudo Paramétrico

## 📊 Fluxograma do Processo

```
┌─────────────────────────────────────────────────────────────┐
│  INÍCIO: Análise de Camada Limite Laminar                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ETAPA 1: Configuração Inicial                              │
│  Script: find_executables.py                                │
│  ✓ Localiza GMSH e SU2                                      │
│  ✓ Verifica instalações                                     │
│  ✓ Fornece caminhos para configurar scripts                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ETAPA 2: Definir Parâmetros do Estudo                      │
│  Decisão: O que variar?                                     │
│  • d_inlet (distância do inlet)                             │
│  • H_dom (altura do domínio)                                │
│  • Ambos (matriz completa)                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────────┐
│  OPÇÃO A:        │    │  OPÇÃO B:            │
│  Workflow Manual │    │  Workflow Automático │
│  (2 scripts)     │    │  (1 script)          │
└────────┬─────────┘    └─────────┬────────────┘
         │                        │
         │                        ▼
         │              ┌────────────────────────┐
         │              │ run_parametric_study.py│
         │              │ • Gera malhas          │
         │              │ • Executa SU2          │
         │              │ • Organiza resultados  │
         │              └──────────┬─────────────┘
         │                         │
         │                         └──────────┐
         ▼                                    │
┌─────────────────────┐                      │
│ generate_meshes.py  │                      │
│ • Cria malhas .su2  │                      │
│ • Varia parâmetros  │                      │
└─────────┬───────────┘                      │
          │                                  │
          ▼                                  │
┌─────────────────────┐                      │
│ run_su2_batch.py    │                      │
│ • Executa SU2       │                      │
│ • Para todas malhas │                      │
└─────────┬───────────┘                      │
          │                                  │
          └──────────────┬───────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  RESULTADOS GERADOS                                         │
│  • mesh_[id].su2         - Arquivos de malha                │
│  • flow_[id].vtu         - Campos de escoamento             │
│  • history_[id].csv      - Histórico de convergência        │
│  • surface_flow_[id].vtu - Dados de superfície              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ETAPA 3: Análise de Resultados                             │
│  Script: analyze_results.py                                 │
│  ✓ Gráficos de convergência                                 │
│  ✓ Comparação entre casos                                   │
│  ✓ Tabela resumo (Cd, Cl)                                   │
│  ✓ Exporta gráficos PNG                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  VISUALIZAÇÃO FINAL                                         │
│  • VISIT/Paraview: Abrir arquivos .vtu                      │
│  • Excel/Python: Analisar .csv                              │
│  • Gráficos: Visualizar .png                                │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  FIM: Relatório e Conclusões                                │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Casos de Uso Específicos

### Caso 1: Estudar influência da distância do inlet

**Objetivo:** Verificar se a distância do inlet até a borda de ataque (BA) afeta a solução.

**Parâmetros:**
- `H_dom` = 0.03 (fixo)
- `d_inlet` = -0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14, -0.16

**Comando:**
```bash
python run_parametric_study.py
# Escolha opção 1
# Confirme valores padrão
```

**Resultado esperado:** 8 simulações comparando efeito da distância do inlet.

---

### Caso 2: Estudar influência da altura do domínio

**Objetivo:** Verificar se a altura do domínio afeta pressão e velocidade.

**Parâmetros:**
- `d_inlet` = -0.16 (fixo)
- `H_dom` = 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10

**Comando:**
```bash
python run_parametric_study.py
# Escolha opção 2
# Confirme valores padrão
```

**Resultado esperado:** 8 simulações comparando efeito da altura.

---

### Caso 3: Matriz completa (Design of Experiments)

**Objetivo:** Estudar interação entre ambos parâmetros.

**Parâmetros:**
- `d_inlet` = -0.08, -0.12, -0.16 (3 valores)
- `H_dom` = 0.02, 0.03, 0.04, 0.05 (4 valores)
- **Total:** 3 × 4 = 12 simulações

**Comando:**
```bash
python run_parametric_study.py
# Escolha opção 3
```

**Resultado esperado:** 12 simulações com todas combinações.

---

## ⏱️ Estimativas de Tempo

### Por Simulação (aproximado)
- Geração de malha (GMSH): 5-10 segundos
- Simulação SU2: 5-15 minutos (depende de ITER e malha)
- Pós-processamento: < 5 segundos

### Estudo Completo
| Casos | Tempo Estimado |
|-------|----------------|
| 5 casos | ~30-60 min |
| 8 casos | ~50-100 min |
| 12 casos | ~80-150 min |

**Dica:** Execute overnight para estudos grandes!

---

## 📁 Organização dos Arquivos

### Antes
```
Lab9_Atividade1710/
├── lam_flatplate.cfg
├── placa_mod.geo
├── run_parametric_study.py
├── analyze_results.py
└── (outros scripts...)
```

### Durante Execução
```
Lab9_Atividade1710/
├── (arquivos originais)
├── placa_temp.geo           ← Temporário (gerado/removido)
├── lam_flatplate.cfg.backup ← Backup (criado/restaurado)
└── mesh_d016_H03.su2        ← Malhas sendo geradas
```

### Depois
```
Lab9_Atividade1710/
├── (arquivos originais)
│
├── Malhas/
│   ├── mesh_d002_H03.su2
│   ├── mesh_d004_H03.su2
│   └── ...
│
├── Resultados/
│   ├── flow_d002_H03.vtu
│   ├── surface_flow_d002_H03.vtu
│   ├── history_d002_H03.csv
│   └── ...
│
└── Análises/
    ├── convergence_d002_H03.png
    ├── comparison_d_inlet.png
    ├── comparison_H_dom.png
    └── summary_results.csv
```

**Dica:** Organize os arquivos em pastas para facilitar análise!

---

## 🔍 Checklist de Verificação

### Antes de Executar
- [ ] GMSH instalado e caminho configurado
- [ ] SU2 instalado e caminho configurado
- [ ] Python 3.x instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `lam_flatplate.cfg` presente
- [ ] Arquivo `placa_mod.geo` presente
- [ ] Espaço em disco suficiente (~100 MB por caso)

### Durante Execução
- [ ] Monitore convergência no terminal
- [ ] Verifique erros/warnings
- [ ] Acompanhe tempo estimado restante

### Após Execução
- [ ] Verifique todos os arquivos .vtu foram gerados
- [ ] Verifique convergência nos arquivos .csv
- [ ] Execute `analyze_results.py`
- [ ] Visualize resultados no VISIT
- [ ] Compare com teoria de Blasius

---

## 🎓 Teoria: O que estamos estudando?

### Camada Limite Laminar

A solução teórica de **Blasius** fornece valores esperados para:

**Coeficiente de Arrasto (Skin Friction):**
```
Cf = 0.664 / √(Re_x)
```

**Espessura da Camada Limite:**
```
δ/x = 5.0 / √(Re_x)
```

### Objetivos da Análise Paramétrica

1. **Independência do domínio:** Mostrar que a solução não depende de:
   - Distância do inlet (`d_inlet`)
   - Altura do domínio (`H_dom`)
   
2. **Validação:** Comparar Cd numérico com teoria de Blasius

3. **Convergência:** Verificar que todas simulações convergem

---

## 💡 Dicas e Boas Práticas

### 1. Comece Pequeno
```bash
# Teste com 2-3 casos primeiro
python run_parametric_study.py
# Opção 4 (customizado)
# d_inlet: -0.16, -0.12
# H_dom: 0.03, 0.05
```

### 2. Monitore Recursos
- CPU: SU2 usa 1 core por padrão
- RAM: ~500 MB por simulação
- Disco: Limpe resultados antigos se necessário

### 3. Backup
```bash
# Antes de rodar tudo
mkdir backup
cp lam_flatplate.cfg backup/
cp placa_mod.geo backup/
```

### 4. Análise Incremental
```bash
# Não espere todas simulações terminarem
# Analise resultados conforme vão sendo gerados
python analyze_results.py
```

### 5. Documentação
Anote parâmetros usados em cada estudo:
```
Estudo 1 (DD/MM/AAAA):
- Objetivo: Testar d_inlet
- Casos: 8
- Observações: ...
```

---

## 🆘 Resolução de Problemas

### Problema: Simulação não converge
**Soluções:**
1. Aumente `ITER` no `lam_flatplate.cfg`
2. Refine a malha (diminua `h` no `.geo`)
3. Verifique condições de contorno

### Problema: GMSH falha ao gerar malha
**Soluções:**
1. Verifique se `d_inlet` < 0
2. Verifique se `H_dom` > 0
3. Teste manualmente: `gmsh placa_mod.geo -2 -format su2 -o test.su2`

### Problema: SU2 muito lento
**Soluções:**
1. Reduza `ITER` (ex: 999 ao invés de 9999)
2. Use malha mais grossa
3. Execute em paralelo (avançado)

### Problema: Falta memória
**Soluções:**
1. Feche outros programas
2. Use malha mais grossa
3. Processe menos casos por vez

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique mensagens de erro
2. Consulte documentação do [SU2](https://su2code.github.io/docs_v7/home/)
3. Revise este guia
4. Peça ajuda ao professor/monitor

---

**Boa sorte com suas simulações! 🚀**


