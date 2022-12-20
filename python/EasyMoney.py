import os
from ppadb.client import Client as AdbClient
import json
import matplotlib.pyplot as plt
import numpy as np
import tkinter
from tkinter import *
from tkinter.ttk import *
import threading
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import date
from pathlib import Path
import sys
from yahooquery import Ticker
import pandas as pd


execDump = 1
listStock = {}
generalInfo = {}
today = date.today()

class Stock:
    def __init__(self, nome, quantidade, precoMedio, situacao):
        self.__nome = nome
        self.__quantidade = quantidade
        self.__precoMedio = precoMedio
        self.__situacao = situacao

    def set_nome(self, nome):
        self.__nome = nome
    
    def get_quant(self):
        return self.__quantidade

    def get_valormed(self):
        return self.__precoMedio
    
    def get_situacao(self):
        return self.__situacao


def dump_logcat(connection):
    global execDump
    print("iniciando logs")
    fileName = "history_"+str(today)+".txt"
    p = Path(__file__).with_name(fileName)
    log = p.open("w+")
    while execDump == 1:
        data = connection.read(1024)
        if not data:
            break
        try:
            log.write(data.decode('utf-8'))
            print(data.decode('utf-8'))
        except Exception as e:
            print("Erro to read log "+str(e))

    print("Encerrado getlog")
    connection.close()
    log.close

def extractInfoFromLog():
        fileNameExtract = "history_"+str(today)+".txt"
        p = Path(__file__).with_name(fileNameExtract)
        with p.open('r', encoding='utf8') as f:
            for info in f:
                try:
                    if "quantidade:" in info:
                        stockPrices = info.split()
                        print(stockPrices)
                        stockname = stockPrices[7]
                        quantidade = stockPrices[9]
                        #print("Lendo : "+stockname+ " com quantidade: "+quantidade)
                    
                    if "valor Médio:" in info:
                        stockPrices = info.split()
                        stockname = stockPrices[7]
                        valorMedio = stockPrices[10]
                        #print("Lendo : "+stockname+ " valor Médio: "+valorMedio)
                        #listStock[stockname]= Stock(stockname, quantidade, valorMedio)
                    
                    if "Situacao:" in info:
                        stockPrices = info.split()
                        stockname = stockPrices[7]
                        situacao = stockPrices[9]
                        #print("Lendo : "+stockname+ " situacao: "+situacao)
                        listStock[stockname]= Stock(stockname, quantidade, valorMedio,situacao)

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
                except Exception as e:
                    print("Error to read data: "+str(e))   

        saveFile()
    

def saveFile():
    stockDetails = ""
    fileInfoName = "fileInfo_"+str(today)+".txt"
    p = Path(__file__).with_name(fileInfoName)
    fileInfo = p.open("w+")
    for key in listStock:
        print(key, ' ', listStock[key].get_quant(), ' ', listStock[key].get_valormed())
        infoLine = key + " "+listStock[key].get_quant()+ " "+listStock[key].get_valormed()
        stockDetails = stockDetails+key+"    "+listStock[key].get_quant()+"                   "+listStock[key].get_situacao()+"\n"
        fileInfo.write(infoLine+"\n")
    for key in generalInfo:
        print(key, ' ', generalInfo[key])
        infoLine = key + " "+generalInfo[key]
        fileInfo.write(infoLine+"\n")
    fileInfo.close
    stockDetailVar.set(stockDetails)

def plotGraph(tam):
    price = []
    time = []
    i = 0
    stock2 = stockGraphVar.get()
    fileNameGraph = "history_"+str(today)+".txt"
    #fileNameGraph = "history_2022-11-29.txt"
    p = Path(__file__).with_name(fileNameGraph)
    with p.open('r', encoding='utf8') as f:
        for line in f:
            if "Preço" in line and "R$" in line and stock2 in line:
                stockPrices = line.split()
                price.append(float(stockPrices[10].replace(",",".")))
                timePrice = stockPrices[1]
                time.append(timePrice[0:5])

    xpoints = np.array(time)    
    ypoints = np.array(price)

    if tam != -1:
        if xpoints.size >= tam:
            n = xpoints.size - tam
            xpoints = xpoints[n:]
            ypoints = ypoints[n:]


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
        if percVar < 0 and (percVar*-1)>=0.2 and number <= 20:
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
    canvas.get_tk_widget().place(x=310, y=160)
    plt.show()

def plotGraphByFile(tam):
    price = []
    time = []
    i = 0
    stock2 = stockGraphVar.get()
    fileNameGraph = "tupy.txt"
    #fileNameGraph = "history_2022-11-29.txt"
    p = Path(__file__).with_name(fileNameGraph)
    with p.open('r', encoding='utf8') as f:
        for line in f:
            stockPrices = line.split()
            price.append(float(stockPrices[10].replace(",",".")))
            timePrice = stockPrices[1]
            time.append(timePrice[0:5])

    xpoints = np.array(time)    
    ypoints = np.array(price)

    if tam != -1:
        if xpoints.size >= tam:
            n = xpoints.size - tam
            xpoints = xpoints[n:]
            ypoints = ypoints[n:]


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
        if percVar < 0 and (percVar*-1)>=0.2 and number <= 20:
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
    canvas.get_tk_widget().place(x=310, y=160)
    plt.show()

