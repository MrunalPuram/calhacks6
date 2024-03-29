import torch.nn as nn
import torch
import numpy as np
import psycopg2
import psycopg2.errorcodes
import time
import logging
import random
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, layer_dim, output_dim):
        super(LSTMModel, self).__init__()
        self.hidden_dim = hidden_dim
        self.input_dim = input_dim
        self.layer_dim = layer_dim

        self.lstm = nn.LSTM(self.input_dim, self.hidden_dim, self.layer_dim)
        output_dim = output_dim
        # self.fc = nn.Linear(hidden_dim, output_dim)

        self.linear_layers = torch.nn.Sequential(
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        output, (hidden, cell) = self.lstm(x)
        # print(hidden[self.num_layers-1])
        # print(len(hidden[self.num_layers-1]))
        # print(output[len(output)-1])
        # print(len(output[len(output)-1]))

        out = self.linear_layers(output[:,-1,:])
        return out

def make_data(train_percent):
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
    numdaysinmonths = [[31, 31], [29, 28], [31, 31], [30, 30], [31, 31], [30, 30], [31, 31], [31, 31], [30, 30], [31, 31], [30, 30], [31, 31]]
    features = ['Financial Returns Score', 'Growth Score', 'Integrated Score', 'Multiple Score']
    tseries = {}
    total = []
    for id in companies.keys():
        vals = []
        for k in rows:
            if k[3] == id:
                t = (int(k[0][:4]), int(k[0][5:7]), int(k[0][8:10])) #(Year, Month, Day)
                monthind = t[0]-2016
                totdays = 0
                for i in range(monthind+1):
                    if monthind == 0 or i == 1:
                        nd = t[1]   #Year is 2016
                    else:
                        nd = 12     #Year is 2017
                    for j in range(nd):
                        if j == t[1]-1 and i == monthind:
                            totdays+=t[2]
                            continue
                        totdays += numdaysinmonths[j][monthind]
                vals.append([totdays, k[1], k[2], k[4], k[5]])
        #print(np.array(vals).shape)
        if len(vals) == 22:
            total.append(vals)
        vals = np.array(vals)
        tseries[id] = vals
    #for i in tseries.keys():
        #print(tseries[i])
    total = np.array(total)
    print(total.shape)
    train = total[:int(train_percent*total.shape[0]),:,:]
    test = total[int(train_percent*total.shape[0]):,:,:]
    # train = train.transpose(1,0,2)
    # test = test.transpose(1,0,2)
    trainx = train[:,:17,:]
    trainy=train[:,17:,:]
    testx=test[:,:17,:]
    testy=test[:,17:,:]
    print(trainx.shape)
    print(trainy.shape)
    print(testx.shape)
    print(testy.shape)
    return [trainx, trainy, testx, testy]

def train(input_dim, hidden_dim, layer_dim, output_dim, epochs, data):
    # input_dim = 5
    # hidden_dim = 15
    # layer_dim = 2
    # output_dim = 25
    # epochs = 700
    trainx, trainy, testx, testy = data
    model = LSTMModel(input_dim, hidden_dim, layer_dim, output_dim)
    model.to(device)

    # trainy, testy = trainy.transpose(1,0,2).reshape(55,25), testy.transpose(1,0,2).reshape(24,25)



    criterion = nn.MSELoss()
    learning_rate = 0.1
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for i in range(epochs):
        outputs = model.forward(trainx)
        #print(trainy.reshape(trainy.shape[0], trainy.shape[1]*trainy.shape[2]).shape)
        #print(outputs.shape)
        loss = criterion(outputs, trainy.reshape(trainy.shape[0], trainy.shape[1]*trainy.shape[2]))
        if i % 100 == 0:
            print("Epoch: {0}, Loss: {1}".format(i,loss.item()))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    return model


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--load_model', '-lm', type=str, default=None)
    parser.add_argument('--input_dim', '-in_dim', type=int, default=5)
    parser.add_argument('--hidden_dim', '-h_dim', type=int, default=10)
    parser.add_argument('--layer_dim', '-l_dim', type=int, default=3)
    parser.add_argument('--output_dim', '-out_dim', type=int, default=25)
    parser.add_argument('--epochs', '-ep', type=int, default=1000)
    parser.add_argument('--train_split', '-ts', type=float, default=0.8)
    parser.add_argument('--model_name', '-mn', type=str, default=None)


    args = parser.parse_args()
    # convert to dictionary
    params = vars(args)

    data = make_data(params['train_split'])   #trainx, trainy, testx, testy
    for i in range(len(data)):
        data[i] = torch.from_numpy(data[i]).float().to(device)
    trainx, trainy, testx, testy = data
    # trainx = torch.from_numpy(trainx).float().to(device)
    # trainy = torch.from_numpy(trainy).float().to(device)
    # testx = torch.from_numpy(testx).float().to(device)
    # testy = torch.from_numpy(testy).float().to(device)
    if params['load_model'] == None:
        model = train(params['input_dim'], params['hidden_dim'], params['layer_dim'], params['output_dim'], params['epochs'], data)
    else:
        model = LSTMModel(params['input_dim'], params['hidden_dim'], params['layer_dim'], params['output_dim'])
        model.load_state_dict(torch.load('rnn_models/{0}'.format(params['model_name'])))
        model.eval()#model = torch.load('rnn_models/{0}'.format(params['model_name']))
    with torch.no_grad():
        print(model.forward(testx).reshape(16,5,5))
        print(testy.reshape(testy.shape[0], testy.shape[1]*testy.shape[2]))
        print(torch.sum(model.forward(testx) - testy.reshape(testy.shape[0], testy.shape[1]*testy.shape[2])))
    torch.save(model.state_dict(), 'rnn_models/{0}_{1}_{2}.pt'.format(params['hidden_dim'], params['layer_dim'], params['epochs']))
    #model.save_state_dict()

    features = ['Financial Returns Score', 'Growth Score', 'Integrated Score', 'Multiple Score']
    prediction = model.forward(testx).reshape(16,5,5).detach().numpy()
    actual = testy.reshape(testy.shape[0], testy.shape[1]*testy.shape[2]).detach().numpy()
    for i in range(prediction.shape[0]):
        xs = testy[i,:,0].detach().numpy()
        yactual = testy[i,:,1:].detach().numpy()
        ypredicted = prediction[i,:,1:]
        xpred = prediction[i,:,0]
        #print(yactual.shape)
        plt.figure()
        for j in range(yactual.shape[1]):
            plt.plot(xs, yactual[:,j], label='{0} Actual'.format(features[j]))
            plt.plot(xs, ypredicted[:,j], label='{0} Predicted'.format(features[j]))
            plt.legend()
            plt.xlabel('Number of Days Since 1/1/2016')
        plt.savefig('rnn_testpredictgraphs/{0}.png'.format(i))

if __name__ == "__main__":
    main()
