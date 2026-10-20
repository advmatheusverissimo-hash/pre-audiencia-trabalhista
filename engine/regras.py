"""Carga das regras (rules/*.yaml) e validação do caso de entrada."""

import json
from datetime import date
from pathlib import Path

import jsonschema
import yaml

RAIZ = Path(__file__).resolve().parent.parent
DIR_REGRAS = RAIZ / "rules"
SCHEMA_CASO = RAIZ / "schemas" / "caso.schema.json"

ONUS_VALIDOS = {"reclamante", "reclamada", "pericia"}
MEIOS_VALIDOS = {"documental", "oral", "pericial"}


class RegraInvalida(ValueError):
    """Arquivo de regras com estrutura inválida."""


class CasoInvalido(ValueError):
    """Caso de entrada fora do schema."""


def _ler_yaml(nome, dir_regras=DIR_REGRAS):
    caminho = Path(dir_regras) / nome
    with open(caminho, encoding="utf-8") as f:
        dados = yaml.safe_load(f)
    if not isinstance(dados, dict):
        raise RegraInvalida(f"{nome}: conteúdo não é um mapa")
    return dados


def _validar_regra(nome_pedido, regra, onde):
    for campo in ("onus", "fundamento", "meio_prova", "efeito"):
        if campo not in regra:
            raise RegraInvalida(f"onus.yaml: {nome_pedido} ({onde}) sem o campo '{campo}'")
    if regra["onus"] not in ONUS_VALIDOS:
        raise RegraInvalida(f"onus.yaml: {nome_pedido} ({onde}) com ônus '{regra['onus']}' inválido")
    invalidos = set(regra["meio_prova"]) - MEIOS_VALIDOS
    if invalidos:
        raise RegraInvalida(f"onus.yaml: {nome_pedido} ({onde}) com meio de prova inválido: {sorted(invalidos)}")


def carregar_regras(dir_regras=DIR_REGRAS):
    onus = _ler_yaml("onus.yaml", dir_regras)
    pedidos = onus.get("pedidos")
    if not isinstance(pedidos, dict) or not pedidos:
        raise RegraInvalida("onus.yaml: seção 'pedidos' ausente ou vazia")
    for nome, conf in pedidos.items():
        if "padrao" not in conf:
            raise RegraInvalida(f"onus.yaml: {nome} sem 'padrao'")
        _validar_regra(nome, conf["padrao"], "padrao")
        for i, variante in enumerate(conf.get("variantes", [])):
            if not isinstance(variante.get("quando"), dict) or not variante["quando"]:
                raise RegraInvalida(f"onus.yaml: {nome} variante {i} sem 'quando'")
            _validar_regra(nome, variante, f"variante {i}")
    return {
        "onus": onus,
        "teses": _ler_yaml("teses-defesa.yaml", dir_regras).get("teses", {}),
        "temas": _ler_yaml("temas-sensiveis.yaml", dir_regras).get("temas", []),
        "instrucao": _ler_yaml("instrucao.yaml", dir_regras),
    }


def _data(valor, campo):
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        raise CasoInvalido(f"{campo}: data inválida ({valor!r}); use AAAA-MM-DD") from None


def validar_caso(caso):
    """Valida contra o schema e converte as datas. Devolve uma cópia normalizada."""
    with open(SCHEMA_CASO, encoding="utf-8") as f:
        schema = json.load(f)
    try:
        jsonschema.validate(caso, schema)
    except jsonschema.ValidationError as e:
        caminho = "/".join(str(p) for p in e.absolute_path) or "(raiz)"
        raise CasoInvalido(f"{caminho}: {e.message}") from None

    caso = json.loads(json.dumps(caso))
    proc, contrato = caso["processo"], caso["contrato"]
    proc["data_ajuizamento"] = _data(proc["data_ajuizamento"], "processo.data_ajuizamento")
    proc["data_audiencia"] = _data(proc["data_audiencia"], "processo.data_audiencia")
    contrato["admissao"] = _data(contrato["admissao"], "contrato.admissao")
    if contrato.get("saida"):
        contrato["saida"] = _data(contrato["saida"], "contrato.saida")
        if contrato["saida"] < contrato["admissao"]:
            raise CasoInvalido("contrato.saida: anterior à admissão")
    for p in caso["pedidos"]:
        per = p.get("periodo") or {}
        for k in ("inicio", "fim"):
            if per.get(k):
                per[k] = _data(per[k], f"pedidos[{p['id']}].periodo.{k}")
        if per.get("inicio") and per.get("fim") and per["fim"] < per["inicio"]:
            raise CasoInvalido(f"pedidos[{p['id']}].periodo: fim anterior ao início")
    ids = [p["id"] for p in caso["pedidos"]]
    if len(ids) != len(set(ids)):
        raise CasoInvalido("pedidos: ids repetidos")
    caso.setdefault("lado", "reclamante")
    return caso
