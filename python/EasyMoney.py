import os
from ppadb.client import Client as AdbClient
import json
import matplotlib.pyplot as plt
import numpy as np
from tkinter import *
from tkinter.ttk import *
import threading
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import date

execDump = 1
listStock = {}
generalInfo = {}

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


def dump_logcat(connection):
    global execDump
    print("iniciando logs")
    
    log = open("history_"+today+".txt","w+")
    while execDump == 1:
        data = connection.read(1024)
        if not data:
            break
        print(data.decode('utf-8'))
        log.write(data.decode('utf-8'))
    print("Encerrado")
    connection.close()
    log.close

def extractInfoFromLog():
    #while execDump == 1:
        with open('history.txt', encoding='utf8') as f:
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
                    comprado = stockPrices[11]
                    generalInfo["Comprado"]= comprado
                    buyValueVar.set(comprado)
                
                if "vendido" in info:
                    stockPrices = info.split()
                    vendido = stockPrices[11]
                    generalInfo["Vendido"]= vendido
                    sellValueVar.set(vendido)
                
                if "investido" in info:
                    stockPrices = info.split()
                    investido = stockPrices[11]
                    generalInfo["Investido"]= investido
                    investValueVar.set(investido)
                
                if "lucro - tax" in info:
                    stockPrices = info.split()
                    lucro = stockPrices[11]
                    generalInfo["Lucro"]= lucro
                    profitValueVar.set(lucro)

                
                print(listStock)
                print(generalInfo)      

        saveFile()

def saveFile():
    fileInfo = open("fileInfo_"+today+".txt","w+")
    for key in listStock:
        print(key, ' ', listStock[key].get_quant(), ' ', listStock[key].get_valormed())
        infoLine = key + " "+listStock[key].get_quant()+ " "+listStock[key].get_valormed()
        fileInfo.write(infoLine+"\n")
    for key in generalInfo:
        print(key, ' ', generalInfo[key])
        infoLine = key + " "+generalInfo[key]
        fileInfo.write(infoLine+"\n")
    fileInfo.close

def plotGraph(stock2):
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

    figure = Figure(figsize=(6.5, 4.5 ), dpi=100, facecolor ="gray")
    figure.suptitle(stock2,fontweight ="bold") 

    graph = figure.add_subplot(1, 1, 1)

    graph.plot(xpoints, ypoints)
    graph.grid(True, linestyle='-.')
    graph.tick_params(axis='x', labelsize=8, rotation=90)
    graph.tick_params(axis='y', labelsize=8)

    ant = 0
    number = 0
    unitPriceMed = 0
    for p in ypoints:
        percVar = (p - ant)*100 / ant
        ant = p
        if percVar < 0 and (percVar*-1)>=0.2:
            graph.plot(xpoints[i], p, marker="o", markersize=5, color="red")
            unitPriceMed = ((unitPriceMed * number) + (p * 5)) / (number + 5)
            number = number + 5
        elif percVar > 0:
            percUnitVar = (p - unitPriceMed)*100 / unitPriceMed
            if percUnitVar >= 0.2 and number > 0:
                graph.plot(xpoints[i], p, marker="o", markersize=5, color="green")
                number = 0
        i = i + 1

    canvas = FigureCanvasTkAgg(figure, window)
    canvas.get_tk_widget().place(x=310, y=110)
    plt.show()

def readLogsFromAndroid(device):
    try:
        device.shell("logcat | grep STOCK_INFO", handler=dump_logcat)
    except:
        print("No device")

def getInfoPeriodic():
    while execDump == 1:
        print("Listening...")
        time.sleep(120)
        extractInfoFromLog()

def start():
    x = threading.Thread(target=init)
    x.start() 

def init(args=None):
 
    # Default is "127.0.0.1" and 5037
    client = AdbClient(host="127.0.0.1", port=5037)
    print(client.version())
    devices = client.devices()
    device = devices[0]
    
    x = threading.Thread(target=readLogsFromAndroid, args=(device,))
    x.start()

    x = threading.Thread(target=getInfoPeriodic)
    x.start()

