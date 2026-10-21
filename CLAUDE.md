# Pré-audiência trabalhista — instruções para o Claude Code

- O usuário é advogado (SP) e dono do produto. Toda comunicação e todo relatório são em
  português do Brasil. Relatórios sempre em **.docx**, nunca em Markdown.
- Princípio: **o modelo lê, classifica e argumenta; o código calcula e aplica regra; o advogado
  decide.** Toda saída aponta o ID/folha do PJe de onde veio.
- Regra de ônus, tese de defesa e pergunta-base só existem em `rules/*.yaml`, mantidos pelo
  advogado. Nunca inventar regra no código nem no prompt; pedido sem regra sai como
  "sem regra — advogado define".
- Parecer sai sempre como MINUTA (`revisada_por_advogado: NÃO`). Nada vai a cliente sem revisão.
- Jurisprudência, ementa ou número de processo só entram no parecer depois de conferidos em
  fonte oficial.
- Código segue a skill `codigo-seguro`: segredos só por variável de ambiente; testes cobrem
  caminho feliz, caminho de erro e bordas de data (recesso de 20/12 a 06/01, vedação de
  audiências até 20/01 — art. 775-A, CLT —, 29/02, virada de mês/ano).
- LGPD: processos de clientes ficam em `casos/` (fora do git). Testes usam só dados fictícios.

## Comandos

- `pip install -r requirements.txt`
- `python -m pytest -q`
- `python -m engine.cli casos/<numero>/caso.json --saida casos/<numero>/saida`

## Roteiro (pesquisa de 20/10/2026)

1. **Fase 1 (este repositório):** M1 ingestão, M2 extração, M4 ônus por regras, M7 kit de
   instrução, M8 Word.
2. Fase 2: M5 matriz de risco (log-odds com priors do escritório) e M6 acordo (piso, alvo,
   abertura), calibrados com 30–50 processos encerrados.
3. Fase 3: preditor de defesa Camadas B e C (provedor por CNPJ) e DataJud.
4. Fase 4: espelho da reclamada, M9 pós-audiência, painel de carteira.

Pedido do advogado em 21/10/2026, a implementar depois (um módulo por momento processual):
- Antes e depois da instrução (pós-audiência, razões finais).
- Sentença: espaço para a sentença, custas e depósito recursal a recolher.
- Fase recursal: recurso ordinário, recurso de revista, agravo de petição.
- Execução: liquidação, cálculos, penhora, embargos.