def readLogsFromAndroid(device):
    device.shell("logcat | grep STOCK_INFO", handler=dump_logcat)
 
def copyBackupFile():
    client = AdbClient(host="127.0.0.1", port=5037)
    print(client.version())
    devices = client.devices()
    device = devices[0]
    file = "/home/lavorato/Desktop/EasyMoney/easymoney/python/fileInfo_"+str(today)+".txt"
    fileTo = "/data/local/tmp/fileInfo_"+str(today)+".txt"
    device.push(file, fileTo)

def getInfoPeriodic():
    while execDump == 1:
        print("Listening...")
        time.sleep(60)
        extractInfoFromLog()
    print("Encerrando getInfo")

def start():
    global execDump
    execDump = 1
    x = threading.Thread(target=init)
    x.setName("initializing")
    x.start()

def stop():
    global execDump
    client = AdbClient(host="127.0.0.1", port=5037)
    print(client.version())
    devices = client.devices()
    device = devices[0]
    file = "/home/lavorato/Desktop/EasyMoney/easymoney/python/fileToEnd.txt"
    fileTo = "/data/local/tmp/end.txt"
    device.push(file, fileTo)
    execDump = 0
    statusVar.set("Parando...")


def startGetStockPrices(device):
    device.shell("rm /data/local/tmp/end.txt")
    device.shell("am instrument -w -r -e class com.lavorato.easymoney.CheckStockPrice com.lavorato.easymoney.test/androidx.test.runner.AndroidJUnitRunner")
    statusVar.set("Leituras interrompidas!")

def startGetStockPricesManual():
    x = threading.Thread(target=init)
    x.setName("initializing")
    x.start()


def init(args=None):
 
    # Default is "127.0.0.1" and 5037
    client = AdbClient(host="127.0.0.1", port=5037)
    print(client.version())
    devices = client.devices()
    device = devices[0]

    #device.install("/home/lavorato/Desktop/EasyMoney/easymoney/python/dependencies/StockPrices.apk")
    
    x = threading.Thread(target=startGetStockPrices, args=(device,))
    x.start()

    x = threading.Thread(target=readLogsFromAndroid, args=(device,))
    x.start()

    x = threading.Thread(target=getInfoPeriodic)
    x.start()
    statusVar.set("Executando...")

if __name__ == "__main__":

    abev = Ticker("TUPY3.SA")
    abev2 = abev.history(start='2022-12-09', end='2022-12-10',  interval = "1m")
    df = pd.DataFrame(abev2)
    reset_df = df.reset_index()
    print(reset_df)

    listDate = reset_df['date']

    listX = []
    for d in listDate:
        #print(str(d).partition(' '))
        listX.append(str(d).partition(' ')[2][0:5])
    

    xpoints = np.array(listX)    
    ypoints = np.array(reset_df['close'])

    #print(ypoints)
    
    window=Tk()
    # add widgets here

    # set minimum window size value
    window.minsize(1000, 650)
 
    # set maximum window size value
    window.maxsize(1000, 650)
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
    stockGraphVar = StringVar()
    statusVar = StringVar()

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
    labelSellValue = Label( frameResults, textvariable=sellValueVar, foreground = "blue", font=('Arial', 13, 'bold')).place(x=posXResultRef+590, y=posYResultRef+22)
    sellValueVar.set("1200.00")
    
    frameConfig = Labelframe(window, text = 'Objetivos', width=250, height=140).place(x=20, y=400)
    
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

    frameGraph = Labelframe(window, text = 'Gráfico', width=670, height=535).place(x=300, y=90)
    Label(frameConfig, text = 'Ação: ',font=('Arial', 10, 'bold')).place(x=310, y=115)
    Entry(frameConfig, textvariable=stockGraphVar, width= 15).place(x=360, y=115)
    Button(window, text="Últimos 10 mim", command= lambda: plotGraph(10) ).place(x=500,y=110)
    Button(window, text="Últimos 20 mim", command= lambda: plotGraph(20) ).place(x=630,y=110)
    Button(window, text="Última 1h", command= lambda: plotGraph(60) ).place(x=760,y=110)
    Button(window, text="Todo período", command= lambda: plotGraph(-1) ).place(x=860,y=110)

    labelStockInfo = Label( frameResults, text="Nome      Quantidade     Situação", foreground = "gray", font=('Arial', 10, 'bold')).place(x=30, y=115)
    labelSellValue = Label( frameResults, textvariable=stockDetailVar, foreground = "blue", font=('Arial', 10)).place(x=30, y=145)

    Button(window, text="Salvar dados",command=copyBackupFile, width=25).place(x=45,y=550)
    tkinter.Button(window, text="Iniciar", height=1, width=10, command = start).place(x=735,y=25)
    tkinter.Button(window, text="Parar", height=1, width=10, command = stop).place(x=860,y=25)
    statusLabel = Label(window, textvariable=statusVar,font=('Arial', 10, 'bold')).place(x=735, y=60)
    window.mainloop()
    execDump = 0
    