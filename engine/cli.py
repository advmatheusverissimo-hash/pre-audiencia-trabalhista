"""Linha de comando: caso.json (saída do agente extrator) → parecer .docx + roteiro de bolso .docx.

Uso:
    python -m engine.cli caminho/caso.json --saida pasta/
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from engine.datas import analisar_datas
from engine.instrucao import kit_instrucao
from engine.onus import quadro_onus, temas_sensiveis
from engine.parecer_docx import gerar_parecer, gerar_roteiro_bolso
from engine.regras import CasoInvalido, RegraInvalida, carregar_regras, validar_caso


def analisar(caso_bruto, regras=None, hoje=None):
    regras = regras or carregar_regras()
    caso = validar_caso(caso_bruto)
    quadro = quadro_onus(caso, regras)
    return {
        "caso": caso,
        "datas": analisar_datas(caso, hoje=hoje),
        "quadro": quadro,
        "temas": temas_sensiveis(caso, regras),
        "kit": kit_instrucao(caso, quadro, regras),
        "regra_geral": regras["onus"]["regra_geral"],
        "versao_regras": regras["onus"].get("versao", "—"),
        "revisado_por": regras["onus"].get("revisado_por", "—"),
    }


def _nome_base(numero):
    return "".join(c if c.isalnum() else "-" for c in numero).strip("-")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pré-audiência trabalhista: ônus + kit de instrução em .docx")
    ap.add_argument("caso", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("saida"))
    ap.add_argument("--hoje", type=date.fromisoformat, default=None, help="AAAA-MM-DD (para testes)")
    args = ap.parse_args(argv)

    try:
        with open(args.caso, encoding="utf-8") as f:
            caso = json.load(f)
        resultado = analisar(caso, hoje=args.hoje)
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {args.caso}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"Erro: JSON inválido em {args.caso} (linha {e.lineno})", file=sys.stderr)
        return 2
    except (CasoInvalido, RegraInvalida) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 2

    args.saida.mkdir(parents=True, exist_ok=True)
    base = _nome_base(resultado["caso"]["processo"]["numero"])
    parecer = gerar_parecer(resultado, args.saida / f"parecer-pre-audiencia-{base}.docx")
    roteiro = gerar_roteiro_bolso(resultado, args.saida / f"roteiro-bolso-{base}.docx")
    print(parecer)
    print(roteiro)
    sem_regra = [l["pedido"]["id"] for l in resultado["quadro"] if l["sem_regra"]]
    if sem_regra:
        print(f"Atenção: pedidos sem regra de ônus: {', '.join(sem_regra)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
