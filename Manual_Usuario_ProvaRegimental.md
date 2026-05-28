# Manual do Usuário — Gerador de Provas Unicid

**Versão do sistema:** 3.7.0
**Autores:** Cid R Andrade · Co-Autor: Prof. Me. Rafael Cotrin (v3.4.0+)

---

## 1. Introdução

O **Gerador de Provas Unicid** é uma aplicação local desenvolvida em Python/Streamlit que automatiza a criação de avaliações institucionais nos padrões da Unicid. O sistema produz múltiplas versões de uma mesma prova — com questões embaralhadas — garantindo integridade acadêmica em ambientes presenciais.

Principais capacidades:

- Geração de provas **AR** (Regimental) e **AF** (Final) em formato DOCX e PDF.
- Suporte a dois fluxos de entrada: **planilha XLSX** (método tradicional) ou **importação via IA** (Claude AI, para documentos não estruturados).
- Geração de até **8 versões** (A a H) com embaralhamento automático das alternativas e questões.
- Exportação em **ZIP** contendo todos os arquivos DOCX, PDFs opcionais e gabarito em texto.

---

## 2. Requisitos

| Requisito | Observação |
|---|---|
| Navegador atualizado | Chrome, Edge, Firefox ou Safari |
| Conexão com internet | Necessária para acessar o sistema e para o fluxo via IA |
| Microsoft Word | Necessário **apenas** para geração de PDF (instalado no seu computador) |
| Chave da API Anthropic | Necessária **apenas** para o fluxo de importação via IA |

> O sistema roda integralmente na nuvem — nenhum software adicional precisa ser instalado pelo usuário.

---

## 3. Como Acessar

Acesse pelo navegador, sem instalação:

**https://prova-unicid.streamlit.app/**

> Compatível com qualquer navegador moderno (Chrome, Edge, Firefox, Safari).
> Não é necessário instalar nenhum software para usar o sistema.

---

## 4. Visão Geral da Interface

A interface está organizada em **quatro abas** no topo:

| Aba | O que contém |
|---|---|
| 🏠 **Gerador de Provas** | Fluxo principal: tipo, versões, disciplina, questões, imagens e geração |
| 📖 **Manual** | Esta documentação |
| ❓ **FAQ** | Perguntas frequentes |
| ⚙️ **Configurações** | Preferências do professor salvas no navegador (professor, gabarito, discursivas, PDF) |

### Aba Gerador de Provas

Dentro da aba Gerador, a organização é vertical:

1. **Tipo de avaliação** + **Número de versões** — linha superior.
2. **Disciplina** — campo de texto.
3. Sub-abas de origem das questões: **📊 Planilha XLSX** (padrão) ou **🤖 Importar por IA**.
4. **Incluir imagens nas provas** — checkbox opcional; quando marcado, revela upload manual de imagens e o painel DALL-E.
5. **Gerar Provas** — botão principal.

> As informações do professor, o tipo de gabarito, o número de questões dissertativas, o espaço de resposta e a opção de PDF são configurados **uma única vez** na aba ⚙️ Configurações e ficam salvos no navegador.

---

## 5. Fluxo 1 — Questões via Planilha XLSX

Este é o método padrão, indicado quando o professor já possui as questões organizadas em planilha.

### 5.1 Passo a Passo

1. **Na primeira utilização:** abra a aba ⚙️ Configurações, preencha o nome do professor e ajuste as demais preferências. Clique em **💾 Salvar como padrão** — as configurações ficam salvas no navegador.
2. Selecione o **Tipo de avaliação** (AR ou AF) na aba Gerador.
3. Ajuste o **Número de versões** com o controle deslizante.
4. Preencha o campo **Disciplina**.
5. Na sub-aba **📊 Planilha XLSX**, faça o upload da **planilha de questões objetivas**.
6. Se o tipo for AR, faça também o upload da **planilha de questões dissertativas** (aparece abaixo do upload de objetivas).
7. Clique em **Gerar Provas**.

### 5.2 Formato da Planilha de Questões Objetivas

A planilha deve ter as seguintes colunas (sem cabeçalho obrigatório, mas recomendado):

| Coluna | Conteúdo |
|---|---|
| A | Enunciado da questão |
| B | Resposta correta |
| C | Distrator 1 |
| D | Distrator 2 |
| E | Distrator 3 |
| F | Distrator 4 |

> **Regra:** cada linha representa uma questão. O sistema embaralha as alternativas (B a F) automaticamente em cada versão gerada.

### 5.3 Formato da Planilha de Questões Dissertativas

A planilha de dissertativas usa apenas **uma coluna**:

| Coluna | Conteúdo |
|---|---|
| A | Enunciado da questão dissertativa |

