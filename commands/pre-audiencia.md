---
description: Parecer pré-audiência completo a partir do PDF do processo (ônus por pedido, kit de instrução, Word)
argument-hint: <caminho do PDF integral do PJe>
---

Prepare o parecer pré-audiência do processo em `$ARGUMENTS`.

Princípio: o modelo lê, classifica e argumenta; o código (`engine/`) aplica regra e calcula;
o advogado decide. Toda saída aponta o ID/folha do PJe de onde veio.

1. **M1 — Ingestão.** Extraia o texto do PDF peça por peça (inicial, documentos, contestação,
   réplica, atas), guardando o ID/folha de cada trecho. Se o PDF for imagem, faça OCR e avise
   que a qualidade deve ser conferida. Salve em `casos/<numero>/pecas/` (pasta fora do git).
2. **M2 — Extração.** Use o subagente `extrator` para montar `casos/<numero>/caso.json`
   conforme `schemas/caso.schema.json`. Pedido sem tipo conhecido em `rules/onus.yaml` mantém
   o tipo descritivo — não force encaixe.
3. **Defesa.** Se já houver contestação, registre a tese real de cada pedido
   (`defesa.origem = "contestacao"`). Se não houver, use o subagente `preditor-defesa`
   (Camada A, `rules/teses-defesa.yaml`) e marque `defesa.origem = "prevista"`.
4. **M4/M7/M8 — Motor.** Rode
   `python -m engine.cli casos/<numero>/caso.json --saida casos/<numero>/saida`.
   Se o comando falhar, mostre o erro ao usuário e corrija o `caso.json`; não contorne a validação.
5. **Instrução específica.** Use o subagente `instrucao` para propor perguntas adicionais
   ligadas aos fatos do caso (com o ID do documento para confronto) e apresente-as ao advogado
   separadas das perguntas-base.
6. **Revisão.** Use o subagente `revisor` sobre o resultado e relate as divergências.
7. Entregue ao usuário os caminhos dos dois .docx (parecer e roteiro de bolso), a lista de
   alertas e as pendências. Lembre que os documentos saem como MINUTA
   (`revisada_por_advogado: NÃO`).

Nunca cite jurisprudência, ementa ou número de processo que não tenha sido conferido em fonte
oficial nesta sessão.
