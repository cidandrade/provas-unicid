# Gerador de Provas UNICID

App **Streamlit** que automatiza a criação de avaliações institucionais nos
padrões da UNICID — provas **AR** (Regimental) e **AF** (Final) em DOCX/PDF,
com múltiplas versões embaralhadas para garantir integridade acadêmica em
ambientes presenciais.

Em produção: **[prova-unicid.streamlit.app](https://prova-unicid.streamlit.app/)**

Autores: Prof. Cid R. Andrade · Co-autor: Prof. Me. Rafael Cotrin (v3.4.0+)

## O que faz

- Gera provas **AR** e **AF** em **DOCX** e, opcionalmente, **PDF**.
- Duas formas de entrada de questões:
  - **Planilha XLSX** — método tradicional (coluna A = enunciado, B = resposta
    correta, C–F = distratores).
  - **Importação via IA** (Claude/ChatGPT) — a partir de documentos não estruturados.
- Até **8 versões** (A–H) por prova, com alternativas e questões embaralhadas
  automaticamente por versão.
- **Gabarito** em texto ou HTML, com símbolo de identificação por versão.
- Geração de imagens para questões via **DALL-E**.
- Exportação em **ZIP** com todos os DOCX, PDFs opcionais e gabarito, nomeados
  por professor e data.
- Quatro modelos de documento (padrão / Zipgrade × AR / AF), preenchidos a
  partir dos templates `.docx` na raiz do projeto.
- Preferências do professor (nome, tipo de gabarito, nº de dissertativas, nº
  de linhas de resposta, incluir PDF) persistidas no `localStorage` do navegador.

## Executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

- Requer **Python 3.11+** (ambiente de referência: `.devcontainer`, imagem `python:3.11-bookworm`).
- Conversão para PDF exige Word (Windows/Mac) ou **LibreOffice** (Linux — ver `packages.txt`).
- Chaves de API (Anthropic/OpenAI) vão em variáveis de ambiente / secrets do
  Streamlit — nunca no código.

Dependências opcionais degradam graciosamente quando ausentes: `docx2pdf`
(PDF), `anthropic` (importação/imagens via Claude), `openai` (imagens via
DALL-E), `streamlit-local-storage` (persistência de preferências),
`json-repair` (tolerância a JSON malformado da IA).

## Estrutura

```
provas-unicid/
├── app.py                          # app inteiro (~3000 linhas) — ver arquitetura no CLAUDE.md
├── Modelo_AR.docx / Modelo_ARZ.docx    # templates: Regimental (padrão / Zipgrade)
├── Modelo_AF.docx / Modelo_AFZ.docx    # templates: Final (padrão / Zipgrade)
├── static/fonts/                   # fontes auto-hospedadas (Inter, Libre Baskerville, Roboto Mono)
├── .streamlit/config.toml          # Design System UNICID via theming nativo do Streamlit
├── docs/INSTRUCAO_DS.md            # tokens completos e histórico da migração do Design System
├── Manual_Usuario_ProvaRegimental.md
├── FAQ_ProvaRegimental.md
├── Evidencias_manual_ProvaRegimental/  # screenshots referenciados pelo manual
└── requirements.txt / packages.txt
```

## Documentação para o usuário final

O app expõe suas próprias abas de ajuda (⚙️ Configurações, 📖 Manual, ❓ FAQ),
com o conteúdo espelhado nestes arquivos:

- [Manual do Usuário](Manual_Usuario_ProvaRegimental.md) — fluxo completo, requisitos, formato do XLSX.
- [FAQ](FAQ_ProvaRegimental.md) — dúvidas comuns de instalação e uso.

## Design System

Fidelidade visual via **theming nativo** do Streamlit (`.streamlit/config.toml`):
cor primária `#18A89B`, fontes Inter / Libre Baskerville / Roboto Mono, raio
`6px`. Detalhes e tokens completos em [`docs/INSTRUCAO_DS.md`](docs/INSTRUCAO_DS.md).

## Contribuindo

Guia de arquitetura, funções de domínio (não alterar) e convenções do projeto
em [`CLAUDE.md`](CLAUDE.md). Não há testes automatizados nem linter — a
verificação é visual, rodando o app e exercitando os fluxos de geração.

## Licença

[GNU GPL v3](LICENSE)
