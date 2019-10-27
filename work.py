from datetime import date
from gs_quant.data import Dataset
from gs_quant.markets.securities import SecurityMaster, AssetIdentifier
from gs_quant.session import GsSession
import psycopg2
import psycopg2.errorcodes
import time
import logging
import random

client_id = '75d63f91387b434a9c68c8100f45c372'
client_secret = '2567e2c8ad3a203660e2636d07a6a674cbb1fc84774d5870ecba43667a975e74'
print("here")
scopes = GsSession.Scopes.get_default()
GsSession.use(client_id=client_id, client_secret=client_secret, scopes=scopes)

ds = Dataset('USCANFPP_MINI')

gsids = ds.get_coverage()['gsid'].values.tolist()
id_to_names = {}
localDB = []
for gsid in gsids:
    data = ds.get_data(gsid=gsid)
    localDB.append(data)
    if not data.empty:
        id = data['assetId'][0]
        id_to_names[gsid] = (id, SecurityMaster.get_asset(id, AssetIdentifier.MARQUEE_ID))

company_names = list(map(lambda x: (x[0], x[1].name), id_to_names.values()))

def print_all(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM names")
        rows = cur.fetchall()
        for row in rows:
            print([str(cell) for cell in row])

def add_name(conn, gsid, id, name):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM names WHERE name = '{}'".format(name))
        rows = cur.fetchall()
        if len(rows) == 0:
            cur.execute('CREATE TABLE IF NOT EXISTS names (gsid STRING, id STRING, name STRING)')
            cur.execute("INSERT INTO names (gsid, id, name) VALUES ('{}', '{}', '{}')".format(gsid, id, name))
            logging.debug("add_name(): status message: {}".format(cur.statusmessage))
    conn.commit()

def add_names(conn, inp):
    with conn.cursor() as cur:
        for gsid, id, name in inp:
            cur.execute("SELECT * FROM names WHERE name ='{}'".format(name.replace("'", "")))
            rows = cur.fetchall()
            if len(rows) == 0:
                cur.execute('CREATE TABLE IF NOT EXISTS names (gsid STRING, id STRING, name STRING)')
                cur.execute("INSERT INTO names (gsid, id, name) VALUES ('{}', '{}', '{}')".format(gsid, id, name.replace("'", "")))
                logging.debug("add_name(): status message: {}".format(cur.statusmessage))
    conn.commit()

conn = psycopg2.connect(
        database='defaultdb',
        user='maxroach',
        password='Q7gc8rEdS',
        sslmode='require',
        sslrootcert='certs/ca.crt',
        sslkey='certs/client.maxroach.key',
        sslcert='certs/client.maxroach.crt',
        port=26257,
        host='gcp-us-west2.data-fingers.crdb.io'
    )
first = list(id_to_names.keys())[0]
submit = [(str(first), str(id_to_names[first][0]), str(id_to_names[first][1].name))for first in id_to_names]
add_names(conn, submit)
with conn.cursor() as cur:
    for data in localDB:
        dates = list(map(str, data.T.keys()))
        count = 0
        for row in data.T:
            current = dict(data.T[row])
            cur.execute('CREATE TABLE IF NOT EXISTS full_data (date STRING, financialReturnsScore FLOAT, growthScore FLOAT, gsid STRING, integratedScore FLOAT, multipleScore FLOAT)')
            cur.execute("SELECT * FROM full_data WHERE date ='{}' AND gsid = '{}'".format(dates[count], current['gsid']))
            rows = cur.fetchall()
            if len(rows) == 0:
                print("inserted")
                cur.execute("INSERT INTO full_data (date, financialReturnsScore, growthScore, gsid, integratedScore, multipleScore) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(dates[count], current['financialReturnsScore'], current['growthScore'], current['gsid'], current['integratedScore'], current['multipleScore']))
                logging.debug("add_name(): status message: {}".format(cur.statusmessage))
            count += 1

conn.commit()


with conn.cursor() as cur:
    cur.execute("SELECT * FROM full_data")
    rows = cur.fetchall()
    cur.execute("SELECT * FROM names")
    names = cur.fetchall()

conn.commit()
