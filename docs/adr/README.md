# Architecture Decision Records — gac-api

Decisiones que cuesta caro redescubrir: por qué algo está montado como está, qué
alternativas se descartaron y qué consecuencias acarrea.

No todo cambio merece un ADR. Sí lo merece cuando la decisión es difícil de
revertir, cuando afecta a la operación (despliegue, base de datos, permisos), o
cuando alguien razonable haría lo contrario si no supiera lo que aquí se cuenta.

## Formato

Un fichero por decisión, numerado: `NNNN-titulo-en-kebab-case.md`, con
**Contexto**, **Decisión**, **Consecuencias** y **Alternativas descartadas**.

Un ADR no se edita cuando la realidad cambia: se escribe uno nuevo que lo
sustituya y se marca el anterior como *Sustituido por NNNN*.

## Índice

| ADR | Título | Estado |
| --- | ------ | ------ |
| [0001](0001-migraciones-y-privilegios-de-base-de-datos.md) | Migraciones y privilegios de base de datos | Aceptado |
