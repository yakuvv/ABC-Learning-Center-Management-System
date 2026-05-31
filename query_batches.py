import sqlite3
try:
    conn = sqlite3.connect('abc_learning_center.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM BATCH;')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM BATCH WHERE isActive=1;')
    active = cursor.fetchone()[0]
    print(f'Total: {total}, Active: {active}')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
