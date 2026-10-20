# Pré-audiência trabalhista 360º

Plugin do Claude Code que prepara a audiência trabalhista do lado do reclamante:

- lê o processo e extrai os pedidos com a fonte (ID/folha do PJe);
- prevê ou registra a defesa da reclamada pedido a pedido;
- monta o **quadro de ônus da prova** por pedido a partir de regras versionadas;
- gera o **kit de instrução**: perguntas ao preposto e às testemunhas, contradita, protestos e
  requerimentos;
- confere prescrição bienal e quinquenal e a data da audiência (recesso e art. 775-A, CLT);
- entrega **parecer pré-audiência** e **roteiro de bolso** em Word (.docx).

Esta é a Fase 1 do roteiro da pesquisa "Análise pré-audiência trabalhista com IA" (20/10/2026).
Matriz de risco e valor de acordo entram na Fase 2.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `commands/` | `/pre-audiencia`, `/roteiro-audiencia` |
| `agents/` | `extrator`, `preditor-defesa`, `instrucao`, `revisor` |
| `rules/` | `onus.yaml`, `teses-defesa.yaml`, `instrucao.yaml`, `temas-sensiveis.yaml` — mantidos pelo advogado |
| `schemas/` | `caso.schema.json` — contrato entre o extrator e o motor |
| `engine/` | Python determinístico: regras, datas, ônus, instrução, Word, CLI |
| `tests/` | testes com caso fictício |

## Uso

```bash
pip install -r requirements.txt
python -m pytest -q
python -m engine.cli tests/fixtures/caso_ficticio.json --saida saida/
```

No Claude Code: `/pre-audiencia caminho/do/processo.pdf`.

## Como manter as regras

Edite `rules/onus.yaml`: cada pedido tem um `padrao` e `variantes` com condições `quando`. A
primeira variante que bate vence. Depois de editar, rode `python -m pytest -q` — o teste
`test_regras_do_repositorio_sao_coerentes` confere se teses e perguntas apontam para pedidos
existentes. Atualize `versao` e `revisado_por` no topo do arquivo.
