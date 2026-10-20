---
description: Só o roteiro de audiência (perguntas, contradita, protestos) a partir de um caso.json já extraído
argument-hint: <caminho do caso.json>
---

Gere o roteiro de audiência para o caso em `$ARGUMENTS`.

1. Rode `python -m engine.cli $ARGUMENTS --saida <pasta do caso>/saida`.
2. Leia o quadro de ônus produzido e, com o subagente `instrucao`, proponha para cada ponto
   controvertido com prova oral:
   - perguntas fechadas ao preposto para obter confissão;
   - perguntas abertas, em funil, à testemunha própria;
   - perguntas fechadas, um fato por vez, à testemunha da reclamada, com o ID do documento
     para confronto.
3. Respeite o limite de testemunhas do rito (3 no ordinário, 2 no sumaríssimo).
4. Apresente as perguntas propostas separadas das perguntas-base de `rules/instrucao.yaml`,
   para o advogado aprovar.
