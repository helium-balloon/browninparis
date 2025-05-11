# analyse de decouvrir des motifs et des idées importants dans la carte et le data
import sqlite3
conn = sqlite3.connect('stats_big.db')
c = conn.cursor()

sort_largest_distance = '''
SELECT * FROM CREATE TABLE income_paris AS
    SELECT * FROM income
    WHERE IRIS LIKE '75%';
'''

c.execute(paris_location_command)
conn.commit()

sort_smallest_distance = '''
CREATE TABLE income_paris AS
    SELECT * FROM income
    WHERE IRIS LIKE '75%';
'''