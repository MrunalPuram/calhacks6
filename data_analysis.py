import psycopg2
import psycopg2.errorcodes
import time
import logging
import random
import numpy as np
import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d


def plot_companies(tseries):
    for i in tseries.keys():
        xs = tseries[i][:, 0]
        ys = tseries[i][:,1:]
        plt.figure()
        for j in range(ys.shape[1]):
            plt.plot(xs, ys[:,j], label='{0}'.format(features[j]))
        plt.legend()
        plt.xlabel("Number of Days Since 1/1/2016")
        plt.savefig('graphs_GS/{0}.png'.format(i))

def plot_across_companies(tseries, num_features):
    for j in range(1,num_features+1):
        for i in range(1,num_features+1):
            if i > j:
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                for k in tseries.keys():
                    ax.scatter(tseries[k][:,0],tseries[k][:,i], tseries[k][:,j])
                    plt.xlabel("Number of Days Since 1/1/2016")
                    plt.ylabel(features[i-1])
                    plt.zlabel(features[j-1])
                plt.show()





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


with conn.cursor() as cur:
    cur.execute("SELECT * FROM full_data")
    rows = cur.fetchall()
    cur.execute("SELECT * FROM names")
    names = cur.fetchall()

conn.commit()

companies = {}
for name in names:
    companies[name[0]] = name[2]
#print(companies)
#s = set(companies)
#print(len(companies))
#print(len(s))
#print(rows[2])
numdaysinmonths = [[31, 31], [29, 28], [31, 31], [30, 30], [31, 31], [30, 30], [31, 31], [31, 31], [30, 30], [31, 31], [30, 30], [31, 31]]
features = ['Financial Returns Score', 'Growth Score', 'Integrated Score', 'Multiple Score']
tseries = {}
#print(companies)
miny = 3000
maxy = 0
# first = None
# id = None
# for k in rows[100:]:
#     if first == None:
#         first = k[0]
#         id = k[3]
#     if k[0] == first and k[3] == id:
#         print(k)

#for k in rows:
#    if int(k[0][:4]) > maxy:
#        maxy = int(k[0][:4])
#print(maxy)
#print(k[0][:11])   #Time series are all at time 0:00:00 only date changes Min year = 2016 Max year = 2017 So, total of 730 days (2 years)
for id in companies.keys():
    vals = []
    for k in rows:
        if k[3] == id:
            t = (int(k[0][:4]), int(k[0][5:7]), int(k[0][8:10])) #(Year, Month, Day)
            monthind = t[0]-2016
            totdays = 0
            #print(t[1])
            for i in range(monthind+1):
                if monthind == 0 or i == 1:
                    nd = t[1]   #Year is 2016
                else:
                    nd = 12     #Year is 2017
                #print(nd)
                for j in range(nd):
                    if j == t[1]-1 and i == monthind:
                        totdays+=t[2]
                        continue
                    totdays += numdaysinmonths[j][monthind]
            vals.append([totdays, k[1], k[2], k[4], k[5]])

    vals = np.array(vals)
    tseries[id] = vals
# print(tseries['905255'])
#for i in tseries.keys():
#    print(tseries[i])

#plot_companies(tseries)
plot_across_companies(tseries, 4)
