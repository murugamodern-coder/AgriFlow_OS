-- tabSeries lock audit for dev.agriflow.local
SELECT '=== SHOW FULL PROCESSLIST (non-Sleep) ===' AS section;
SHOW FULL PROCESSLIST;

SELECT '=== INNODB_TRX (active transactions) ===' AS section;
SELECT
  trx_id,
  trx_state,
  trx_started,
  TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS age_seconds,
  trx_mysql_thread_id,
  trx_query,
  trx_rows_locked,
  trx_rows_modified,
  trx_tables_locked
FROM information_schema.innodb_trx
ORDER BY trx_started;

SELECT '=== INNODB_LOCK_WAITS ===' AS section;
SELECT
  r.trx_id AS waiting_trx_id,
  r.trx_mysql_thread_id AS waiting_thread,
  r.trx_query AS waiting_query,
  b.trx_id AS blocking_trx_id,
  b.trx_mysql_thread_id AS blocking_thread,
  b.trx_query AS blocking_query,
  TIMESTAMPDIFF(SECOND, b.trx_started, NOW()) AS blocking_age_seconds
FROM information_schema.innodb_lock_waits w
JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id;

SELECT '=== tabSeries row ===' AS section;
SELECT name, current, modified FROM `tabSeries` WHERE name LIKE 'FR-%' OR name = 'FR-';

SELECT '=== tabSeries-related processlist ===' AS section;
SELECT id, user, host, db, command, time, state, LEFT(info, 500) AS info
FROM information_schema.processlist
WHERE info LIKE '%tabSeries%' OR info LIKE '%Series%' OR info LIKE '%FOR UPDATE%'
ORDER BY time DESC;
