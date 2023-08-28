import os
from ppadb.client import Client as AdbClient
import json
import matplotlib.pyplot as plt
import numpy as np

execDump = 1

class Stock:
    def __init__(self, nome, quantidade, precoMedio):
        self.__nome = nome
        self.__quantidade = quantidade
        self.__precoMedio = precoMedio

    def set_nome(self, nome):
        self.__nome = nome
    
    def get_quant(self):
        return self.__quantidade

    def get_valormed(self):
        return self.__precoMedio

listStock = {}


def dump_logcat_by_line(connect):
    file_obj = connect.socket.makefile()
    for index in range(0, 10):
        print("Line {}: {}".format(index, file_obj.readline().strip()))

def dump_logcat(connection):
    global execDump
    
    log = open("history.txt","w+")
    while True:
        data = connection.read(1024)
        if not data:
            break
        info = data.decode('utf-8')
        print(data.decode('utf-8'))
        log.write(data.decode('utf-8'))
    print("Encerrado")
    connection.close()
    execDump = 0
    log.close

def createJsonFile():
    #while execDump == 1:
        with open('history3.txt', encoding='utf8') as f:
            for info in f:
                print("-------------")
                print(info)
                print("-------------")
                if "quantidade:" in info:
                    stockPrices = info.split()
                    print(stockPrices)
                    stockname = stockPrices[7]
                    quantidade = stockPrices[9]
                    print("Lendo : "+stockname+ " com quantidade: "+quantidade)
                
                if "valor Médio:" in info:
                    stockPrices = info.split()
                    stockname = stockPrices[7]
                    valorMedio = stockPrices[10]
                    print("Lendo : "+stockname+ " com valor medio: "+valorMedio)
                    listStock[stockname]= Stock(stockname, quantidade, valorMedio)

                if "gasto" in info:
                    stockPrices = info.split()
                    comprado = stockPrices[12]
                    listStock["Comprado"]= comprado

                
                print(listStock)        

        saveFile()

def saveFile():
    fileInfo = open("fileInfo.txt","w+")
    for key in listStock:
        print(key, ' ', listStock[key].get_quant(), ' ', listStock[key].get_valormed())
        infoLine = key + " "+listStock[key].get_quant()+ " "+listStock[key].get_valormed()
        fileInfo.write(infoLine+"\n")
    fileInfo.close

def readFileLog(stock2):
    price = []
    time = []
    i = 0

    with open('history.txt', encoding='utf8') as f:
        for line in f:
            if "Preço" in line and "R$" in line and stock2 in line:
                stockPrices = line.split()
                price.append(float(stockPrices[10].replace(",",".")))
                timePrice = stockPrices[1]
                time.append(timePrice[0:5])

    xpoints = np.array(time)
    ypoints = np.array(price)
    fig, ax = plt.subplots()
    ax.plot(xpoints, ypoints)
    ax.grid(True, linestyle='-.')
    ax.tick_params(axis='x', labelsize='small', rotation=90)

    ant = 0
    number = 0
    unitPriceMed = 0
    for p in ypoints:
        percVar = (p - ant)*100 / ant
        ant = p
        if percVar < 0 and (percVar*-1)>=0.2:
            ax.plot(xpoints[i], p, marker="o", markersize=5, color="red")
            unitPriceMed = ((unitPriceMed * number) + (p * 5)) / (number + 5)
            number = number + 5
        elif percVar > 0:
            percUnitVar = (p - unitPriceMed)*100 / unitPriceMed
            if percUnitVar >= 0.2 and number > 0:
                ax.plot(xpoints[i], p, marker="o", markersize=5, color="green")
                number = 0
        i = i + 1

    plt.show()

def main(args=None):
    # Default is "127.0.0.1" and 5037
    client = AdbClient(host="127.0.0.1", port=5037)
    print(client.version())
    devices = client.devices()

    device = devices[0]
    #device.shell("logcat | grep STOCK_INFO", handler=dump_logcat)
    #readFileLog("TUPY3F")
    createJsonFile()

if __name__ == "__main__":
    main()