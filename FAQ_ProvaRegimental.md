# FAQ — Gerador de Provas Unicid

Perguntas frequentes sobre o uso do sistema. Para instruções detalhadas, consulte o [Manual do Usuário](Manual_Usuario_ProvaRegimental.md).

---

## Instalação e Requisitos

### 1. Preciso do Microsoft Word instalado?

**Depende do que você precisa.** Para gerar as provas em formato **DOCX**, o Word **não é necessário** — o sistema cria os arquivos diretamente. No entanto, se você marcar a opção **"Incluir PDF no download"**, o sistema utiliza o Word instalado localmente para realizar a conversão para PDF. Sem o Word, a geração de DOCX funciona normalmente; apenas a exportação em PDF ficará indisponível.

---

### 2. O sistema funciona sem internet?

**Não.** O sistema é hospedado em nuvem e exige conexão para ser acessado em [https://prova-unicid.streamlit.app/](https://prova-unicid.streamlit.app/). Dentro do sistema, o fluxo via **XLSX não depende de serviços externos** — toda a geração é feita no servidor. Já o fluxo via **IA exige conexão adicional** com a API do Claude (Anthropic) durante o processamento do documento.

---

### 3. Quais são os arquivos de template e onde os coloco?

O sistema exige quatro arquivos DOCX de template na mesma pasta do aplicativo:

- `Modelo_AR.docx` — Prova Regimental, gabarito Padrão
- `Modelo_ARZ.docx` — Prova Regimental, gabarito Zipgrade
- `Modelo_AF.docx` — Prova Final, gabarito Padrão
- `Modelo_AFZ.docx` — Prova Final, gabarito Zipgrade

> Se algum desses arquivos estiver ausente ou corrompido, o sistema apresentará erro ao tentar gerar a prova correspondente. Mantenha backups desses modelos.

---

## Fluxo via Planilha XLSX

### 4. Qual o formato correto da planilha de questões objetivas?

Cada linha da planilha representa uma questão. As colunas devem seguir esta ordem:

- **Coluna A:** enunciado da questão
- **Coluna B:** resposta correta
- **Colunas C a F:** distratores (alternativas incorretas)

Não é obrigatório incluir cabeçalho, mas é recomendado para facilitar a manutenção da planilha. O sistema embaralha automaticamente as alternativas (colunas B a F) em cada versão gerada.

---

### 5. Posso usar apenas dissertativas da IA e objetivas do XLSX (ou vice-versa)?

**Sim.** O campo **"Extrair"** no painel de IA permite selecionar apenas **Objetivas** ou apenas **Dissertativas**. Assim, você pode, por exemplo, carregar as questões objetivas via XLSX e usar a IA somente para gerar as questões dissertativas — ou o contrário. Os dois fluxos são combinados internamente pelo sistema para formar o conjunto final da prova.

---

## Fluxo via IA

### 6. A IA sempre gera as mesmas questões?

**Não.** A IA (Claude) utiliza amostragem probabilística, o que significa que, mesmo a partir do mesmo documento de origem, cada processamento pode gerar variações nas questões — diferenças de formulação, seleção de trechos e geração de distratores. Se as questões geradas não atenderem ao padrão esperado, use o botão **"Regenerar não confirmadas"** para solicitar uma nova tentativa.

---

### 7. Quais formatos de arquivo são aceitos para importação via IA?

O painel de importação via IA aceita os seguintes formatos:

- `.docx` — documentos Word
- `.xlsx` — planilhas Excel (sem necessidade de seguir o formato padrão do Fluxo 1)
- `.txt` — texto simples
- `.gs` — Google Apps Script exportado
- `.json` — dados estruturados em JSON

> **Dica:** qualquer documento elaborado pelo professor pode ser utilizado como fonte — slides, apostilas, questionários, listas de exercícios, etc.

---

### 8. Posso usar Google Forms como fonte para a IA?

**Sim, de forma indireta.** O Google Forms não exporta diretamente em nenhum dos formatos aceitos, mas você pode:

1. Exportar as respostas ou o formulário para **Google Planilhas** e depois baixar como `.xlsx`.
2. Copiar as questões do formulário para um arquivo `.txt` ou `.docx` e importar esse arquivo.
3. Exportar o script do formulário em `.gs` (Google Apps Script) e importar diretamente.

---

### 9. A chave da API fica salva no sistema?

**Não.** A chave da API é inserida diretamente no campo de texto e utilizada apenas durante a sessão ativa no navegador. Ela **não é gravada em disco**, não é enviada para nenhum servidor além da API da Anthropic, e é descartada ao recarregar a página ou encerrar o navegador.

> Guarde sua chave em um gerenciador de senhas e insira-a a cada sessão de trabalho.

---

### 10. Qual o custo de uso da IA?

O custo estimado é de aproximadamente **US$ 0,10 por processamento** (chamada à API do Claude). O valor real pode variar de acordo com:

- O volume de texto enviado (documentos maiores consomem mais tokens).
- O modelo Claude selecionado internamente pelo sistema.
- A tabela de preços vigente da Anthropic, que pode ser consultada em [anthropic.com/pricing](https://anthropic.com/pricing).

Regenerar questões não confirmadas gera uma nova chamada à API, com custo adicional.

---

### 11. O que fazer se a IA não gerou questões dissertativas?

Verifique os seguintes pontos:

1. Certifique-se de que o campo **"Extrair"** está configurado como **"Ambas"** ou **"Dissertativas"** — não apenas **"Objetivas"**.
2. Confirme que o documento de origem contém conteúdo suficiente e claro para que a IA identifique questões abertas.
3. Tente **Regenerar não confirmadas** para solicitar uma nova tentativa.
4. Se o problema persistir, tente fornecer um documento mais estruturado, com enunciados claramente delimitados (ex.: numerados ou separados por parágrafos).

---

### 12. Posso gerar apenas Prova Final (AF) com a IA?

**Sim.** O fluxo via IA não está restrito ao tipo AR. Basta selecionar **AF** como tipo de avaliação, usar o campo **"Extrair"** com **"Objetivas"** (ou "Ambas", sem prejuízo) e aprovar ao menos 20 questões objetivas. Para provas AF, questões dissertativas não são utilizadas.

---

## Configuração e Geração

### 13. Quantas versões posso gerar?

O sistema suporta até **8 versões** em uma única geração, identificadas pelas letras **A a H**. O número é definido pelo controle deslizante na seção de configuração. Para turmas que necessitem de mais variação, você pode repetir o processo com um pool diferente de questões.

---

### 14. O que é Zipgrade?

**Zipgrade** é um aplicativo (iOS/Android) que realiza correção automática de provas por leitura óptica, de forma semelhante a um gabarito de bolinha. Ao selecionar o tipo de gabarito **Zipgrade**, o sistema utiliza o template `Modelo_ARZ.docx` ou `Modelo_AFZ.docx`, que inclui o cartão-resposta no formato compatível com o aplicativo. O professor fotografa os cartões preenchidos pelos alunos e o Zipgrade faz a correção automaticamente.

---

### 15. Como funciona o gabarito gerado pelo sistema?

O arquivo de gabarito é um documento de texto simples incluído no ZIP de download. Ele lista, para **cada versão** gerada, a sequência de respostas corretas das questões objetivas, já considerando o embaralhamento aplicado naquela versão específica. Isso significa que a resposta correta para a Questão 1 na Versão A pode ser diferente da Versão B — o gabarito reflete essa diferença.

> Sempre confira o gabarito antes da aplicação da prova para garantir que corresponde ao conteúdo gerado.

---

### 16. Como garantir variedade entre as versões?

A variedade entre versões depende diretamente do **tamanho do pool de questões** disponível. O sistema embaralha as questões e alternativas entre versões, mas se o pool tiver exatamente o mínimo necessário (ex.: 8 objetivas para AR), todas as versões conterão as mesmas questões — apenas com alternativas em ordem diferente. Para obter questões distintas entre versões:

- **Via XLSX:** inclua mais linhas do que o mínimo necessário na planilha.
- **Via IA:** aprove mais questões do que o mínimo na etapa de revisão.

> O próprio sistema exibe uma dica de diversidade indicando quantas questões extras estão disponíveis no pool atual.

---

### 17. O que significa "pool de questões"?

"Pool" é o conjunto total de questões aprovadas e disponíveis para sorteio em uma sessão. Para cada versão da prova, o sistema seleciona aleatoriamente o número necessário de questões a partir deste pool. Quanto maior o pool em relação ao mínimo necessário, maior a probabilidade de que versões diferentes apresentem questões distintas.

**Exemplo prático:** com um pool de 24 objetivas para uma prova AR (que requer 8), cada versão pode receber 8 questões completamente diferentes das demais.

---

## Problemas e Casos Limítrofes

### 18. O sistema trava ou apresenta erro durante a geração. O que fazer?

Verifique as causas mais comuns:

1. **Templates ausentes:** confirme que os quatro arquivos `Modelo_*.docx` estão na pasta do aplicativo.
2. **Planilha com formato incorreto:** verifique se as colunas da XLSX seguem o padrão descrito no manual.
3. **Questões insuficientes:** para AR, são necessárias ao menos 8 objetivas e 2 ou 3 dissertativas. Para AF, ao menos 20 objetivas.
4. **Erro de API:** se o erro ocorrer durante o processamento com IA, verifique se a chave da API está correta e se há saldo disponível na conta Anthropic.
5. **Recarregue a página** no navegador (`F5`) e tente novamente.

---

### 19. Posso reutilizar planilhas de semestres anteriores?

**Sim.** As planilhas XLSX não têm prazo de validade e podem ser reutilizadas em qualquer semestre. Recomenda-se manter um arquivo de questões por disciplina e ir acrescentando novas questões ao longo do tempo para ampliar o pool disponível.

---

### 20. O PDF gerado é diferente do DOCX?

O PDF é uma conversão fiel do DOCX, realizada pelo Microsoft Word. O conteúdo e o layout são idênticos — o PDF é fornecido apenas como alternativa de formato para distribuição ou impressão, garantindo que a formatação não seja alterada em diferentes computadores.

---

---

## Configurações e Persistência

### 21. Onde configuro meu nome de professor?

Na aba **⚙️ Configurações**. Preencha o campo **Nome do professor**, ajuste as demais preferências (gabarito, discursivas, linhas de resposta, PDF) e clique em **💾 Salvar como padrão**. As configurações ficam salvas no navegador e são carregadas automaticamente nas próximas sessões.

---

### 22. Minhas configurações sumiram. Por quê?

As preferências são salvas no **localStorage do navegador** deste dispositivo específico. Elas podem sumir se:
- Você acessou o app em outro computador ou navegador.
- O histórico/dados do navegador foram limpos.
- O modo de navegação anônima foi usado (dados não persistem).

Para restaurar as configurações padrão do sistema, clique em **↺ Restaurar padrão** na aba Configurações.

---

### 23. Posso usar o Fluxo IA e o Fluxo XLSX ao mesmo tempo?

**Sim.** As duas origens de questões são combinadas automaticamente pelo sistema. Você pode, por exemplo, carregar questões objetivas via XLSX (sub-aba **📊 Planilha XLSX**) e usar a IA apenas para as dissertativas (sub-aba **🤖 Importar por IA**), ou o contrário. Quando ambas as fontes estiverem ativas, o XLSX tem prioridade sobre as questões da IA.

---

### 24. O campo de imagens desapareceu da tela principal. Onde está?

O upload de imagens e o painel DALL-E agora são **opt-in**: eles só aparecem quando você marca a caixa **"Incluir imagens nas provas"** na aba Gerador. Se a caixa estiver desmarcada, as seções ficam ocultas para manter a tela limpa.

---

*Dúvidas não listadas aqui? Consulte o [Manual do Usuário](Manual_Usuario_ProvaRegimental.md) ou entre em contato com a equipe de desenvolvimento.*
