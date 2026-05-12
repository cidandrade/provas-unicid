"""
Gerador de Provas Unicid - Versão Web
Versão 3.1.0
Gera provas com questões de múltipla escolha e dissertativas,
já no formato da Unicid

Autor: Cid R Andrade (profandrade@gmail.com)
Data desta versão: maio/2026

Formato do arquivo XLSX de questões OBJETIVAS:
- Coluna A: Enunciado
- Coluna B: Resposta Correta
- Colunas C–F: Distratores (4 opções incorretas)
A primeira linha deve ser a primeira questão (sem cabeçalho).

Formato do arquivo XLSX de questões DISSERTATIVAS:
- Coluna A: Enunciado
A primeira linha deve ser a primeira questão (sem cabeçalho).

Este programa é Software Livre licenciado sob a GPL v3+.
Veja https://www.gnu.org/licenses/ para mais detalhes.

ChangeLog
3.1.0 maio/2026:  Regimental passa a usar Modelo_AR2.docx com 3 dissertativas
                  (questões 9, 10, 11 sorteadas aleatoriamente)
3.0.1 maio/2026:  Preenchimento automático de {{Sem aqui}} (1 ou 2) e
                  {{Ano aqui}} (ano corrente) nos templates DOCX
3.0.0 maio/2026:  Migração para Streamlit; entrada via XLSX; sem dependência
                  do Google Colab ou Google Drive; download em ZIP
"""

import streamlit as st
import random
import os
import zipfile
from io import BytesIO
from docx import Document
from datetime import datetime
import openpyxl

# --- Configurações Globais ---

SIMBOLOS_PROVA = {
    "A": "**",
    "B": "==",
    "C": "%%",
    "D": "//",
    "E": "[]",
    "F": "##",
    "G": "!!",
    "H": "()"
}

LETRAS_PROVA = list(SIMBOLOS_PROVA.keys())
ABC = "ABCDE"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_AR = os.path.join(BASE_DIR, "Modelo_AR2.docx")
MODELO_AF = os.path.join(BASE_DIR, "Modelo_AF.docx")


# --- Funções de Lógica Central (mantidas do prova.py) ---

def replace_text_in_paragraph_runs(paragraph, old_text, new_text, bold_prefix=False):
    """
    Substitui um texto em um parágrafo, lidando com múltiplas 'runs'.
    Preserva a formatação ao redor e aplica negrito ao prefixo (A), (B)...
    se bold_prefix for True.

    Quando o placeholder está inteiramente num único run e bold_prefix é False,
    substitui só o texto desse run para preservar outros elementos do parágrafo
    (ex: campos de numeração de página w:fldChar).
    """
    if old_text not in paragraph.text:
        return False

    # Caso simples: placeholder em um único run e sem necessidade de bold_prefix.
    # Substitui só esse run, preservando os demais elementos (ex: w:fldChar).
    if not bold_prefix:
        for run in paragraph.runs:
            if old_text in run.text:
                run.text = run.text.replace(old_text, new_text)
                return True

    # Caso complexo: placeholder pode estar dividido entre runs, ou bold_prefix
    # requer divisão em múltiplos runs. Reconstrói o parágrafo inteiro.

    # Captura formatação do run que contém o placeholder (ou o primeiro run)
    ref_run = None
    for run in paragraph.runs:
        if ref_run is None:
            ref_run = run
        if old_text in run.text:
            ref_run = run
            break

    original_text = "".join(run.text for run in paragraph.runs)
    paragraph.clear()
    parts = original_text.split(old_text)

    def add_run(text):
        r = paragraph.add_run(text)
        if ref_run is not None:
            r.bold = ref_run.bold
            r.italic = ref_run.italic
            r.underline = ref_run.underline
            if ref_run.font.name:
                r.font.name = ref_run.font.name
            if ref_run.font.size:
                r.font.size = ref_run.font.size
        return r

    for i, part in enumerate(parts):
        add_run(part)
        if i < len(parts) - 1:
            if bold_prefix:
                temp = new_text
                while True:
                    match = False
                    for char in ABC:
                        prefix = f"({char})"
                        if prefix in temp:
                            before, temp = temp.split(prefix, 1)
                            if before:
                                add_run(before)
                            bold_run = add_run(prefix)
                            bold_run.bold = True
                            match = True
                            break
                    if not match:
                        if temp:
                            add_run(temp)
                        break
            else:
                add_run(new_text)

    return True


