"""Guarda as regras do arquivo de doutrina: só metadados, trecho só depois de conferido."""

from pathlib import Path

import yaml

RULES = Path(__file__).resolve().parent.parent / "rules"


def _carregar(nome):
    return yaml.safe_load((RULES / nome).read_text(encoding="utf-8"))


def test_obras_ligadas_a_pedidos_existentes():
    pedidos = _carregar("onus.yaml")["pedidos"]
    for obra in _carregar("doutrina.yaml")["obras"]:
        assert set(obra["pedidos"]) <= set(pedidos), obra["id"]


def test_trecho_so_com_conferencia():
    for obra in _carregar("doutrina.yaml")["obras"]:
        if obra["trecho"]:
            assert obra["situacao"] == "conferido", obra["id"]
            assert obra["pagina"] and obra["conferido_em"], obra["id"]


def test_ids_unicos_e_links_https():
    obras = _carregar("doutrina.yaml")["obras"]
    assert len({o["id"] for o in obras}) == len(obras)
    assert all(o["link"].startswith("https://") for o in obras)
    assert all(o["situacao"] in {"a_conferir", "conferido"} for o in obras)
