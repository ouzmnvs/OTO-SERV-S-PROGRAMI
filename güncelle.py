import sqlite3
from database_progress import update_servis_tutar

conn = sqlite3.connect("oto_servis.db")
cursor = conn.cursor()
cursor.execute("SELECT id FROM servisler")
servisler = cursor.fetchall()
conn.close()

for (servis_id,) in servisler:
    update_servis_tutar(servis_id)