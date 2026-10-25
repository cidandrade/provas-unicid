# -*- coding: utf-8 -*-
"""
Leitura do BancoProvas (https://bco-provas.netlify.app) a partir do Gerador.

Acesso somente leitura ao Firestore do projeto unicid-b5a4d com uma conta de
serviço (credencial em st.secrets["gcp_service_account"], montada pelo app.py).
A conta de serviço ignora as Firestore rules, então as regras de acesso do
BancoProvas são reaplicadas aqui:
- só professores com status 'approved' em professors/{uid};
- regra dos 10%: quem contribuiu com >= 10% das questões ativas da disciplina
  vê todas; os demais veem só as próprias.

ESPELHO LÓGICO — manter sincronizado com:
- contribuicaoElegivel() em HubAcademico/firestore.rules
- buscarElegibilidade() em BancoProvas/src/services/questoes.ts
- atendeFiltro() em BancoProvas/src/services/destino.ts
"""

import base64
import re

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.oauth2 import service_account

# Mesma tag de app.py (_IMG_TAG_PAT); repetida aqui para não importar o app.
_IMG_TAG_PAT = re.compile(r'\[img:([^\]]+)\]', re.IGNORECASE)

DIAS = {
    "seg": "Segunda-feira", "ter": "Terça-feira", "qua": "Quarta-feira",
    "qui": "Quinta-feira", "sex": "Sexta-feira", "sab": "Sábado",
}
TURNOS = {"matutino": "Matutino", "noturno": "Noturno"}
TURMAS = ("A", "B")


def criar_cliente(info):
    """Cria o cliente Firestore a partir do dict da conta de serviço."""
    cred = service_account.Credentials.from_service_account_info(dict(info))
    return firestore.Client(project=info["project_id"], credentials=cred)


def buscar_professor_por_email(db, email):
    """
    Casa o e-mail digitado contra professors. Retorna {uid, nome, email} ou None.
    Professores não aprovados na Ágora são tratados como inexistentes.
    """
    email = (email or "").strip()
    if not email:
        return None
    def _aprovado(docs):
        for d in docs:
            dados = d.to_dict() or {}
            if dados.get("status") == "approved":
                return {"uid": d.id, "nome": dados.get("name", ""), "email": dados.get("email", email)}
        return None

    for tentativa in dict.fromkeys([email, email.lower()]):
        achado = _aprovado(
            db.collection("professors")
            .where(filter=FieldFilter("email", "==", tentativa))
            .limit(5)
            .stream()
        )
        if achado:
            return achado
    # Firestore só compara exato; e-mails gravados com maiúsculas caem aqui.
    alvo = email.casefold()
    return _aprovado(
        d for d in db.collection("professors").stream()
        if str((d.to_dict() or {}).get("email", "")).strip().casefold() == alvo
    )


def elegivel(stats, uid):
    """Regra dos 10%: 10 * meu >= total (com total > 0)."""
    if not stats:
        return False
    total = stats.get("total", 0) or 0
    meu = (stats.get("porProfessor") or {}).get(uid, 0) or 0
    return total > 0 and 10 * meu >= total


def listar_disciplinas_do_professor(db, uid):
    """
    Disciplinas em que o professor tem ao menos uma questão ativa (sem isso ele
    não enxerga nada, nem pela regra dos 10%). Ordenadas por nome.
    Retorna [{id, nome, total, meu, elegivel}].
    """
    # Coleção pequena (1 doc por disciplina): filtra no cliente para não
    # depender de índice no campo porProfessor.<uid>.
    stats_por_id = {}
    for d in db.collection("disciplinaStats").stream():
        stats = d.to_dict() or {}
        if ((stats.get("porProfessor") or {}).get(uid, 0) or 0) > 0:
            stats_por_id[d.id] = stats
    if not stats_por_id:
        return []

    refs = [db.collection("disciplinas").document(i) for i in stats_por_id]
    nomes = {}
    for d in db.get_all(refs):
        if d.exists:
            nomes[d.id] = (d.to_dict() or {}).get("nome") or d.id

    disciplinas = []
    for disc_id, stats in stats_por_id.items():
        disciplinas.append({
            "id": disc_id,
            "nome": nomes.get(disc_id, disc_id),
            "total": stats.get("total", 0) or 0,
            "meu": stats["porProfessor"][uid],
            "elegivel": elegivel(stats, uid),
        })
    disciplinas.sort(key=lambda x: x["nome"].casefold())
    return disciplinas


