# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# provas-unicid — Contexto do projeto

App **Streamlit** (`app.py`, ~3000 linhas) que gera provas regimentais (AR) e
finais (AF) em DOCX/PDF para a UNICID. Autores: Prof. Cid R. Andrade e
Prof. Rafael Cotrin (v3.4.0+).

## Comandos

```bash
# Executar o app localmente
streamlit run app.py

# Instalar dependências
pip install -r requirements.txt
```

Não há testes automatizados nem linter configurado. A verificação é visual,
rodando o app e exercitando os fluxos de geração de prova/gabarito.

## Arquitetura

`app.py` é um único arquivo organizado em camadas:

**Camada de domínio (funções puras — não alterar):**
- Geração de documento DOCX: `criar_prova`, `gera_prova_bytes`, `gera_gabarito_str`, `gera_gabarito_html`, funções `docx_*` e `_injetar_*`, `replace_text_in_paragraph_runs`
- Leitura de XLSX: `get_questoes_xlsx`, `get_questoes_dissertativas_xlsx`, `_ler_enunciados_xlsx_obj`, `_ler_enunciados_xlsx_dis`
- Chamadas à IA: `_chamar_api_claude`, `processar_com_claude`, `regenerar_nao_confirmadas`, `_gerar_imagem_dalle`, `_gerar_prompts_imagem_claude`
- Prompts: `_prompt_objetivas`, `_prompt_dissertativas`

**Camada de UI (funções `_ui_*`):**
- `_ui_configuracoes(ls)` — aba ⚙️, persiste em localStorage
- `_ui_importar_ia()` — sub-aba de importação por IA (Claude/ChatGPT)
- `_ui_dalle_imagens()` — geração de imagens para questões via DALL-E
- `_ui_manual()` / `_ui_faq()` — abas de documentação estática

**Entry point:**
- `main()` — configura a página, injeta CSS, carrega configurações do localStorage e monta as 4 abas (`tab_ger`, `tab_cfg`, `tab_man`, `tab_faq`)

### Modelos DOCX

Quatro arquivos `.docx` na raiz servem de template, selecionados pelo dict `MODELOS`:

| Chave | Arquivo |
| --- | --- |
| `("R", "Padrão")` | `Modelo_AR.docx` |
| `("R", "Zipgrade")` | `Modelo_ARZ.docx` |
| `("F", "Padrão")` | `Modelo_AF.docx` |
| `("F", "Zipgrade")` | `Modelo_AFZ.docx` |

`gera_prova_bytes` abre o modelo, substitui placeholders de texto via
`replace_text_in_paragraph_runs` e injeta questões, alternativas e linhas de
resposta diretamente no XML do `python-docx`.

### Versões da prova

Até 8 versões (A–H), cada uma identificada por um símbolo de rodapé em
`SIMBOLOS_PROVA`. As alternativas são embaralhadas por versão; o gabarito
é calculado e exportado em texto ou HTML.

### Persistência de configurações

`CONFIG_DEFAULTS` + `_LS_KEYS` definem as 5 preferências do professor (nome,
tipo de gabarito, nº de dissertativas, nº de linhas, incluir PDF). São lidas e
gravadas no `localStorage` do navegador via `streamlit-local-storage`, com
fallback para `st.session_state` quando o pacote não está instalado.

### Dependências opcionais

Importadas com `try/except` no topo do arquivo — a ausência de cada uma
degrada graciosamente:
- `docx2pdf` — conversão para PDF (Linux usa LibreOffice via subprocess)
- `anthropic` — importação de questões e geração de imagens via Claude
- `openai` — geração de imagens via DALL-E
- `streamlit-local-storage` — persistência de configurações entre sessões
- `json_repair` — tolerância a JSON malformado retornado pela IA

### Formato XLSX esperado

Coluna A = enunciado, coluna B = resposta correta, colunas C–F = distratores.
Primeira linha = primeira questão (sem linha de cabeçalho).
Formatação inline: `*itálico*`, `**negrito**`, `***negrito e itálico***`.
Tags de imagem: `[img:nome_arquivo]` no enunciado.

## Travas (não negociáveis)

- **Não migrar de framework.** Manter Streamlit. Nada de NiceGUI, Reflex, React.
- **Não alterar as funções de domínio** listadas acima. São o núcleo do app e devem ficar intactas.
- **Fluxo de Git liberado na `main`.** Commits diretos na `main` são permitidos;
  branch + Pull Request é opcional. `push --force` e `git reset --hard` também
  estão liberados — usar com cautela, pois há co-autor no histórico.
- **Segredos** (chaves Anthropic/OpenAI) ficam em variáveis de ambiente /
  secrets, nunca no código nem neste arquivo.

## Design System

A fidelidade visual vem do **theming nativo** em `.streamlit/config.toml`
(cores `#18A89B`, fontes Inter/Libre Baskerville/Roboto Mono, raio `6px`).
As fontes estão auto-hospedadas em `static/fonts/` com `enableStaticServing = true`.

`_inject_css()` mantém apenas o que o tema nativo não cobre:
- cabeçalho teal (`div.app-header`)
- botão secundário outline
- cores dos alertas (success/warning/error/info)
- sombra dos expanders

Regra: **não** estilizar via seletores `data-testid` + `!important` quando
existir opção nativa equivalente no `config.toml`. Onde fizer sentido, preferir
`st.container(border=True)` no lugar de cards via CSS.

Tokens completos e histórico da migração: `@docs/INSTRUCAO_DS.md`
