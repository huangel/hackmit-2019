import datetime
import io
import numpy as np
import sqlite3
from sklearn.neighbors import KDTree

def _adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def _convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

sqlite3.register_adapter(np.ndarray, _adapt_array)
sqlite3.register_converter("array", _convert_array)

class VoiceRecognition():
    def __init__(self):
        self.db = 'voices.db'
        self.conn = sqlite3.connect(self.db, detect_types=sqlite3.PARSE_DECLTYPES)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS voices_table (name text, voice array, timing timestamp);''')
        self.conn.commit()
        all_names = self.c.execute('''SELECT name FROM voices_table''').fetchall()
        self.all_names = [n[0] for n in all_names]
        all_vectors = self.c.execute('''SELECT voice FROM voices_table''').fetchall()
        self.all_vectors = np.array([v[0] for v in all_vectors])

    def predict(self, voice_vector):
        if len(self.all_vectors) == 0:
            timestamp = datetime.datetime.now()
            self.c.execute('''INSERT into voices_table VALUES (?,?,?);''', ('', voice_vector, timestamp))
            self.conn.commit()
            return 'Enter name: '
        tree = KDTree(self.all_vectors)
        if len(self.all_vectors) == 1:
            dist, ind = tree.query([voice_vector], k=1)
            ind_1 = ind[0][0]
            dist_1 = dist[0][0]
            timestamp = datetime.datetime.now()
            self.c.execute('''INSERT into voices_table VALUES (?,?,?);''', ('', voice_vector, timestamp))
            self.conn.commit()
            if dist_1 <= 10:
                return self.all_names[ind_1]
            else:
                return "Suggested: " + self.all_names[ind_1]
        else:
            dist, ind = tree.query([voice_vector], k=2)
            ind_1 = ind[0][0]
            ind_2 = ind[0][1]
            dist_1 = dist[0][0]
            dist_2 = dist[0][1]
        timestamp = datetime.datetime.now()
        self.c.execute('''INSERT into voices_table VALUES (?,?,?);''', ('', voice_vector, timestamp))
        self.conn.commit()
        if abs(dist_1 - dist_2) <= 0.5:
            return 'Suggested: ' + self.all_names[ind_1] + ' ' + self.all_names[ind_2]
        if dist_1 <= 10:
            return self.all_names[ind_1]
        return 'Suggested: ' + self.all_names[ind_1]

    def reassign_name(self, name):
        num = 0
        for n in self.all_names:
            if n == name:
                num += 1
                if num == 3:
                    return
        self.c.execute('''UPDATE voices_table SET name = ? WHERE name = ?''', (name, ''))
        self.conn.commit()