def all_paragraphs(document):
    """
    Itera sobre todos os parágrafos do documento: corpo, tabelas, cabeçalhos,
    rodapés e Structured Document Tags (w:sdt), percorrendo recursivamente.
    """
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph

    _CONTAINER_TAGS = {
        qn("w:body"), qn("w:tbl"), qn("w:tr"), qn("w:tc"),
        qn("w:hdr"), qn("w:ftr"),
        qn("w:sdt"), qn("w:sdtContent"),
    }

    def _iter(element):
        for child in element:
            if child.tag == qn("w:p"):
                yield Paragraph(child, element)
            elif child.tag in _CONTAINER_TAGS:
                yield from _iter(child)

    yield from _iter(document.element.body)
    for section in document.sections:
        yield from _iter(section.header._element)
        yield from _iter(section.footer._element)


def criar_prova(nome_prova, simbolo_rodape, qt_questoes, questoes_selecionadas):
    """
    Cria o conteúdo de uma prova (questões objetivas formatadas e gabarito).
    Retorna (lista_de_textos_de_questões, string_gabarito).
    """
    lista_questoes = []
    gabarito = "GABARITO\n"

    for indice, questao_tupla in enumerate(questoes_selecionadas, start=1):
        pergunta_texto = questao_tupla[0]
        resposta_correta_texto = questao_tupla[1]
        opcoes_originais = list(questao_tupla[2:])

        questao_texto_completo = pergunta_texto + "\n\n"

        opcoes_com_indice = [(opcoes_originais[j], j) for j in range(len(opcoes_originais))]
        random.shuffle(opcoes_com_indice)

        posicao_resposta_correta = -1
        for opcao_indice_exibicao, (opcao_texto, _) in enumerate(opcoes_com_indice):
            questao_texto_completo += f"({ABC[opcao_indice_exibicao]}) {opcao_texto}\n"
            if opcao_texto.lower().replace(" ", "") == resposta_correta_texto.lower().replace(" ", ""):
                posicao_resposta_correta = opcao_indice_exibicao

        lista_questoes.append(questao_texto_completo)

        if posicao_resposta_correta != -1:
            gabarito += f"{indice}: {ABC[posicao_resposta_correta]}\n"
        else:
            gabarito += f"{indice}: ERRO (Resposta não identificada para '{pergunta_texto[:40]}...')\n"

    return lista_questoes, gabarito


# --- Funções de I/O adaptadas para Streamlit ---

def get_questoes_xlsx(uploaded_file):
    """
    Lê questões objetivas de um arquivo XLSX.
    Espera: A=Enunciado, B=Resposta correta, C–F=Distratores.
    Retorna lista de tuplas ou None em caso de erro.
    """
    questoes = []
    try:
        wb = openpyxl.load_workbook(uploaded_file, read_only=True, data_only=True)
        ws = wb.active
        for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if not row or all(cell is None for cell in row):
                continue
            if len(row) < 6:
                st.warning(f"Linha {i}: menos de 6 colunas. Ignorando.")
                continue
            pergunta = str(row[0]).strip() if row[0] is not None else ""
            resposta_correta = str(row[1]).strip() if row[1] is not None else ""
            distratores = [
                str(row[j]).strip() if row[j] is not None else ""
                for j in range(2, 6)
            ]
            if not all([pergunta, resposta_correta] + distratores):
                st.warning(f"Linha {i}: célula vazia em coluna essencial (A–F). Ignorando.")
                continue
            alternativas = [resposta_correta] + distratores
            questoes.append((pergunta, resposta_correta, *alternativas))
        wb.close()
    except Exception as e:
        st.error(f"Erro ao ler questões objetivas: {e}")
        return None

    if not questoes:
        return None
    return questoes


def get_questoes_dissertativas_xlsx(uploaded_file):
    """
    Lê questões dissertativas de um arquivo XLSX.
    Espera: A=Enunciado.
    Retorna lista de strings ou None em caso de erro.
    """
    questoes = []
    try:
        wb = openpyxl.load_workbook(uploaded_file, read_only=True, data_only=True)
        ws = wb.active
        for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if not row or row[0] is None:
                continue
            enunciado = str(row[0]).strip()
            if enunciado:
                questoes.append(enunciado)
            else:
                st.warning(f"Linha {i}: enunciado vazio. Ignorando.")
        wb.close()
    except Exception as e:
        st.error(f"Erro ao ler questões dissertativas: {e}")
        return None

    if not questoes:
        return None
    return questoes


