"""Guarda o arquivo da defesa da reclamada: estrutura com base legal e eSocial ligado a pedidos existentes."""

from pathlib import Path

import yaml

RULES = Path(__file__).resolve().parent.parent / "rules"


def _carregar(nome):
    return yaml.safe_load((RULES / nome).read_text(encoding="utf-8"))


def test_todo_item_da_estrutura_tem_base_legal():
    for secao in _carregar("defesa-empresa.yaml")["estrutura_contestacao"]:
        for item in secao["itens"]:
            assert item["titulo"] and item["quando"] and item["base"], item


def test_esocial_por_pedido_usa_eventos_e_pedidos_conhecidos():
    d = _carregar("defesa-empresa.yaml")
    pedidos = _carregar("onus.yaml")["pedidos"]
    for tipo, eventos in d["esocial"]["por_pedido"].items():
        assert tipo in pedidos, tipo
        assert set(eventos) <= set(d["esocial"]["eventos"]), tipo


def test_classificacao_cobre_as_tres_faixas_da_matriz():
    assert set(_carregar("defesa-empresa.yaml")["classificacao_cpc25"]) == {"alta", "media", "baixa"}
