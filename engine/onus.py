"""M4 — motor de ônus: aplica rules/onus.yaml a cada pedido do caso."""

LIMITE_EMPREGADOS_PONTO = 20  # art. 74, §2º, CLT


def contexto_pedido(caso, pedido):
    """Monta as chaves que as condições `quando` do onus.yaml podem testar."""
    n = (caso["processo"].get("reclamada") or {}).get("numero_empregados")
    defesa = pedido.get("defesa") or {}
    return {
        "controles_ponto": (caso.get("provas") or {}).get("controles_ponto", "nao_informado"),
        "reclamada_mais_de_20": None if n is None else n > LIMITE_EMPREGADOS_PONTO,
        "tese_defesa": defesa.get("tese", "nao_informada"),
        "ruptura_alegada_reclamada": caso["contrato"].get("ruptura_alegada_reclamada", "nao_informada"),
    }


def _bate(quando, ctx):
    for chave, esperado in quando.items():
        valor = ctx.get(chave)
        if isinstance(esperado, list):
            if valor not in esperado:
                return False
        elif valor != esperado:
            return False
    return True


def aplicar_regra(conf_pedido, ctx):
    """Primeira variante que bate inteira vence; senão, o padrão."""
    for variante in conf_pedido.get("variantes", []):
        if _bate(variante["quando"], ctx):
            return variante, variante["quando"]
    return conf_pedido["padrao"], None


def quadro_onus(caso, regras):
    pedidos_conf = regras["onus"]["pedidos"]
    teses = regras["teses"]
    quadro = []
    for pedido in caso["pedidos"]:
        conf = pedidos_conf.get(pedido["tipo"])
        defesa = pedido.get("defesa") or {}
        tese = teses.get(defesa.get("tese")) if defesa.get("tese") else None
        linha = {
            "pedido": pedido,
            "defesa": defesa,
            "tese": tese,
            "tese_desconhecida": bool(defesa.get("tese")) and tese is None,
        }
        if conf is None:
            linha.update(sem_regra=True, rotulo=pedido["tipo"], onus=None, fundamento=None,
                         meio_prova=[], efeito="Sem regra em rules/onus.yaml — advogado define.",
                         condicao=None)
        else:
            ctx = contexto_pedido(caso, pedido)
            regra, condicao = aplicar_regra(conf, ctx)
            linha.update(sem_regra=False, rotulo=conf.get("rotulo", pedido["tipo"]),
                         onus=regra["onus"], fundamento=regra["fundamento"],
                         meio_prova=list(regra["meio_prova"]), efeito=regra["efeito"],
                         condicao=condicao)
            if pedido["tipo"] == "horas_extras" and ctx["reclamada_mais_de_20"] is None \
                    and ctx["controles_ponto"] == "ausentes":
                linha["pendencia"] = ("Informar o número de empregados da reclamada: a presunção da "
                                      "Súmula 338, I, TST só vale para mais de 20 (art. 74, §2º, CLT).")
        quadro.append(linha)
    return quadro


def temas_sensiveis(caso, regras):
    """Temas suspensos/em mudança que tocam o caso (rules/temas-sensiveis.yaml)."""
    tipos = {p["tipo"] for p in caso["pedidos"]}
    teses = {(p.get("defesa") or {}).get("tese") for p in caso["pedidos"]} - {None}
    achados = []
    for tema in regras["temas"]:
        alvo = set(tema.get("pedidos", []))
        if "*" in alvo or alvo & tipos or set(tema.get("teses_defesa", [])) & teses:
            achados.append(tema)
    return achados
