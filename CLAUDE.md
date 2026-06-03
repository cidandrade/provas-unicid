# provas-unicid — Contexto do projeto

App **Streamlit** (`app.py`, ~3000 linhas) que gera provas regimentais (AR) e
finais (AF) em DOCX/PDF para a UNICID. Autores: Prof. Cid R. Andrade e
Prof. Rafael Cotrin (v3.4.0+).

## Travas (não negociáveis)

- **Não migrar de framework.** Manter Streamlit. Nada de NiceGUI, Reflex, React.
- **Não alterar as funções de domínio**: geração de documento (`criar_prova`,
  `gera_prova_bytes`, `gera_gabarito_str`, `docx_*`, `_injetar_*`,
  `replace_text_in_paragraph_runs`), leitura de XLSX (`get_questoes_*`,
  `_ler_enunciados_*`), os prompts (`_prompt_*`) e as chamadas às APIs
  Anthropic/OpenAI (`_chamar_api_claude`, `_gerar_imagem_dalle`,
  `processar_com_claude`). São o núcleo do app e devem ficar intactas.
- **Fluxo de Git liberado na `main`.** Commits diretos na `main` são permitidos;
  branch + Pull Request é opcional. `push --force` e `git reset --hard` também
  estão liberados — usar com cautela, pois há co-autor no histórico.
- **Segredos** (chaves Anthropic/OpenAI) ficam em variáveis de ambiente /
  secrets, nunca no código nem neste arquivo.

## Design System

A fidelidade visual deve vir do **theming nativo** em `.streamlit/config.toml`
(cores, fontes, raios, tamanhos). O CSS injetado em `_inject_css()` fica
reduzido a uma camada mínima, só para o que o tema nativo não cobre.

Regra: **não** estilizar via seletores `data-testid` + `!important` quando
existir opção nativa equivalente no `config.toml`. Onde fizer sentido, preferir
componentes nativos (ex.: `st.container(border=True)` no lugar de cards via CSS).

Tokens, fontes e o passo a passo completo da migração do DS estão em:
@docs/INSTRUCAO_DS.md
