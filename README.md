# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Repositório de entrega do desafio de **Engenharia e Avaliação de Prompts com LangChain e LangSmith**.

- **Prompt Público no LangSmith Hub:** [`publichandle/bug_to_user_story_v2`](https://smith.langchain.com/prompts/bug_to_user_story_v2/2f860ed1?organizationId=d0e1ad7c-8a25-4cbf-ac57-0f07c18809f0)
- **Dataset Público de Avaliação e Experimentos (LangSmith):** [`https://smith.langchain.com/public/ee3cb357-1eb2-4882-9169-2a13f50dc047/d`](https://smith.langchain.com/public/ee3cb357-1eb2-4882-9169-2a13f50dc047/d)

---

## Técnicas Aplicadas (Fase 2)

Para transformar o prompt original de baixa qualidade (`prompts/bug_to_user_story_v1.yml`) no prompt otimizado (`prompts/bug_to_user_story_v2.yml`), foram aplicadas **4 técnicas avançadas de Prompt Engineering**:

### 1. Role Prompting (Definição de Persona e Contexto)
- **Por que foi escolhida:** O prompt `v1` definia o modelo apenas como *"um assistente que ajuda a transformar relatos de bugs de usuários em tarefas para desenvolvedores"*, resultando em respostas genéricas, sem empatia com o usuário afetado e sem articulação de valor de negócio. Definir uma persona especialista orienta o vocabulário, o tom construtivo e o rigor técnico da especificação.
- **Exemplo prático aplicado no `v2`:**
  ```text
  Você é um Product Manager Sênior e Especialista em Engenharia de Requisitos Ágeis.
  Sua missão é transformar relatos de bugs em User Stories claras, completas, empáticas,
  orientadas a valor de negócio e tecnicamente precisas em formato Markdown/texto estruturado.
  ```

### 2. Chain of Thought — CoT (Raciocínio Passo a Passo)
- **Por que foi escolhida:** O dataset de avaliação (`datasets/bug_to_user_story.jsonl`) contém 15 bugs divididos em 3 níveis de complexidade (**5 simples**, **7 médios** e **3 complexos**). Um passo a passo estruturado de análise antes da geração garante que o modelo classifique corretamente a complexidade do bug, identifique a persona exata afetada e extraia 100% dos fatos técnicos (SLAs, endpoints, códigos HTTP, queries SQL, severidade e impacto financeiro) sem inventar dados (zero alucinações).
- **Exemplo prático aplicado no `v2`:**
  ```text
  Antes de redigir a resposta final, execute mentalmente os seguintes passos:
  Passo 1 - Classifique a complexidade do relato de bug (SIMPLES, MÉDIO ou COMPLEXO).
  Passo 2 - Identifique a persona exata afetada (nunca use apenas "Como um usuário" genérico).
  Passo 3 - Extraia todos os fatos, métricas e detalhes técnicos do relato sem inventar ferramentas externas.
  Passo 4 - Aplique o esqueleto estrutural (Skeleton of Thought) correspondente à complexidade identificada.
  ```

### 3. Skeleton of Thought (Estrutura Adaptativa por Complexidade)
- **Por que foi escolhida:** Bugs simples exigem concisão (apenas User Story e Critérios de Aceitação em formato Given-When-Then), enquanto bugs médios exigem `Contexto Técnico:` / `Contexto de Segurança:` e bugs complexos exigem múltiplas seções delimitadas (`=== USER STORY PRINCIPAL ===`, `=== CRITÉRIOS DE ACEITAÇÃO ===` subdivididos em A, B, C e D, `=== CRITÉRIOS TÉCNICOS ===`, `=== CONTEXTO DO BUG ===` e `=== TASKS TÉCNICAS SUGERIDAS ===`). O *Skeleton of Thought* fornece o molde exato para cada categoria, maximizando `Clarity`, `Precision` e `F1-Score`.
- **Exemplo prático aplicado no `v2`:**
  - **Molde Simples:** User Story (`Como um..., eu quero..., para que...`) + `Critérios de Aceitação:` (`- Dado que` / `- Quando` / `- Então` / `- E` / `- E`).
  - **Molde Médio:** Molde Simples + critérios específicos do domínio (`Critérios Adicionais para Admins:`, `Exemplo de Cálculo:`, `Critérios Técnicos:`, `Critérios de Prevenção:`, `Critérios de Acessibilidade:`) + `Contexto Técnico:`.
  - **Molde Complexo:** Síntese + `=== USER STORY PRINCIPAL ===` + `=== CRITÉRIOS DE ACEITAÇÃO ===` (A..D) + `=== CRITÉRIOS TÉCNICOS ===` + `=== CONTEXTO DO BUG ===` + `=== TASKS TÉCNICAS SUGERIDAS ===`.

### 4. Few-shot Learning (Exemplos de Entrada e Saída)
- **Por que foi escolhida:** Exemplos concretos de entrada e saída calibram com precisão a granularidade, o idioma, o estilo de escrita BDD/Gherkin e a formatação visual esperada pelos avaliadores, sem depender apenas de descrições abstratas.
- **Exemplo prático aplicado no `v2`:** Foram incluídos **3 exemplos completos e inéditos** no `system_prompt` (não pertencentes ao dataset de avaliação para evitar *data leakage*):
  1. `EXEMPLO 1 (BUG SIMPLES)`: Filtro de busca por categoria no catálogo.
  2. `EXEMPLO 2 (BUG MÉDIO)`: Exportação de extrato bancário com erro HTTP 504 e falta de índice composto SQL.
  3. `EXEMPLO 3 (BUG COMPLEXO)`: Módulo de agendamento médico com 4 falhas críticas (IDOR/LGPD, race condition em slots, falha HTTP 429 em SMS e quebra de layout mobile).

---

## Resultados Finais

### Link Público do Dataset e Experimentos no LangSmith
- **Dataset Público (15 exemplos + Experimentos comparativos):**
  👉 **[https://smith.langchain.com/public/ee3cb357-1eb2-4882-9169-2a13f50dc047/d](https://smith.langchain.com/public/ee3cb357-1eb2-4882-9169-2a13f50dc047/d)**
- **Prompt Público no LangSmith Hub:**
  👉 **[`publichandle/bug_to_user_story_v2`](https://smith.langchain.com/prompts/bug_to_user_story_v2/2f860ed1?organizationId=d0e1ad7c-8a25-4cbf-ac57-0f07c18809f0)**

### Evolução das Iterações e Métricas Obtidas

Todas as 5 métricas superaram com folga o critério mínimo de aprovação ($\ge 0.80$) nas duas execuções completas com modelos distintos da família Google Gemini:

| Métrica | Prompt v1 (Referência Inicial) | Iteração 1 (`bc838971` — `gemini-3-flash-preview`) | Iteração 2 (`359c1385` — `gemini-3.5-flash-lite`) | Meta Mínima | Status |
|---|---|---|---|---|---|
| **Helpfulness** *(Derivada)* | 0.45 ✗ | **0.91** ✓ | **0.89** ✓ | $\ge 0.80$ | ✅ APROVADO |
| **Correctness** *(Derivada)* | 0.52 ✗ | **0.93** ✓ | **0.90** ✓ | $\ge 0.80$ | ✅ APROVADO |
| **F1-Score** *(Base)* | 0.48 ✗ | **0.96** ✓ | **0.92** ✓ | $\ge 0.80$ | ✅ APROVADO |
| **Clarity** *(Base)* | 0.50 ✗ | **0.92** ✓ | **0.91** ✓ | $\ge 0.80$ | ✅ APROVADO |
| **Precision** *(Base)* | 0.46 ✗ | **0.90** ✓ | **0.88** ✓ | $\ge 0.80$ | ✅ APROVADO |
| **MÉDIA GERAL** | **0.4820** ✗ | **0.9238** ✓ | **0.9008** ✓ | $\ge 0.80$ | ✅ **APROVADO** |

#### Saída do CLI — Iteração 1 (`publichandle-bug_to_user_story_v2-bc838971`)
```text
🔍 Avaliando: publichandle/bug_to_user_story_v2
   Puxando prompt do LangSmith Hub: publichandle/bug_to_user_story_v2
   ✓ Prompt carregado com sucesso
   Rodando experimento no LangSmith...
      [1] F1:0.97 Clarity:0.95 Precision:0.97
      [2] F1:0.97 Clarity:0.95 Precision:0.93
      [3] F1:1.00 Clarity:0.95 Precision:0.93
      [4] F1:0.92 Clarity:0.95 Precision:0.93
      [5] F1:0.92 Clarity:0.95 Precision:0.93
      [6] F1:1.00 Clarity:0.85 Precision:0.93
      [7] F1:1.00 Clarity:0.95 Precision:0.97
      [8] F1:0.97 Clarity:0.95 Precision:0.97
      [9] F1:0.95 Clarity:0.95 Precision:0.93
      [10] F1:0.90 Clarity:0.90 Precision:0.83
      [11] F1:0.95 Clarity:0.85 Precision:0.83
      [12] F1:0.90 Clarity:0.90 Precision:0.83
      [13] F1:0.97 Clarity:0.90 Precision:0.93
      [14] F1:0.90 Clarity:0.95 Precision:0.93
      [15] F1:1.00 Clarity:0.90 Precision:0.66

==================================================
Prompt: publichandle/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.91 ✓
  - Correctness: 0.93 ✓

Métricas Base:
  - F1-Score: 0.96 ✓
  - Clarity: 0.92 ✓
  - Precision: 0.90 ✓

--------------------------------------------------
📊 MÉDIA GERAL: 0.9238
--------------------------------------------------

✅ STATUS: APROVADO - Todas as métricas >= 0.8
```

#### Saída do CLI — Iteração 2 (`publichandle-bug_to_user_story_v2-359c1385`)
```text
==================================================
Prompt: publichandle/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.89 ✓
  - Correctness: 0.90 ✓

Métricas Base:
  - F1-Score: 0.92 ✓
  - Clarity: 0.91 ✓
  - Precision: 0.88 ✓

--------------------------------------------------
📊 MÉDIA GERAL: 0.9008
--------------------------------------------------

✅ STATUS: APROVADO - Todas as métricas >= 0.8
```

### Comparação entre o Prompt Original (`v1`) e o Otimizado (`v2`)

| Aspecto | Prompt Original (`bug_to_user_story_v1.yml`) | Prompt Otimizado (`bug_to_user_story_v2.yml`) | Por que mudou? |
|---|---|---|---|
| **Separação System vs User** | Duplicava `{bug_report}` tanto no `system_prompt` quanto no `user_prompt`. | `system_prompt` contém apenas instruções, regras e exemplos; `user_prompt` contém exclusivamente `"{bug_report}"`. | Evita repetição desnecessária de tokens e separa instruções permanentes da entrada variável. |
| **Persona (Role Prompting)** | Assistente genérico sem especialização. | *Product Manager Sênior e Especialista em Engenharia de Requisitos Ágeis*. | Garante linguagem centrada no usuário, empatia e foco em valor de negócio (`para que...`). |
| **Formato da User Story e Critérios** | Nenhuma instrução de formato (saída livre e inconsistente). | Exige formato ágil padrão (`Como [persona], eu quero [ação], para que [benefício]`) e critérios BDD/Gherkin (`Dado que` / `Quando` / `Então` / `E`). | Alinha 100% da estrutura com os critérios de avaliação de `Clarity` e `F1-Score`. |
| **Adaptação à Complexidade** | Tratava bugs de 1 linha e bugs críticos de múltiplas falhas da mesma forma. | *Skeleton of Thought* adaptativo em 3 níveis (Simples, Médio e Complexo com seções `=== ... ===`). | Evita prolixidade em bugs simples (protegendo `Precision` e `Clarity`) e garante completude técnica em bugs médios e complexos (protegendo `Recall`/`F1-Score`). |
| **Prevenção de Alucinações e Edge Cases** | Sem restrições contra invenção de dados. | Regras explícitas para preservar 100% das métricas/logs/endpoints do relato, generalizar IDs ilustrativos em bugs simples e não inventar ferramentas externas. | Aumenta `Precision` e `Correctness` no julgamento LLM-as-a-Judge. |
| **Exemplos (Few-shot)** | 0 exemplos (Zero-shot). | 3 exemplos completos (Simples, Médio e Complexo). | Demonstra na prática a estrutura e a densidade técnica esperadas em cada nível de complexidade. |

---

### Tracing Detalhado de 3 Exemplos no LangSmith

Durante o ciclo de otimização, utilizamos o **Tracing do LangSmith** para inspecionar as entradas, saídas geradas, tempo de execução e raciocínio (`reasoning`) dos juízes de avaliação:

#### Exemplo 1 — Bug Simples (Run ID: `01a130a8-b778-7632-a8d3-4a49afebe81c`)
- **Input (`bug_report`):** `"Botão de adicionar ao carrinho não funciona no produto ID 1234."`
- **Evolução via Debug de Trace:** Na Iteração 1 (`run 01a13095-8241-72e2-9637-fd7bddb49e16`), o trace mostrou que o modelo havia restringido a User Story ao `"produto ID 1234"`. Na Iteração 2, após ajuste nas regras do prompt, o modelo generalizou corretamente a funcionalidade:
  ```text
  Como um cliente navegando na loja, eu quero adicionar produtos ao carrinho com sucesso, para que eu possa prosseguir com a minha compra.

  Critérios de Aceitação:
  - Dado que estou na página de detalhes de um produto
  - Quando clico no botão "Adicionar ao carrinho"
  - Então o produto deve ser incluído no carrinho de compras com a quantidade selecionada
  - E devo visualizar uma confirmação visual de que o item foi adicionado
  - E o contador de itens no ícone do carrinho deve ser atualizado imediatamente
  ```
- **Notas no Trace:** `F1-Score: 0.97` | `Clarity: 0.95` (`2.66s`)
- **Feedback do Juiz (`Clarity`):** *"A resposta é excelente e segue o padrão de User Story (Gherkin) de forma impecável. A organização é lógica, a linguagem é técnica, porém acessível, e não há ambiguidades."*

#### Exemplo 2 — Bug Médio de Segurança / IDOR (Run ID: `01a13094-61e0-7b22-b31c-a6a6743464b7`)
- **Input (`bug_report`):** `"Endpoint /api/users/:id retorna dados de qualquer usuário sem validar permissões... Severidade: ALTA - vazamento de dados pessoais"`
- **Saída Gerada no Trace (Resumo):** User Story com persona autenticada + `Critérios de Aceitação:` (bloqueio `HTTP 403 Forbidden` para acesso a terceiros) + `Critérios Adicionais para Admins:` (`HTTP 200` e registro em log) + `Contexto de Segurança:` (Severidade ALTA, OWASP A01:2021 Broken Access Control, exposição de email/telefone/endereço e implementação de middleware de autorização).
- **Notas no Trace:** `F1-Score: 0.97` | `Clarity: 0.95` | `Precision: 0.97` | `Helpfulness: 0.96` | `Correctness: 0.97` (`11.62s`)
- **Feedback do Juiz (`Precision`):** *"A resposta gerada é excelente e tecnicamente precisa. Ela expande o formato de User Story e Critérios de Aceitação de forma profissional, mantendo total fidelidade ao problema de IDOR relatado. Não há alucinações; a inclusão de detalhes como 'middleware de autorização' e a distinção clara entre usuários comuns e administradores está correta e alinhada com as melhores práticas de segurança (OWASP)."*

#### Exemplo 3 — Bug Complexo Crítico de Checkout (Run ID: `01a13093-c705-7db3-ac3d-9047df09b597`)
- **Input (`bug_report`):** `"Sistema de checkout com múltiplas falhas críticas. PROBLEMAS IDENTIFICADOS: 1. SEGURANÇA - XSS no campo de cupom... 2. INTEGRAÇÃO - Gateway de pagamento retorna erro intermitente (504 / Connection pool exhausted)... 3. LÓGICA DE NEGÓCIO - Race condition em cupons (PROMO10, 147 usos)... 4. UX - Loading infinito após timeout..."`
- **Saída Gerada no Trace (Resumo):** User Story síntese + `=== USER STORY PRINCIPAL ===` + `=== CRITÉRIOS DE ACEITAÇÃO ===` divididos em A (Segurança XSS), B (Integração Pagamento <30s com retry/backoff), C (Controle atômico de cupons até 100 usos) e D (UX sem loading infinito) + `=== CRITÉRIOS TÉCNICOS ===` (DOMPurify, CSP, pool do Postgres, Circuit Breaker, `SELECT FOR UPDATE` / `Idempotency-Key`, polling/webhook) + `=== CONTEXTO DO BUG ===` (Severidade CRÍTICA, 150+ clientes, R$ 15.000 em perdas, 45 tickets, queda de rating 4.5→3.2) + `=== TASKS TÉCNICAS SUGERIDAS ===`.
- **Notas no Trace:** `F1-Score: 1.00` | `Clarity: 0.95` | `Precision: 0.93` | `Helpfulness: 0.94` | `Correctness: 0.965` (`12.70s`)
- **Feedback do Juiz (`F1-Score`):** *"A resposta gerada é excelente. Ela manteve 100% de precisão, abordando todos os problemas técnicos e de negócio com terminologia correta (ex: Idempotency-Key, Circuit Breaker, DOMPurify). O recall também é total, pois cobriu todos os critérios de aceitação, requisitos técnicos e o contexto do bug definidos na resposta esperada."*

---

## Como Executar

### 1. Pré-requisitos e Dependências
- **Python:** 3.10+ (testado com Python 3.13.7)
- **Conta e API Key no LangSmith:** [https://smith.langchain.com](https://smith.langchain.com) (com handle público do LangSmith Hub configurado)
- **API Key de LLM:** Google Gemini ([Google AI Studio](https://aistudio.google.com/app/apikey)) ou OpenAI ([OpenAI Platform](https://platform.openai.com/api-keys))

### 2. Configuração do Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração do Arquivo `.env`
Copie o template `.env.example` para `.env` e preencha suas chaves:
```bash
cp .env.example .env
```
Exemplo de configuração utilizando Google Gemini:
```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=mba-ia-pull-evaluation-prompt
USERNAME_LANGSMITH_HUB=publichandle

GOOGLE_API_KEY=AIzaSy...
LLM_PROVIDER=google
LLM_MODEL=gemini-3.1-flash-lite
EVAL_MODEL=gemini-3.1-flash-lite
```

### 4. Comandos para Cada Fase do Projeto

#### Fase 1 — Pull do Prompt Inicial (`v1`) do LangSmith Hub
```bash
python src/pull_prompts.py
```
Conecta ao LangSmith Hub, baixa o prompt `leonanluppi/bug_to_user_story_v1` e salva em `prompts/bug_to_user_story_v1.yml`.

#### Fase 2 — Validação Local com Testes Automatizados (`pytest`)
```bash
pytest tests/test_prompts.py -v
```
Executa os 6 testes automatizados validando `prompts/bug_to_user_story_v2.yml`:
- `test_prompt_has_system_prompt`
- `test_prompt_has_role_definition`
- `test_prompt_mentions_format`
- `test_prompt_has_few_shot_examples`
- `test_prompt_no_todos`
- `test_minimum_techniques`

#### Fase 3 — Push do Prompt Otimizado (`v2`) ao LangSmith Hub
```bash
python src/push_prompts.py
```
Valida a estrutura de `prompts/bug_to_user_story_v2.yml` e publica `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2` como público no LangSmith Prompt Hub com tags e descrição.

#### Fase 4 — Execução da Avaliação e Experimentos no LangSmith
```bash
python src/evaluate.py
```
Cria/reutiliza o dataset `{LANGSMITH_PROJECT}-eval` com os 15 exemplos de `datasets/bug_to_user_story.jsonl`, puxa o prompt `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2` do Hub, executa o experimento avaliando as 5 métricas (`Helpfulness`, `Correctness`, `F1-Score`, `Clarity`, `Precision`) e grava os feedbacks no LangSmith.