def gera_prova_bytes(modelo_caminho, identificador_prova, questoes_formatadas,
                     simbolo_rodape, tipo_avaliacao, questoes_dissertativas=None):
    """
    Preenche o template DOCX com as questões e retorna os bytes do arquivo gerado.
    """
    try:
        document = Document(modelo_caminho)

        # Substitui placeholders das questões objetivas
        for i, questao_texto in enumerate(questoes_formatadas, start=1):
            placeholder = f"{{{{Questão {i} aqui}}}}"
            for paragraph in document.paragraphs:
                if replace_text_in_paragraph_runs(paragraph, placeholder, questao_texto, bold_prefix=True):
                    break

        # Substitui as questões dissertativas (AR: posições 9, 10, 11)
        if questoes_dissertativas:
            for idx, texto_diss in enumerate(questoes_dissertativas, start=9):
                placeholder_diss = f"{{{{Questão {idx} aqui}}}}"
                for paragraph in document.paragraphs:
                    if replace_text_in_paragraph_runs(paragraph, placeholder_diss, texto_diss):
                        break

        # Substitui o símbolo da versão no rodapé (pode haver mais de uma ocorrência)
        for paragraph in all_paragraphs(document):
            replace_text_in_paragraph_runs(paragraph, "{{simbolo aqui}}", simbolo_rodape)

        # Substitui semestre e ano (buscando também em células de tabela)
        agora = datetime.now()
        semestre = "1" if agora.month <= 6 else "2"
        ano = str(agora.year)
        for paragraph in all_paragraphs(document):
            replace_text_in_paragraph_runs(paragraph, "{{Sem aqui}}", semestre)
        for paragraph in all_paragraphs(document):
            replace_text_in_paragraph_runs(paragraph, "{{Ano aqui}}", ano)

        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        st.error(f"Erro ao gerar prova {identificador_prova}: {e}")
        return None


def gera_gabarito_str(gabaritos_por_prova, tipo_avaliacao):
    """Gera o conteúdo do gabarito geral como string UTF-8."""
    nome_completo = "Regimental" if tipo_avaliacao == "R" else "Final"
    linhas = [f"--- GABARITO GERAL - AVALIAÇÃO {nome_completo.upper()} ---\n"]
    for nome_prova, gabarito_texto in gabaritos_por_prova.items():
        linhas.append(f"PROVA {nome_prova}\n{gabarito_texto}\n{'=' * 30}\n")
    return "\n".join(linhas)


# --- Interface Streamlit ---

