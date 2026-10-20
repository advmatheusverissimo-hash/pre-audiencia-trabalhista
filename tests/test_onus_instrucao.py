from datetime import date

import pytest
import yaml

from engine.cli import analisar
from engine.instrucao import kit_instrucao
from engine.onus import quadro_onus, temas_sensiveis
from engine.regras import CasoInvalido, RegraInvalida, carregar_regras, validar_caso


def _linha(quadro, pid):
    return next(l for l in quadro if l["pedido"]["id"] == pid)


def test_quadro_caminho_feliz(caso_bruto, regras):
    quadro = quadro_onus(validar_caso(caso_bruto), regras)
    p1 = _linha(quadro, "P1")
    assert p1["onus"] == "reclamada" and "338, III" in p1["fundamento"]   # ponto britânico
    p2 = _linha(quadro, "P2")
    assert p2["onus"] == "reclamada" and "212" in p2["fundamento"]        # pedido de demissão
    assert _linha(quadro, "P3")["onus"] == "reclamada"                    # FGTS, Súmula 461
    assert _linha(quadro, "P4")["onus"] == "pericia"
    assert _linha(quadro, "P5")["onus"] == "reclamante"
    assert _linha(quadro, "P1")["tese"]["rotulo"].startswith("Cartões")


def test_sumula_338_exige_mais_de_20_empregados(caso_bruto, regras):
    caso_bruto["provas"]["controles_ponto"] = "ausentes"
    caso_bruto["processo"]["reclamada"]["numero_empregados"] = 20
    caso_bruto["pedidos"][0].pop("defesa")
    p1 = _linha(quadro_onus(validar_caso(caso_bruto), regras), "P1")
    assert p1["onus"] == "reclamante" and p1["condicao"] is None

    caso_bruto["processo"]["reclamada"]["numero_empregados"] = 21
    p1 = _linha(quadro_onus(validar_caso(caso_bruto), regras), "P1")
    assert p1["onus"] == "reclamada" and "338, I" in p1["fundamento"]


def test_numero_empregados_desconhecido_gera_pendencia(caso_bruto, regras):
    caso_bruto["provas"]["controles_ponto"] = "ausentes"
    caso_bruto["processo"]["reclamada"]["numero_empregados"] = None
    caso_bruto["pedidos"][0].pop("defesa")
    p1 = _linha(quadro_onus(validar_caso(caso_bruto), regras), "P1")
    assert "pendencia" in p1


def test_cargo_de_confianca_inverte_onus(caso_bruto, regras):
    caso_bruto["provas"]["controles_ponto"] = "variaveis"
    caso_bruto["pedidos"][0]["defesa"]["tese"] = "cargo_confianca"
    p1 = _linha(quadro_onus(validar_caso(caso_bruto), regras), "P1")
    assert p1["onus"] == "reclamada" and "62" in p1["fundamento"]


def test_pedido_sem_regra_nao_inventa(caso_bruto, regras):
    caso_bruto["pedidos"].append({"id": "P9", "tipo": "pedido_inexistente", "descricao": "x"})
    p9 = _linha(quadro_onus(validar_caso(caso_bruto), regras), "P9")
    assert p9["sem_regra"] and p9["onus"] is None and "advogado define" in p9["efeito"]


def test_tese_fora_do_catalogo(caso_bruto, regras):
    caso_bruto["pedidos"][2]["defesa"] = {"origem": "contestacao", "tese": "tese_nova"}
    p3 = _linha(quadro_onus(validar_caso(caso_bruto), regras), "P3")
    assert p3["tese_desconhecida"]


