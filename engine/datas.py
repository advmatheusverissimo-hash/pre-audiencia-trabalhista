"""Regras de data: prescrição (art. 7º, XXIX, CF; art. 11, CLT), recesso e art. 775-A, CLT.

Tudo aqui é conta, não interpretação. Casos limítrofes saem como alerta para o advogado.
"""

from datetime import date, timedelta


def somar_anos(d, anos):
    """Soma anos de calendário; 29/02 vira 28/02 em ano não bissexto."""
    try:
        return d.replace(year=d.year + anos)
    except ValueError:
        return d.replace(year=d.year + anos, day=28)


def marco_quinquenal(data_ajuizamento):
    """Créditos anteriores a esta data estão prescritos (Súmula 308, I, TST)."""
    return somar_anos(data_ajuizamento, -5)


def fim_contrato_projetado(saida, aviso_previo_dias=0):
    """Data de término com a projeção do aviso prévio indenizado (OJ 83, SDI-1, TST)."""
    return saida + timedelta(days=aviso_previo_dias)


def limite_bienal(saida, aviso_previo_dias=0):
    """Último dia para ajuizar: dois anos do término do contrato, aviso projetado."""
    return somar_anos(fim_contrato_projetado(saida, aviso_previo_dias), 2)


def no_recesso(d):
    """Recesso forense: 20/12 a 06/01, inclusive (art. 62, I, Lei 5.010/1966)."""
    return (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 6)


def audiencia_vedada(d):
    """Prazos suspensos e audiências vedadas de 20/12 a 20/01, inclusive (art. 775-A, caput e §2º, CLT)."""
    return (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 20)


def analisar_datas(caso, hoje=None):
    """Devolve marco quinquenal, situação bienal, alertas gerais e alertas por pedido."""
    hoje = hoje or date.today()
    proc, contrato = caso["processo"], caso["contrato"]
    ajuizamento, audiencia = proc["data_ajuizamento"], proc["data_audiencia"]
    marco = marco_quinquenal(ajuizamento)
    alertas = []

    bienal = None
    if contrato.get("saida"):
        limite = limite_bienal(contrato["saida"], contrato.get("aviso_previo_dias", 0))
        bienal = {"limite": limite, "prescrito": ajuizamento > limite}
        if bienal["prescrito"]:
            alertas.append(
                f"Prescrição bienal: ação ajuizada em {ajuizamento:%d/%m/%Y}, após o limite de "
                f"{limite:%d/%m/%Y} (término com aviso projetado). Conferir causas de interrupção "
                "(ex.: ação anterior arquivada — Súmula 268, TST)."
            )

    if audiencia_vedada(audiencia):
        periodo = "no recesso forense (20/12 a 06/01) e " if no_recesso(audiencia) else ""
        alertas.append(
            f"Audiência em {audiencia:%d/%m/%Y} cai {periodo}no período de 20/12 a 20/01, em que "
            "audiências são vedadas (art. 775-A, §2º, CLT). Conferir a designação na pauta da vara."
        )
    if audiencia < hoje:
        alertas.append(f"Data da audiência ({audiencia:%d/%m/%Y}) já passou — conferir a data informada.")

    por_pedido = {}
    for p in caso["pedidos"]:
        inicio = (p.get("periodo") or {}).get("inicio")
        fim = (p.get("periodo") or {}).get("fim")
        if inicio and fim and fim < marco:
            por_pedido[p["id"]] = f"Período inteiro anterior a {marco:%d/%m/%Y}: prescrito (quinquenal)."
        elif inicio and inicio < marco:
            por_pedido[p["id"]] = f"Parcelas anteriores a {marco:%d/%m/%Y} prescritas (quinquenal)."

    return {
        "marco_quinquenal": marco,
        "bienal": bienal,
        "dias_ate_audiencia": (audiencia - hoje).days,
        "alertas": alertas,
        "por_pedido": por_pedido,
    }
