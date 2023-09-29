import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter

def ler_arquivo(nome_arquivo, stock, oprType):
    datas = []
    precos = []

    with open(nome_arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()

        for linha in linhas:
            partes = linha.split()

            if len(partes) == 15 and partes[6] == 'Stock:' and partes[7] == stock and partes[10] == oprType+':':
                data_hora = datetime.strptime(partes[1], '%H:%M:%S.%f')

                try:
                    preco = float(partes[11].replace('R$', '').replace(',', '.'))
                except ValueError:
                    continue

                datas.append(data_hora)
                precos.append(preco)

    return datas, precos

def calcular_variacoes_percentuais(precos):
    variacoes = []
    for i in range(1, len(precos)):
        variacao = (precos[i] - precos[i-1]) / precos[i-1] * 100
        variacoes.append(variacao)
    return variacoes

def achar_venda_seguinte(pos,vendas):
    for i in range(0, len(vendas)):
        if vendas[i] > pos:
            return vendas[i]


def gerar_grafico(datas, precos, variacoes, stock, precosVenda):
    plt.plot(datas, precos, '-o', color='black', markersize=4)
    plt.plot(datas, precosVenda, '-o', color='green', markersize=4)
    plt.xlabel('Hora e Minuto')
    plt.ylabel('Preço')
    plt.title('Variação do preço da ação '+stock)

    pontosDeCompra = []
    pontosDeVenda = []
    todosPontos = []

    numStockPorcompra = 5
    mediaPreco = 0;

    totalCompra = 0
    totalVenda = 0
    totalStock = 0
    variacaoParaVenda = 0

    
    # Formatar o eixo x para exibir somente as horas e minutos
    formatter = DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(formatter)

    for i, variacao in enumerate(variacoes):
        if i > 0 and variacao <= -0.1:
            plt.plot(datas[i+1], precos[i+1], 'bo', markersize=6)
            #pontosDeCompra.append(i+1)
            #todosPontos.append(i+1)
            print("comprei no ponto "+str(datas[i+1]))
            mediaPreco = (mediaPreco * totalStock + (precos[i+1] * numStockPorcompra)) / (totalStock + numStockPorcompra)
            totalStock += numStockPorcompra
            totalCompra += precos[i+1]*numStockPorcompra
        if mediaPreco > 0:
            variacaoParaVenda = (precosVenda[i+1] - mediaPreco) * 100 / mediaPreco
            
        if i > 1 and variacaoParaVenda > 0.1 and totalStock > 0:
            plt.plot(datas[i+1], precosVenda[i+1], 'rs', markersize=6)
            print("Variacao para venda "+str(variacaoParaVenda))
            #pontosDeVenda.append(i+1)
            #todosPontos.append(i+1)
            print("Vendi no ponto "+str(datas[i+1])+ " a preco "+str(precosVenda[i+1])+ " media: "+str(mediaPreco))
            totalVenda += precosVenda[i+1]*totalStock
            print("total de vendas: "+str(totalVenda))
            totalStock = 0
        

    print("compras : "+str(totalCompra)+ " vendas: "+str(totalVenda)+" Lucro: "+str(totalVenda - totalCompra)+" totaldeAcoes: "+str(totalStock))


    plt.text(datas[0], max(precos), 'Lucro: '+str(totalVenda - totalCompra), ha='left', va='center', color='green')
            
    plt.show()

# Nome do arquivo que contém os dados da ação
arquivo = '/home/lavorato/Desktop/EasyMoney/easymoney/python/history_2023-09-11.txt'
# Nome da ação desejada
stock_desejada = 'CSNA3F'

# Ler o arquivo e extrair as informações para a ação desejada
datas, precosCompra = ler_arquivo(arquivo, stock_desejada,"Compra")
#print(precosCompra)

datas, precosVenda = ler_arquivo(arquivo, stock_desejada,"Venda")
#print(precosVenda)

# Calcular as variações percentuais em relação ao ponto anterior
variacoes = calcular_variacoes_percentuais(precosCompra)
print(len(variacoes))

# Gerar o gráfico com a marcação dos pontos de redução
gerar_grafico(datas, precosCompra, variacoes,stock_desejada,precosVenda)
