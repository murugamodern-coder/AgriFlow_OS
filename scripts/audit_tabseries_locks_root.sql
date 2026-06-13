-- tabSeries lock audit (run as MariaDB root)
SELECT '=== SHOW FULL PROCESSLIST ===' AS section;
SHOW FULL PROCESSLIST;

SELECT '=== INNODB_TRX ===' AS section;
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

SELECT '=== tabSeries FR rows ===' AS section;
SELECT name, `current`, modified
FROM `_d3af7c5e24dd488b`.`tabSeries`
WHERE name LIKE 'FR%';

SELECT '=== tabSeries / FOR UPDATE in processlist ===' AS section;
SELECT id, user, host, db, command, time, state, LEFT(info, 800) AS info
FROM information_schema.processlist
WHERE info LIKE '%tabSeries%'
   OR info LIKE '%FOR UPDATE%'
   OR (command != 'Sleep' AND time > 5)
ORDER BY time DESC;

SELECT '=== Sleep connections with open trx (age>30s) ===' AS section;
SELECT p.id, p.user, p.host, p.db, p.command, p.time, p.state, LEFT(p.info, 200) AS info,
       t.trx_started, TIMESTAMPDIFF(SECOND, t.trx_started, NOW()) AS trx_age_seconds,
       t.trx_query
FROM information_schema.processlist p
JOIN information_schema.innodb_trx t ON t.trx_mysql_thread_id = p.id
WHERE p.command = 'Sleep' OR p.time > 10
ORDER BY t.trx_started;