Não são necessárias colunas de resposta — as questões dissertativas destinam-se à resposta manuscrita do aluno.

### 5.4 Formatação de Texto nas Planilhas

O sistema reconhece marcações simples para aplicar estilos ao texto das questões:

| Marcação na célula | Resultado no documento |
|---|---|
| `*texto*` | *itálico* |
| `**texto**` | **negrito** |
| `***texto***` | ***negrito e itálico*** |

---

## 6. Fluxo 2 — Importação via IA

Este fluxo utiliza a API do **Claude AI (Anthropic)** para extrair e estruturar questões a partir de documentos não estruturados, como slides, apostilas ou listas de exercícios.

> **Custo estimado:** aproximadamente **US$ 0,10 por processamento** (sujeito a variação conforme volume de texto enviado e tabela de preços da Anthropic).

Para acessar este fluxo, clique na sub-aba **🤖 Importar por IA** dentro da aba Gerador.

### 6.1 Obtendo a Chave da API do Claude

1. Acesse [console.anthropic.com](https://console.anthropic.com).
2. Crie ou acesse sua conta Anthropic.
3. Vá em **API Keys** e gere uma nova chave (começa com `sk-ant-...`).
4. Copie a chave — ela será inserida diretamente no campo do sistema.

> **Atenção:** a chave da API **não é salva** pelo sistema. Ela é usada apenas durante a sessão ativa e descartada ao fechar o navegador ou recarregar a página.

### 6.2 Formatos de Arquivo Aceitos

O sistema aceita os seguintes tipos para importação via IA:

- `.docx` — documentos Word
- `.xlsx` — planilhas Excel (sem o formato padrão exigido no Fluxo 1)
- `.txt` — arquivos de texto simples
- `.gs` — Google Apps Script exportado
- `.json` — dados estruturados em JSON

> **Dica:** qualquer documento elaborado pelo professor pode ser utilizado — slides convertidos em texto, questionários do Google Forms exportados, listas de exercícios, etc.

### 6.3 Passo a Passo da Importação

1. Clique na sub-aba **🤖 Importar por IA** e insira sua **chave da API** no campo indicado.
2. Selecione no dropdown **Extrair** o tipo de questão desejado:
   - **Ambas** — extrai objetivas e dissertativas.
   - **Objetivas** — extrai apenas questões de múltipla escolha.
   - **Dissertativas** — extrai apenas questões dissertativas.
3. Faça o upload do(s) arquivo(s) de origem no campo de carregamento.
4. Clique em **Processar com IA**.

### 6.4 Revisão das Questões Geradas

![Painel de revisão das questões](Evidencias_manual_ProvaRegimental/Saída%20do%20modelo%20para%20avaliacao%20do%20professor.png)

Após o processamento, o sistema exibe cada questão extraída para revisão do professor:

- **✅ Aprovar** — inclui a questão no pool ativo.
- **❌ Rejeitar** — descarta a questão da sessão atual.

O painel mostra o enunciado completo, as alternativas e, para questões objetivas, a resposta correta e os distratores gerados.

> **Recomendação:** revise todas as questões com atenção antes de aprovar. A IA pode interpretar incorretamente termos técnicos ou contextos específicos da disciplina.

### 6.5 Regenerando Questões Rejeitadas

Clique em **Regenerar não confirmadas** para solicitar à IA que reprocesse as questões ainda não aprovadas. Isso é útil quando a formulação inicial não atendeu aos critérios de qualidade desejados.

### 6.6 Confirmando ou Descartando

![Painel de confirmação](Evidencias_manual_ProvaRegimental/Confirmação_dos%20dados.png)

Após revisar as questões, utilize os botões do painel de confirmação:

- **Usar questões aprovadas (X obj · Y dis)** — confirma o pool aprovado e habilita a geração da prova.
- **Descartar tudo** — remove todas as questões da sessão atual, permitindo recomeçar.

A mensagem de confirmação exibe o total de questões ativas: `"Questões ativas via IA: X objetiva(s) · Y dissertativa(s). Pronto para gerar a prova."`

### 6.7 Pool de Questões e Variedade

O sistema informa sobre **diversidade do pool**: quanto maior o número de questões aprovadas em relação ao mínimo necessário (8 objetivas e 2–3 dissertativas para AR), maior a variação entre as versões geradas, pois o sistema sorteia questões diferentes para cada versão.

> **Exemplo:** se você aprovar 16 objetivas para uma prova AR, o sistema poderá selecionar 8 diferentes para cada versão, aumentando significativamente a variedade entre as provas.

---

## 7. Configurações da Prova

As configurações estão divididas em duas partes: campos **por prova** (na aba Gerador) e **preferências do professor** (na aba ⚙️ Configurações, salvas no navegador).

### 7.1 Campos por prova (aba Gerador)

| Campo | Onde | Descrição |
|---|---|---|
| **Tipo de avaliação** | Aba Gerador | AR (8 obj + 2–3 dis) ou AF (20 obj) |
| **Número de versões** | Aba Gerador | Controle deslizante de 1 a 8 |
| **Disciplina** | Aba Gerador | Nome da disciplina para o cabeçalho |

### 7.2 Preferências do professor (aba ⚙️ Configurações)

Abra a aba **⚙️ Configurações**, ajuste os campos abaixo e clique em **💾 Salvar como padrão**. As preferências ficam salvas no navegador e são restauradas automaticamente nas próximas sessões.

| Preferência | Descrição |
|---|---|
| **Nome do professor** | Aparece no cabeçalho de todas as provas |
| **Tipo de gabarito** | Padrão ou Zipgrade (para leitura óptica) |
| **Questões discursivas (AR)** | 2 ou 3 questões dissertativas por prova |
| **Linhas de resposta** | Espaço para resposta manuscrita (1 a 20 linhas) |
| **Incluir PDF no download** | Gera também versões PDF além do DOCX |

> **Nota:** as preferências ficam salvas **neste navegador** e **neste dispositivo**. Em outro computador ou navegador, configure novamente e salve.

> **Restaurar padrões:** clique em **↺ Restaurar padrão** para voltar a todos os valores iniciais do sistema.

### 7.3 Pontuação automática

A pontuação é calculada automaticamente com base no tipo de avaliação e no número de dissertativas configurado:

**Para provas AR:**
- Valor por questão dissertativa: **3,00 ÷ número de dissertativas** (ex.: 1,50 pt cada para 2 questões).
- Total dissertativas: **3,00 pts** · Total objetivas: **2,00 pts** (8 × 0,25 pt).

**Para provas AF:**
- 20 questões objetivas com pontuação distribuída igualmente.

---

## 8. Geração e Download

Após configurar tudo, clique no botão **Gerar Provas**.

### 8.1 Conteúdo do ZIP

O arquivo ZIP para download contém:

- Um arquivo `.docx` para cada versão gerada (ex.: `Prova_AR_A.docx`, `Prova_AR_B.docx`, ...).
- Arquivos `.pdf` correspondentes (se a opção de PDF estiver marcada).
- Um arquivo de texto com o **gabarito** de todas as versões.

### 8.2 Estrutura do Documento DOCX

Cada arquivo DOCX segue a estrutura:

- **Cabeçalho:** dados institucionais, professor, disciplina e versão da prova.
- **Seção de questões objetivas:** formatada em **2 colunas** para melhor aproveitamento do espaço.
- **Quebra de página:** separação automática entre objetivas e dissertativas.
- **Seção de questões dissertativas:** formatada em **1 coluna**, com espaço em branco para resposta conforme configurado no slider.

### 8.3 Arquivo de Gabarito

O gabarito é um arquivo de texto simples que lista, para cada versão, a ordem correta das alternativas de todas as questões objetivas. O formato facilita a correção manual ou a importação em sistemas de correção.

---

## 9. Dicas de Uso

- **Faça um teste com poucas versões** antes de gerar o conjunto completo, para validar layout e pontuação.
- **Mantenha as planilhas XLSX com pelo menos o dobro de questões** do necessário para maximizar a variação entre versões.
- **Revise o gabarito** sempre após a geração — confirme que as respostas corretas correspondem ao esperado após o embaralhamento.
- **Ao usar a IA**, prefira documentos com enunciados completos e bem delimitados; listas numeradas ou com marcadores facilitam a extração.
- **Salve a chave da API** em local seguro (gerenciador de senhas), pois o sistema não a armazena entre sessões.
- **Nomeie as planilhas de forma descritiva** (ex.: `Questoes_Obj_Anatomia_2025.xlsx`) para facilitar o reaproveitamento em semestres futuros.

---

## 10. Limitações Conhecidas

- A geração de PDF depende do Microsoft Word instalado localmente — não funciona em ambientes de servidor sem o Word.
- O fluxo via IA requer conexão ativa com a internet durante o processamento; a geração das provas em si pode ser feita offline.
- A qualidade das questões geradas pela IA depende da clareza e estrutura do documento de origem — textos muito densos ou pouco organizados podem resultar em extrações imprecisas.
- O sistema não valida automaticamente a correção acadêmica das questões geradas pela IA — a revisão pelo professor é indispensável.
- Arquivos de template corrompidos ou fora do padrão Unicid podem causar erros de geração; mantenha backups dos quatro arquivos de modelo.
- O número máximo de versões é 8 (A a H); para turmas maiores, considere repetir a geração com diferentes sementes ou questões.