def test_temas_sensiveis_pejotizacao(caso_bruto, regras):
    caso_bruto["pedidos"].append({"id": "P6", "tipo": "vinculo_emprego", "descricao": "Vínculo",
                                  "defesa": {"origem": "contestacao", "tese": "pejotizacao"}})
    caso = validar_caso(caso_bruto)
    ids = {t["id"] for t in temas_sensiveis(caso, regras)}
    assert {"pejotizacao_stf", "correcao_juros", "nr1_psicossocial"} <= ids
    assert _linha(quadro_onus(caso, regras), "P6")["onus"] == "reclamada"


def test_kit_limite_testemunhas_por_rito(caso_bruto, regras):
    caso = validar_caso(caso_bruto)
    kit = kit_instrucao(caso, quadro_onus(caso, regras), regras)
    assert kit["limite_testemunhas"]["quantidade"] == 3
    caso_bruto["processo"]["rito"] = "sumarissimo"
    caso = validar_caso(caso_bruto)
    kit = kit_instrucao(caso, quadro_onus(caso, regras), regras)
    assert kit["limite_testemunhas"]["quantidade"] == 2


def test_kit_blocos_e_requerimentos(caso_bruto, regras):
    caso = validar_caso(caso_bruto)
    kit = kit_instrucao(caso, quadro_onus(caso, regras), regras)
    ids = {b["pedido_id"] for b in kit["blocos"]}
    assert ids == {"P1", "P2", "P5"}              # P3 documental, P4 pericial: sem prova oral
    reqs = " ".join(kit["requerimentos"])
    assert "art. 400, CPC" in reqs and "inversão da ordem" in reqs


@pytest.mark.parametrize("mexer, trecho", [
    (lambda c: c["processo"].update(rito="sumario"), "rito"),
    (lambda c: c["processo"].update(data_audiencia="18/11/2026"), "data inválida"),
    (lambda c: c["contrato"].update(saida="2018-01-01"), "anterior à admissão"),
    (lambda c: c.update(pedidos=[]), "pedidos"),
    (lambda c: c["pedidos"].append(dict(c["pedidos"][0])), "ids repetidos"),
    (lambda c: c["pedidos"][0].update(periodo={"inicio": "2025-01-31", "fim": "2024-12-31"}), "fim anterior"),
])
def test_caso_invalido(caso_bruto, mexer, trecho):
    mexer(caso_bruto)
    with pytest.raises(CasoInvalido, match=trecho):
        validar_caso(caso_bruto)


def test_regra_invalida(tmp_path):
    from engine.regras import DIR_REGRAS
    for nome in ("teses-defesa.yaml", "temas-sensiveis.yaml", "instrucao.yaml"):
        (tmp_path / nome).write_text((DIR_REGRAS / nome).read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "onus.yaml").write_text(yaml.safe_dump({"pedidos": {"x": {"padrao": {
        "onus": "juiz", "fundamento": "f", "meio_prova": ["oral"], "efeito": "e"}}}}), encoding="utf-8")
    with pytest.raises(RegraInvalida, match="ônus 'juiz'"):
        carregar_regras(tmp_path)


def test_regras_do_repositorio_sao_coerentes(regras):
    """Toda tese citada em variante e todo pedido com perguntas existem nos catálogos."""
    teses = set(regras["teses"])
    for nome, conf in regras["onus"]["pedidos"].items():
        for v in conf.get("variantes", []):
            t = v["quando"].get("tese_defesa")
            for tese in (t if isinstance(t, list) else [t] if t else []):
                assert tese in teses, f"{nome}: tese {tese} fora de teses-defesa.yaml"
    for tipo in regras["instrucao"]["perguntas"]:
        assert tipo in regras["onus"]["pedidos"]
    for chave, tese in regras["teses"].items():
        for tipo in tese["pedidos"]:
            assert tipo in regras["onus"]["pedidos"], f"{chave}: pedido {tipo} sem regra de ônus"


def test_analisar_integra_tudo(caso_bruto):
    r = analisar(caso_bruto, hoje=date(2026, 10, 20))
    assert r["datas"]["dias_ate_audiencia"] == 29
    assert len(r["quadro"]) == 5
