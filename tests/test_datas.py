from datetime import date

import pytest

from engine.datas import (analisar_datas, audiencia_vedada, limite_bienal, marco_quinquenal,
                          no_recesso, somar_anos)
from engine.regras import validar_caso


@pytest.mark.parametrize("d, esperado", [
    (date(2026, 12, 19), False),
    (date(2026, 12, 20), True),   # primeiro dia do recesso
    (date(2026, 12, 31), True),   # virada de ano
    (date(2027, 1, 1), True),
    (date(2027, 1, 6), True),     # último dia do recesso
    (date(2027, 1, 7), False),
])
def test_recesso_forense(d, esperado):
    assert no_recesso(d) is esperado


@pytest.mark.parametrize("d, esperado", [
    (date(2026, 12, 19), False),
    (date(2026, 12, 20), True),
    (date(2027, 1, 7), True),     # fora do recesso, mas ainda vedado pelo art. 775-A
    (date(2027, 1, 20), True),
    (date(2027, 1, 21), False),
])
def test_audiencia_vedada_art_775a(d, esperado):
    assert audiencia_vedada(d) is esperado


def test_somar_anos_29_de_fevereiro():
    assert somar_anos(date(2024, 2, 29), 2) == date(2026, 2, 28)
    assert somar_anos(date(2028, 2, 29), -5) == date(2023, 2, 28)
    assert somar_anos(date(2024, 2, 29), 4) == date(2028, 2, 29)


def test_marco_quinquenal():
    assert marco_quinquenal(date(2026, 3, 10)) == date(2021, 3, 10)


def test_bienal_com_aviso_projetado_vira_mes_e_ano():
    # saída 15/12/2025 + 48 dias de aviso = 01/02/2026 → limite 01/02/2028
    assert limite_bienal(date(2025, 12, 15), 48) == date(2028, 2, 1)
    # saída 31/01 + 30 dias atravessa fevereiro
    assert limite_bienal(date(2026, 1, 31), 30) == date(2028, 3, 2)


def test_bienal_no_limite_nao_prescreve(caso_bruto):
    caso_bruto["contrato"].update(saida="2024-01-10", aviso_previo_dias=0)
    caso_bruto["processo"]["data_ajuizamento"] = "2026-01-10"
    r = analisar_datas(validar_caso(caso_bruto), hoje=date(2026, 10, 20))
    assert r["bienal"]["prescrito"] is False


def test_bienal_um_dia_depois_prescreve(caso_bruto):
    caso_bruto["contrato"].update(saida="2024-01-10", aviso_previo_dias=0)
    caso_bruto["processo"]["data_ajuizamento"] = "2026-01-11"
    r = analisar_datas(validar_caso(caso_bruto), hoje=date(2026, 10, 20))
    assert r["bienal"]["prescrito"] is True
    assert any("bienal" in a for a in r["alertas"])


def test_quinquenal_por_pedido(caso_bruto):
    r = analisar_datas(validar_caso(caso_bruto), hoje=date(2026, 10, 20))
    assert r["marco_quinquenal"] == date(2021, 3, 10)
    assert "P1" in r["por_pedido"] and "10/03/2021" in r["por_pedido"]["P1"]
    assert "P2" not in r["por_pedido"]


def test_pedido_inteiro_prescrito(caso_bruto):
    caso_bruto["pedidos"][0]["periodo"] = {"inicio": "2019-02-01", "fim": "2020-12-31"}
    r = analisar_datas(validar_caso(caso_bruto), hoje=date(2026, 10, 20))
    assert "Período inteiro" in r["por_pedido"]["P1"]


def test_alerta_audiencia_no_recesso(caso_bruto):
    caso_bruto["processo"]["data_audiencia"] = "2026-12-22"
    r = analisar_datas(validar_caso(caso_bruto), hoje=date(2026, 10, 20))
    assert any("recesso" in a and "775-A" in a for a in r["alertas"])


def test_alerta_audiencia_vedada_fora_do_recesso(caso_bruto):
    caso_bruto["processo"]["data_audiencia"] = "2027-01-15"
    r = analisar_datas(validar_caso(caso_bruto), hoje=date(2026, 10, 20))
    alerta = next(a for a in r["alertas"] if "775-A" in a)
    assert "recesso forense" not in alerta


def test_audiencia_ja_passou(caso_bruto):
    r = analisar_datas(validar_caso(caso_bruto), hoje=date(2026, 11, 19))
    assert any("já passou" in a for a in r["alertas"])
    assert r["dias_ate_audiencia"] == -1
