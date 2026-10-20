"""M7 — kit de instrução 360º montado a partir do quadro de ônus e de rules/instrucao.yaml."""


def _objetivo(linha, lado):
    nosso = linha["onus"] == lado
    if linha["onus"] == "pericia":
        return "Prova técnica: quesitos e assistente técnico."
    if nosso:
        return "Ônus nosso: provar o fato com testemunha própria e travar admissões do preposto."
    return "Ônus da parte contrária: obter confissão do preposto e desconstituir a testemunha adversa."


def blocos_prova_oral(quadro, regras, lado="reclamante"):
    perguntas = regras["instrucao"].get("perguntas", {})
    blocos = []
    for linha in quadro:
        if linha["sem_regra"] or "oral" not in linha["meio_prova"]:
            continue
        modelo = perguntas.get(linha["pedido"]["tipo"], {})
        blocos.append({
            "pedido_id": linha["pedido"]["id"],
            "rotulo": linha["rotulo"],
            "onus": linha["onus"],
            "objetivo": _objetivo(linha, lado),
            "preposto": list(modelo.get("preposto", [])),
            "testemunha_propria": list(modelo.get("testemunha_propria", [])),
            "testemunha_adversa": list(modelo.get("testemunha_adversa", [])),
            "sem_modelo": not modelo,
        })
    return blocos


def requerimentos(quadro, lado="reclamante"):
    """Requerimentos de audiência derivados do ônus (exibição, distribuição dinâmica, ordem)."""
    contrario = "reclamada" if lado == "reclamante" else "reclamante"
    reqs = []
    for linha in quadro:
        if linha["sem_regra"]:
            continue
        pid, rotulo = linha["pedido"]["id"], linha["rotulo"]
        tese = linha.get("tese")
        if linha["onus"] == contrario and "documental" in linha["meio_prova"] and lado == "reclamante":
            doc = tese["documento_esperado"] if tese else "documentos do pedido"
            reqs.append(f"[{pid}] {rotulo}: requerer a exibição de {doc}, sob pena de se presumirem "
                        "verdadeiros os fatos (art. 400, CPC).")
        if linha["onus"] == contrario and "oral" in linha["meio_prova"]:
            reqs.append(f"[{pid}] {rotulo}: ônus da {contrario} — requerer que a {contrario} produza "
                        "primeiro a sua prova oral (inversão da ordem dos depoimentos).")
        if linha["onus"] == lado and linha.get("condicao") is None and "documental" in linha["meio_prova"] \
                and lado == "reclamante":
            reqs.append(f"[{pid}] {rotulo}: se a prova estiver com a empresa, requerer a distribuição "
                        "dinâmica do ônus antes da instrução (art. 818, §1º, CLT).")
    return reqs


def kit_instrucao(caso, quadro, regras):
    lado = caso.get("lado", "reclamante")
    conf = regras["instrucao"]
    limite = conf["limite_testemunhas"][caso["processo"]["rito"]]
    return {
        "limite_testemunhas": limite,
        "lembrete_preposto": conf["preposto"]["lembrete"].strip(),
        "blocos": blocos_prova_oral(quadro, regras, lado),
        "contradita": conf["contradita"],
        "protestos": conf["protestos"],
        "lembrete_protestos": conf["lembrete_protestos"],
        "requerimentos": requerimentos(quadro, lado),
    }
