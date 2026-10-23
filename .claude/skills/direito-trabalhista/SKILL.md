---
name: direito-trabalhista
description: Como trabalhar com direito do trabalho brasileiro neste produto (Advogado em Ação / pré-audiência). Use ao criar ou revisar regra de ônus, tese de defesa, cálculo de verba, prazo, jurisprudência ou qualquer texto que vá a cliente.
---

# Direito trabalhista — regras de trabalho

Princípio do produto: **o modelo lê, classifica e argumenta; o código calcula e aplica regra;
o advogado decide.** Toda saída aponta o ID/folha do PJe de onde veio.

## Onde cada coisa mora

| O quê | Onde | Quem mantém |
|---|---|---|
| Ônus da prova por pedido | `rules/onus.yaml` | advogado |
| Teses de defesa e "se vier" | `rules/teses-defesa.yaml`, `rules/contestacao.yaml` | advogado |
| Classificação do pedido | `rules/classificacao.yaml` | advogado |
| Perguntas de instrução | `rules/instrucao.yaml` | advogado |
| Risco (pesos) e acordo | `rules/risco.yaml` | advogado, a calibrar com processos encerrados |
| Correção, juros, FGTS, custas | `rules/correcao.yaml` | advogado |
| Verbas rescisórias | `rules/rescisao.yaml` | advogado |
| Defesa da empresa, eSocial, CPC 25 | `rules/defesa-empresa.yaml` | advogado |
| Quesitos de perícia | `rules/quesitos.yaml` | advogado |
| Jurisprudência e doutrina | `rules/jurisprudencia.yaml`, `rules/doutrina.yaml` | advogado |

Nunca inventar regra no código nem no prompt. Pedido sem regra sai como
"sem regra — advogado define". Regra nova entra no YAML com `base` legal e
`situacao: a_conferir` até o advogado revisar. O app (`audiencia-pronta-guias`) usa cópia em
JSON (`src/lib/motor/regras/*.json`): regerar a partir do YAML, nunca editar o JSON.

## Fontes e verificação

- Lei: Planalto (CLT, CF, Lei 8.036/90, Lei 12.506/2011, Lei 14.905/2024, CPC).
- Jurisprudência: só entra no parecer depois de conferida em fonte oficial (TST, STF, TRT).
  Até lá fica em `rules/jurisprudencia.yaml` com `conferida: false` e o parecer avisa.
- Índices: Banco Central (SGS 10764 IPCA-E, 433 IPCA, 4390 Selic, 7811 TR).
- Andamento público: API do DataJud (CNJ), só metadados; chave em variável de ambiente.
- Não raspar Jusbrasil, não contornar bot-detection, captcha ou WAF; não descompilar o PJe-Calc
  (só replicação funcional, e toda conta é estimativa).

## Pontos em aberto a conferir antes de usar (outubro/2026)

- Juros e correção: ADC 58/59 (IPCA-E pré-judicial; Selic do ajuizamento até 29/08/2024) e, a partir
  de 30/08/2024, IPCA + (Selic − IPCA), conforme SDI-1 (E-ED-RR-713-03.2010.5.04.0029). Há decisões
  que ainda aplicam só a ADC 58: conferir o que a sentença do caso determinou.
- Tema 35 do TST (limitação da condenação aos valores da inicial) e ADI 6002 no STF: sem tese
  definitiva; pedir a limitação de forma subsidiária na defesa.
- Súmula 439 do TST (dano moral: juros do ajuizamento, correção da decisão) diante da ADC 58.
- Pesos de `risco.yaml` são provisórios até calibração com 30–50 processos encerrados.

## Datas (sempre testar)

- Recesso 20/12 a 06/01; audiências vedadas até 20/01 (art. 775-A, CLT).
- Prescrição bienal com projeção do aviso (OJ 83, SDI-1) e quinquenal (Súmula 308, I).
- Regra dos 15 dias para avos de férias e 13º; 29/02; virada de mês e de ano; admissão no dia 31.
- Aviso proporcional: 30 + 3 por ano completo, teto de 90 (Lei 12.506/2011).

## Saída

- Português do Brasil; relatórios em .docx; sempre MINUTA (`revisada_por_advogado: NÃO`).
- Captação respeita o Provimento 205/2021 da OAB.
- LGPD: dados reais de clientes fora do git; testes só com dados fictícios; conferir cada diff.
