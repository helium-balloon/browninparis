# nettoyage du data de revenu pour compris seulement les codes IRIS qui commence avec 75
import sqlite3
conn = sqlite3.connect('stats_big.db')
c = conn.cursor()

paris_location_command = '''
CREATE TABLE income_paris AS
    SELECT * FROM income
    WHERE IRIS LIKE '75%';
'''

c.execute(paris_location_command)
conn.commit()

drop_missing_income_command = '''
DELETE FROM income_paris
WHERE DISP_MED21 = 'ns' 
OR DISP_MED21 = 'nd'
'''

c.execute(drop_missing_income_command)
conn.commit()