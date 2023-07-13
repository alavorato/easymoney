import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter

def ler_arquivo(nome_arquivo, stock):
    datas = []
    precos = []

    with open(nome_arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()

        for linha in linhas:
            partes = linha.split()

            if len(partes) == 11 and partes[6] == 'Stock:' and partes[7] == stock and partes[8] == 'Preço:':
                data_hora = datetime.strptime(partes[1], '%H:%M:%S.%f')

                try:
                    preco = float(partes[10].replace('R$', '').replace(',', '.'))
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
    print(variacoes)
    return variacoes

def achar_venda_seguinte(pos,vendas):
    for i in range(0, len(vendas)):
        if vendas[i] > pos:
            return vendas[i]


def gerar_grafico(datas, precos, variacoes, stock):
    plt.plot(datas, precos, '-o', color='black', markersize=4)
    plt.xlabel('Hora e Minuto')
    plt.ylabel('Preço')
    plt.title('Variação do preço da ação '+stock)

    pontosDeCompra = []
    pontosDeVenda = []
    todosPontos = []

    
    # Formatar o eixo x para exibir somente as horas e minutos
    formatter = DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(formatter)

    for i, variacao in enumerate(variacoes):
        if i > 0 and variacao <= -0.1:
            plt.plot(datas[i+1], precos[i+1], 'bo', markersize=6)
            pontosDeCompra.append(i+1)
            todosPontos.append(i+1)
        if i > 1 and variacao > 0.1:
            plt.plot(datas[i+1], precos[i+1], 'bo', markersize=6, color= 'red')
            pontosDeVenda.append(i+1)
            todosPontos.append(i+1)
        
    
    totalCompra = 0
    totalVenda = 0
    totalStock = 0
    lucro = 0
    print(pontosDeCompra)
    print("\n")
    print(pontosDeVenda)
    for i in range(0, len(todosPontos)-4):
        if todosPontos[i] in pontosDeCompra:
            print("comprei no ponto "+str(todosPontos[i]))
            totalCompra += precos[todosPontos[i]]*100
            totalStock +=100
        if todosPontos[i] in pontosDeVenda and totalStock > 0:
            print("vendi no ponto "+str(todosPontos[i]))
            totalVenda += precos[todosPontos[i]]*totalStock
            totalStock = 0
        print("compras : "+str(totalCompra)+ " vendas: "+str(totalVenda)+" Lucro: "+str(totalVenda - totalCompra)+" totaldeAcoes: "+str(totalStock))


    plt.text(datas[0], max(precos), 'Lucro: '+str(totalVenda - totalCompra), ha='left', va='center', color='green')
            
    plt.show()

# Nome do arquivo que contém os dados da ação
arquivo = '/home/lavorato/Desktop/EasyMoney/easymoney/python/history_2023-04-18.txt'
# Nome da ação desejada
stock_desejada = 'ELET3F'

# Ler o arquivo e extrair as informações para a ação desejada
datas, precos = ler_arquivo(arquivo, stock_desejada)

# Calcular as variações percentuais em relação ao ponto anterior
variacoes = calcular_variacoes_percentuais(precos)

# Gerar o gráfico com a marcação dos pontos de redução
gerar_grafico(datas, precos, variacoes,stock_desejada)