if __name__ == "__main__":

    today = date.today()
    window=Tk()
    # add widgets here

    # set minimum window size value
    window.minsize(1000, 600)
 
    # set maximum window size value
    window.maxsize(1000, 600)
    style = Style(window)
    window.title('Easy Money')

    profitValueVar = StringVar()
    investValueVar = StringVar()
    buyValueVar = StringVar()
    sellValueVar = StringVar()
    stockDetailVar = StringVar()
    targetTobuyVar = StringVar()
    targetToSellVar = StringVar()
    limitValueInvest = StringVar()

    style.configure("My.TLabel", font=('Arial', 10), foreground = "gray")

    posXResultRef = 15
    posYResultRef = 15

    frameResults = Labelframe(window, text = 'Resultados', width=700, height=60).place(x=posXResultRef, y=posYResultRef)
    
    labelProfit = Label( frameResults, text="Lucro:", style="My.TLabel").place(x=posXResultRef+30, y=posYResultRef+25)
    labelProfitValue = Label( frameResults, textvariable=profitValueVar, foreground = "green", font=('Arial', 13, 'bold')).place(x=posXResultRef+80, y=posYResultRef+22)
    profitValueVar.set("40.00")

    labelInvest = Label( frameResults, text="Investido:", style="My.TLabel").place(x=posXResultRef+180, y=posYResultRef+25)
    labelInvestValue = Label( frameResults, textvariable=investValueVar, foreground = "orange", font=('Arial', 13, 'bold')).place(x=posXResultRef+250, y=posYResultRef+22)
    investValueVar.set("200.00")

    labelBuy = Label( frameResults, text="Compras:", style="My.TLabel").place(x=posXResultRef+350, y=posYResultRef+25)
    labelBuyValue = Label( frameResults, textvariable=buyValueVar, foreground = "red", font=('Arial', 13, 'bold')).place(x=posXResultRef+420, y=posYResultRef+22)
    buyValueVar.set("1200.00")

    labelSell = Label( frameResults, text="Vendas:", style="My.TLabel").place(x=posXResultRef+530, y=posYResultRef+25)
    labelSellValue = Label( frameResults, textvariable=buyValueVar, foreground = "blue", font=('Arial', 13, 'bold')).place(x=posXResultRef+590, y=posYResultRef+22)
    sellValueVar.set("1200.00")
    
    frameConfig = Labelframe(window, text = 'Objetivos', width=250, height=175).place(x=20, y=400)
    
    Label(frameConfig, text = 'Compra: ',font=('Arial', 10, 'bold')).place(x=30, y=430)
    Entry(frameConfig, textvariable=targetTobuyVar, width= 15).place(x=100, y=430)
    targetTobuyVar.set("-0.2%")

    Label(frameConfig, text = 'Venda: ',font=('Arial', 10, 'bold')).place(x=40, y=460)
    Entry(frameConfig, textvariable=targetToSellVar, width= 15).place(x=100, y=460)
    targetToSellVar.set("0.2%")

    Label(frameConfig, text = 'Limite: ',font=('Arial', 10, 'bold')).place(x=40, y=490)
    Entry(frameConfig, textvariable=limitValueInvest, width= 15).place(x=100, y=490)
    limitValueInvest.set("2.000,00")

    frameStocks = Labelframe(window, text = 'Ações', width=250, height=300).place(x=20, y=90)
    frameGraph = Labelframe(window, text = 'Gráfico', width=670, height=485).place(x=300, y=90)

    labelStockInfo = Label( frameResults, text="Nome      Quantidade     Situação", foreground = "gray", font=('Arial', 10, 'bold')).place(x=30, y=115)
    labelSellValue = Label( frameResults, textvariable=stockDetailVar, foreground = "blue", font=('Arial', 10)).place(x=30, y=145)

    infoStock = "TUPY3F    10                   3.56\nELET3F     5                    4.52"
    stockDetailVar.set(infoStock)

    #readFileLog("TUPY3F")

    Button(window, text="Parar",command=window.destroy).place(x=840,y=40)
    Button(window, text="Iniciar", command = start).place(x=740,y=40)
    
    window.mainloop()
    execDump = 0
    