def elegivel_para_disciplina(db, uid, disciplina_id):
    snap = db.collection("disciplinaStats").document(disciplina_id).get()
    return elegivel(snap.to_dict() if snap.exists else None, uid)


def atende_filtro(questao, dia=None, turno=None, turma=None):
    """
    A questão serve para a aula filtrada? dia: None = todos, 'sem' = só as sem
    dia definido. Turno/turma em branco na questão valem para qualquer um.
    """
    q_dia, q_turno, q_turma = questao.get("dia"), questao.get("turno"), questao.get("turma")
    if dia == "sem" and q_dia:
        return False
    if dia and dia != "sem" and q_dia != dia:
        return False
    if turno and q_turno and q_turno != turno:
        return False
    if turma and q_turma and q_turma != turma:
        return False
    return True


def _limpar_enunciado(texto):
    texto = texto or ""
    return _IMG_TAG_PAT.sub("", texto).strip()


def _converter_objetiva(enunciado, alternativas):
    """Mesmo formato de get_questoes_xlsx: (enunciado, correta, correta, d1..d4)."""
    alternativas = alternativas or []
    corretas = [a.get("texto", "").strip() for a in alternativas if a.get("correta")]
    distratores = [a.get("texto", "").strip() for a in alternativas if not a.get("correta")]
    if len(alternativas) != 5 or len(corretas) != 1 or not all(corretas + distratores):
        return None
    return (enunciado, corretas[0], corretas[0], *distratores)


def carregar_questoes_banco(db, uid, disciplina_id, dia=None, turno=None, turma=None):
    """
    Carrega as questões ativas que o professor pode ver na disciplina.

    Retorna dict com:
    - objetivas:     lista de tuplas no formato de get_questoes_xlsx
    - dissertativas: lista de enunciados (formato de get_questoes_dissertativas_xlsx)
    - imagens:       {enunciado: questaoId} das questões que têm imagem
    - elegivel:      True se viu todas as questões da disciplina (regra dos 10%)
    - ignoradas:     objetivas descartadas por alternativas inválidas
    - sem_texto:     questões descartadas por enunciado vazio (ex.: só a tag [img:]),
                     que o gerador não aceita — mesmo critério de get_questoes_xlsx
    """
    pode_ver_todas = elegivel_para_disciplina(db, uid, disciplina_id)
    consulta = (
        db.collection("questoes")
        .where(filter=FieldFilter("disciplinaId", "==", disciplina_id))
        .where(filter=FieldFilter("status", "==", "ativa"))
    )
    if not pode_ver_todas:
        consulta = consulta.where(filter=FieldFilter("autorUid", "==", uid))

    # Mais antigas primeiro (sem orderBy na consulta: exigiria índice composto)
    docs = [(d.id, d.to_dict() or {}) for d in consulta.stream()]
    docs.sort(key=lambda par: (par[1].get("createdAt") is None, par[1].get("createdAt") or 0))

    objetivas, dissertativas, imagens = [], [], {}
    ignoradas = sem_texto = 0
    for qid, q in docs:
        if not atende_filtro(q, dia, turno, turma):
            continue
        enunciado = _limpar_enunciado(q.get("enunciado"))
        if not enunciado:
            sem_texto += 1
            continue
        if q.get("tipo") == "objetiva":
            tupla = _converter_objetiva(enunciado, q.get("alternativas"))
            if tupla is None:
                ignoradas += 1
                continue
            objetivas.append(tupla)
        elif q.get("tipo") == "dissertativa":
            dissertativas.append(enunciado)
        else:
            continue
        if q.get("imagem"):
            imagens[enunciado] = qid

    return {
        "objetivas": objetivas,
        "dissertativas": dissertativas,
        "imagens": imagens,
        "elegivel": pode_ver_todas,
        "ignoradas": ignoradas,
        "sem_texto": sem_texto,
    }


def baixar_imagens(db, imagens):
    """
    Lê questaoImagens/{questaoId} e decodifica o base64.
    Recebe {enunciado: questaoId}; retorna ({enunciado: bytes}, [enunciados sem imagem]).
    """
    if not imagens:
        return {}, []
    por_id = {qid: enunc for enunc, qid in imagens.items()}
    refs = [db.collection("questaoImagens").document(qid) for qid in por_id]
    resultado = {}
    for d in db.get_all(refs):
        if not d.exists:
            continue
        dados = (d.to_dict() or {}).get("dados")
        if not dados:
            continue
        try:
            resultado[por_id[d.id]] = base64.b64decode(dados)
        except (ValueError, TypeError):
            continue
    faltando = [enunc for enunc in imagens if enunc not in resultado]
    return resultado, faltando
