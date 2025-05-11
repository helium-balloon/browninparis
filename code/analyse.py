# analyse de decouvrir des motifs et des idées importants dans la carte et le data
import sqlite3
conn = sqlite3.connect('stats_big.db')
c = conn.cursor()

get_avg_distance = '''
SELECT
    (DISP_MED21 / 10000) * 10000 AS income_bin,
    AVG(dist_to_green) AS avg_distance
FROM income_and_distance
WHERE DISP_MED21 BETWEEN 0 AND 70000
GROUP BY income_bin
ORDER BY income_bin;
'''

c.execute(get_avg_distance)
conn.commit()

print(c.fetchall())

# results: [(10000, 191.20), 
#           (20000, 239.43), 
#           (30000, 249.93), 
#           (40000, 348.70), 
#           (50000, 315.77), 
#           (60000, 242.71)]