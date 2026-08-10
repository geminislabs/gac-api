# 0001 — Migraciones y privilegios de base de datos

**Estado:** Aceptado · 2026-08-10

## Contexto

Hasta agosto de 2026 el despliegue de gac-api **nunca aplicó migraciones**.
`alembic upgrade head` existía solo en el `Makefile` y en el `README`, como paso
manual de la instalación local. Se comprobó sobre todo el historial del repo:

```bash
git log --all -S "alembic upgrade" -- .github/   # sin resultados
```

La consecuencia se descubrió al añadir una tabla nueva:

- La migración `ee38a850524a` (2026-06-09) declaraba **siete** tablas.
- La base de producción tenía **tres**: `roles`, `users`, `user_roles`.
- Faltaban `orders`, `order_items`, `payments` y `shipments`.

El esquema real correspondía a lo que `scripts/create_tables.py`
(`Base.metadata.create_all`) creó cuando el proyecto solo tenía autenticación.
Cada liberación desplegaba **código**, nunca **esquema**, y `alembic_version` ni
siquiera existía.

Al automatizar las migraciones aparecieron tres fallos de permisos encadenados,
todos porque el rol de la aplicación (`usr_gac_admin`) no es el dueño del
esquema. Los tres se reprodujeron contra Postgres antes de darlos por
diagnosticados:

1. **`CREATE SCHEMA IF NOT EXISTS gac` → `permission denied for database`.**
   Postgres comprueba el privilegio `CREATE` sobre la base **antes** de evaluar
   el `IF NOT EXISTS`, así que falla aunque el esquema ya exista.
2. **`alembic_version` se creaba en `public`**, porque alembic la ubica en el
   `search_path` y `DB_SCHEME` no se escribe en el `.env` del despliegue.
3. **`permission denied for table users`.** Crear una clave foránea que apunta a
   `gac.users` exige el privilegio `REFERENCES` sobre esa tabla, que el rol no
   tenía por no ser su dueño.

Un cuarto fallo, no de permisos pero sí de esta tanda: comprobar la existencia
del esquema con un `SELECT` previo dejaba **una transacción implícita abierta**.
Alembic dejaba de ser dueño de la suya, ejecutaba las migraciones, escribía sus
`Running upgrade` en el log y al cerrar la conexión hacía **rollback de todo sin
un solo error visible**.

## Decisión

**1. El despliegue aplica migraciones, y si fallan el despliegue falla.**

`docker exec ${CONTAINER_NAME} alembic upgrade head` en el paso *Deploy to EC2*,
con comprobación explícita del resultado. Sin ella, `docker exec` devuelve
no-cero pero, al no ser el último comando del script, la acción SSH no lo
propaga: un esquema desalineado se reporta como despliegue correcto. Eso ya
ocurrió una vez y es peor que un despliegue rojo.

**2. Las migraciones son idempotentes.**

Guardas de existencia por tabla y por índice. No porque sea elegante, sino
porque la base y `alembic_version` llevaban meses desincronizados y había que
poder ejecutarlas sobre ese estado: crean lo que falta y saltan lo que ya está.

**3. `alembic_version` vive en el esquema `gac`.**

Vía `version_table_schema="gac"` en `alembic/env.py`. Junto a lo que gestiona, y
sin depender de los permisos sobre `public`.

**4. El esquema se asegura en `env.py`, consultando antes de crear.**

Solo se intenta `CREATE SCHEMA` si `information_schema.schemata` dice que falta.
El `commit` posterior es **incondicional**: cerrar esa transacción implícita es
lo que permite que alembic sea dueño de la suya.

**5. Las migraciones se ejecutan con el rol de la aplicación**, que necesita
estos privilegios sobre `gac`:

```sql
GRANT USAGE, CREATE ON SCHEMA gac TO usr_gac_admin;
GRANT REFERENCES ON ALL TABLES IN SCHEMA gac TO usr_gac_admin;
```

`REFERENCES` es el que se olvida: hace falta para crear una clave foránea que
apunte a una tabla **preexistente** que el rol no posee. Las tablas creadas por
las propias migraciones sí le pertenecen y no lo requieren.

## Consecuencias

- Un entorno nuevo se levanta con `alembic upgrade head`, sin
  `create_tables.py`. Ese script queda como herramienta de desarrollo.
- **Cada tabla nueva que referencie una tabla preexistente ajena al rol
  necesitará `REFERENCES` sobre ella.** El `GRANT ... ON ALL TABLES` cubre las
  actuales, no las futuras creadas por otro dueño. Si aparece un
  `permission denied for table X` al migrar, es esto.
- Los roles `admin` y `vendedor` se siembran por migración
  (`c1d5a8b03e47`), porque `require_roles(...)` los exige por nombre en 27
  sitios. Antes solo existían si alguien ejecutaba un script a mano, y sin
  `admin` no hay forma de arreglarlo desde la interfaz.
- `make migrations-check` (`scripts/check_migration_drift.py`) diagnostica el
  desfase sin tocar nada.

## Verificación

Las migraciones se prueban contra Postgres real, y se comprueba **el estado de
la base**, no el log. Es una distinción con historia: durante este trabajo el
log dijo "3 migraciones aplicadas" mientras la base seguía intacta por el
rollback silencioso del punto 4.

Escenarios cubiertos: réplica de producción con el rol sin `CREATE` sobre la
base ni `REFERENCES`, base nueva sin esquema, y reejecución (que no debe
reaplicar nada).

```sql
-- Privilegios del rol
SELECT has_database_privilege('usr_gac_admin', current_database(), 'CREATE') AS crear_en_bd,
       has_schema_privilege('usr_gac_admin', 'gac', 'CREATE')                AS crear_en_esquema,
       has_table_privilege('usr_gac_admin', 'gac.users', 'REFERENCES')       AS referenciar_users;

-- Estado tras migrar
SELECT version_num FROM gac.alembic_version;
```

## Alternativas descartadas

**Un rol propietario distinto del de la aplicación, solo para migrar.** Es
mejor a medio plazo: la cuenta que sirve peticiones no debería poder alterar el
esquema. Se descarta *por ahora* para no añadir un secreto y un rol nuevos en
mitad de una entrega, no porque sea peor. **Es la evolución natural de este
ADR** y el momento de retomarlo es cuando `REFERENCES` vuelva a estorbar.

**`alembic stamp` para saldar el desfase.** Habría marcado como aplicadas
cuatro tablas que no existían, y entonces no se habrían creado nunca. Marcar
como hecho lo que no está hecho esconde el problema en vez de resolverlo.

**Migraciones al arrancar el contenedor** (`CMD alembic upgrade head && uvicorn`).
Acopla el arranque de la aplicación al estado de la base y, con más de una
réplica, varias intentarían migrar a la vez. Como paso explícito del despliegue
se ve en el log y falla donde debe.