def main():
    st.set_page_config(
        page_title="Gerador de Provas Unicid",
        page_icon="📝",
        layout="centered"
    )

    st.title("Gerador de Provas Unicid")
    st.caption("Versão 3.1.0 · Cid R Andrade · profandrade@gmail.com")

    st.divider()

    # 1. Tipo de avaliação
    tipo_label = st.radio(
        "Tipo de avaliação",
        ["Regimental — AR  (8 objetivas + 3 dissertativas)", "Final — AF  (20 objetivas)"],
        horizontal=True
    )
    tipo_codigo = "R" if "Regimental" in tipo_label else "F"
    modelo_caminho = MODELO_AR if tipo_codigo == "R" else MODELO_AF
    qt_questoes_objetivas = 8 if tipo_codigo == "R" else 20

    st.divider()

    # 2. Upload de questões objetivas
    st.subheader("Questões objetivas")
    st.caption(
        "Planilha XLSX: **coluna A** = enunciado · **coluna B** = resposta correta "
        "· **colunas C–F** = distratores.  \nA primeira linha deve ser a primeira questão "
        "(sem linha de cabeçalho)."
    )
    arquivo_objetivas = st.file_uploader(
        "Carregar arquivo de questões objetivas (.xlsx)",
        type=["xlsx"],
        key="objetivas"
    )

    # 3. Upload de questões dissertativas (somente AR)
    arquivo_dissertativas = None
    if tipo_codigo == "R":
        st.subheader("Questões dissertativas")
        st.caption(
            "Planilha XLSX: **coluna A** = enunciado.  \n"
            "A primeira linha deve ser a primeira questão (sem linha de cabeçalho)."
        )
        arquivo_dissertativas = st.file_uploader(
            "Carregar arquivo de questões dissertativas (.xlsx)",
            type=["xlsx"],
            key="dissertativas"
        )

    st.divider()

    # 4. Número de versões
    qt_versoes = st.slider("Número de versões da prova", min_value=1, max_value=8, value=4)
    st.caption(f"Serão geradas as versões: {', '.join(LETRAS_PROVA[:qt_versoes])}")

    st.divider()

    # 5. Botão de geração
    gerar = st.button("Gerar Provas", type="primary", use_container_width=True)

    if gerar:
        # --- Validações ---
        if arquivo_objetivas is None:
            st.error("Carregue o arquivo de questões objetivas antes de continuar.")
            return

        if tipo_codigo == "R" and arquivo_dissertativas is None:
            st.error("Carregue o arquivo de questões dissertativas antes de continuar.")
            return

        if not os.path.exists(modelo_caminho):
            st.error(
                f"Arquivo de modelo '{os.path.basename(modelo_caminho)}' não encontrado. "
                "Contate o administrador do sistema."
            )
            return

        # --- Geração ---
        with st.spinner("Lendo questões e gerando provas..."):

            questoes_objetivas = get_questoes_xlsx(arquivo_objetivas)
            if not questoes_objetivas:
                st.error("Nenhuma questão objetiva válida encontrada. Verifique o arquivo XLSX.")
                return

            if len(questoes_objetivas) < qt_questoes_objetivas:
                st.error(
                    f"São necessárias **{qt_questoes_objetivas}** questões objetivas, "
                    f"mas o arquivo contém apenas **{len(questoes_objetivas)}**."
                )
                return

            questoes_dissertativas = None
            qt_dissertativas = 3
            if tipo_codigo == "R":
                questoes_dissertativas = get_questoes_dissertativas_xlsx(arquivo_dissertativas)
                if not questoes_dissertativas:
                    st.error("Nenhuma questão dissertativa válida encontrada. Verifique o arquivo XLSX.")
                    return
                if len(questoes_dissertativas) < qt_dissertativas:
                    st.error(
                        f"São necessárias ao menos **{qt_dissertativas}** questões dissertativas, "
                        f"mas o arquivo contém apenas **{len(questoes_dissertativas)}**."
                    )
                    return

            gabaritos = {}
            zip_buffer = BytesIO()
            erros = []

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for i in range(qt_versoes):
                    nome_prova = LETRAS_PROVA[i]
                    simbolo = SIMBOLOS_PROVA[nome_prova]

                    questoes_selecionadas = random.sample(questoes_objetivas, qt_questoes_objetivas)
                    questoes_formatadas, gabarito_da_prova = criar_prova(
                        nome_prova, simbolo, qt_questoes_objetivas, questoes_selecionadas
                    )

                    dissertativas_selecionadas = None
                    if tipo_codigo == "R" and questoes_dissertativas:
                        dissertativas_selecionadas = random.sample(questoes_dissertativas, qt_dissertativas)

                    gabaritos[nome_prova] = gabarito_da_prova

                    prova_bytes = gera_prova_bytes(
                        modelo_caminho, nome_prova, questoes_formatadas,
                        simbolo, tipo_codigo, dissertativas_selecionadas
                    )
                    if prova_bytes:
                        zf.writestr(f"prova_{nome_prova}.docx", prova_bytes)
                    else:
                        erros.append(nome_prova)

                # Gabarito geral
                gabarito_str = gera_gabarito_str(gabaritos, tipo_codigo)
                data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_completo = "Regimental" if tipo_codigo == "R" else "Final"
                nome_gabarito = f"Gabarito_Geral_{nome_completo}_{data_hora}.txt"
                zf.writestr(nome_gabarito, gabarito_str.encode("utf-8"))

        if erros:
            st.warning(f"Erro ao gerar as versões: {', '.join(erros)}. As demais foram incluídas no ZIP.")
        else:
            versoes_geradas = ", ".join(LETRAS_PROVA[:qt_versoes])
            st.success(f"{qt_versoes} versão(ões) gerada(s) com sucesso: {versoes_geradas}")

        zip_buffer.seek(0)
        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_zip = f"provas_{nome_completo}_{data_hora}.zip"

        st.download_button(
            label="Baixar ZIP com todas as provas",
            data=zip_buffer,
            file_name=nome_zip,
            mime="application/zip",
            use_container_width=True
        )


if __name__ == "__main__":
    main()
