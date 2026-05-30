# Instrução — Migração do Design System para theming nativo (Streamlit)

> Documento de referência para o Claude Code. Tarefa pontual: levar o Design
> System do CSS injetado frágil para o **theming nativo** do Streamlit.

## Contexto

`provas-unicid` é um app Streamlit (`app.py`) que gera provas em DOCX/PDF. Hoje o
Design System está implementado em `_inject_css()` com seletores `data-testid` e
`!important` — frágil e quebra entre versões do Streamlit. **Manter o Streamlit.
Não tocar na lógica de geração de documentos** (ver travas no `CLAUDE.md`).

## Objetivo

Migrar o máximo possível do DS para `.streamlit/config.toml` (theming nativo,
suportado e estável), reduzindo o CSS injetado a uma camada mínima só para o que
a configuração não alcança.

## Passos (nesta ordem)

1. **Base estável primeiro.** Ler o histórico do git. Identificar a última versão
   estável (tag/release ou o commit imediatamente anterior à reformulação da UI).
   Criar um branch de trabalho a partir dela: `git checkout -b ds-nativo <ref>`.
   Não reescrever o histórico do `main`. Ao final, abrir um Pull Request.

2. **Verificar a versão do Streamlit** instalada (`requirements.txt` / ambiente) e
   conferir, no `config.toml` reference dessa versão, os **nomes exatos das chaves
   de theming** — elas mudaram entre versões (ex.: o raio de borda pode ser
   `baseRadius` ou variação). Usar os nomes corretos para a versão em uso.

3. **Criar/atualizar `.streamlit/config.toml`** com o tema nativo:
   - `primaryColor = "#18A89B"`
   - `backgroundColor = "#FFFFFF"`
   - `secondaryBackgroundColor = "#F9FCF9"`
   - `textColor = "#2C3332"`
   - raio base ≈ `6px`
   - Fontes: corpo = **Inter**, títulos = **Libre Baskerville**, código =
     **Roboto Mono** (via `font`, `headingFont`, `codeFont`).
   - Registrar as fontes em blocos `[[theme.fontFaces]]` cobrindo **todos os pesos
     usados**: Inter 400/500/600, Libre Baskerville 400/700, Roboto Mono 400/500.
     Preferir **auto-hospedar** os arquivos de fonte em `static/` com
     `server.enableStaticServing = true`; se for mais rápido, apontar `url` para os
     arquivos de fonte do Google Fonts. Não deixar a tipografia dependendo apenas
     de `@import` em CSS.

4. **Enxugar `_inject_css()`.** Remover tudo que passou a ser coberto pelo
   `config.toml`: cores, fontes, cor do botão primário, bordas de input, fundo da
   sidebar. **Manter CSS apenas para o que o tema não cobre:**
   - botão secundário no estilo "outline" (borda + cor primária);
   - cores por tipo de alerta — success `#3EBD3E`, warning `#FAA311`,
     error `#D13B3B`, info `#2F76EB`;
   - sombra de cards/expanders — e, onde fizer sentido, trocar por
     `st.container(border=True)` (nativo, já respeita o tema) para eliminar CSS.

5. **Remover o banner "Interface em atualização"** do `main()` assim que o DS
   estiver consistente.

6. **Não alterar** nenhuma função de domínio (ver lista no `CLAUDE.md`).

7. **Testar:** rodar localmente (`streamlit run app.py`), validar visualmente que
   cores, as três fontes e os raios batem com os tokens, e confirmar que a geração
   de prova/gabarito continua funcionando.

8. **Commits pequenos e lógicos** e abrir o PR ao final com um resumo:
   - commit 1: branch a partir da base estável;
   - commit 2: `config.toml` + arquivos de fonte;
   - commit 3: enxugar `_inject_css()`;
   - commit 4: remover banner de aviso.

## Tokens de referência (Design System UNICID v1.0)

| Token | Valor |
| --- | --- |
| primary | `#18A89B` |
| primary-hover | `#15968A` |
| primary-active | `#127A74` |
| accent | `#A86018` |
| error | `#D13B3B` |
| success | `#3EBD3E` |
| warning | `#FAA311` |
| info | `#2F76EB` |
| neutral-light | `#F9FCF9` |
| neutral-base | `#E5E7E5` |
| neutral-medium | `#B0B5B0` |
| neutral-dark | `#213331` |
| text | `#2C3332` |
| radius-sm | `6px` |
| radius-md | `8px` |

Fontes: Libre Baskerville (títulos), Inter (corpo), Roboto Mono (código).
