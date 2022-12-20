package com.lavorato.easymoney;

import android.support.test.uiautomator.UiDevice;
import android.support.test.uiautomator.UiObject;
import android.support.test.uiautomator.UiScrollable;
import android.support.test.uiautomator.UiSelector;
import android.util.Log;

import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;

import org.junit.Test;
import org.junit.runner.RunWith;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.ArrayList;

@RunWith(AndroidJUnit4.class)
public class CheckStockPrice {

    @Test
    public void getStockPrices() throws Exception {
        // TODO

        float percToBuy = 0.2F;
        float percToSell = 0.2F;
        float stockNumberForOpen = 5;
        boolean buyStatus = true;
        int testLoop = 0;
        float totalMoney = 0;
        float totalMoneyEarned = 0;
        float totalProfit = 0;
        float limitToInvest = 2000.0F;
        float tax = 0;
        UiDevice mDevice = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        ArrayList<Stock> t = new ArrayList<>();
        String day = LocalDateTime.now().getYear()+"-"+LocalDateTime.now().getMonth().getValue()+"-"+LocalDateTime.now().getDayOfMonth();
        Log.i("STOCK_INFO","Data: "+day);
        String filename = "/data/local/tmp/fileInfo_2022-12-06.txt";
        File file = new File(filename);

        if(file.exists()){
            try {
                BufferedReader br = new BufferedReader(new FileReader(file));
                String line;
                while ((line = br.readLine()) != null) {
                    Log.i("STOCK_INFO","file line: "+line);
                    if(line.contains("Comprado")){
                        String info[] = line.split(" ");
                        totalMoney = Float.parseFloat(info[1]);
                    }else if(line.contains("Vendido")) {
                        String info[] = line.split(" ");
                        totalMoneyEarned = Float.parseFloat(info[1]);
                    }else if(line.contains("Lucro")){
                        String info[] = line.split(" ");
                        totalProfit = Float.parseFloat(info[1]);
                    }else if(!line.contains("Vendido") && !line.contains("Comprado") && !line.contains("Lucro") && !line.contains("Investido")){
                        String info[] = line.split(" ");
                        t.add(new Stock(info[0], Integer.parseInt(info[1]), Float.parseFloat(info[2])));
                    }
                }
                br.close();
            }catch (IOException e) {
                Log.e("STOCK_INFO","Error to read file");
            }
        }else{
            t.add(new Stock("VIIA3F",0,0));
            t.add(new Stock("ABEV3F",0,0));
            t.add(new Stock("CSMG3F",0,0));
            t.add(new Stock ("CSNA3F",0,0));
            t.add(new Stock("ELET3F",0,0));
            t.add(new Stock("PETR3F",0,0));
            t.add(new Stock("TUPY3F",0,0));
            t.add(new Stock("SBFG3F",0,0));
            t.add(new Stock("GGBR3F",0,0));
        }

        UiScrollable appViews2= new UiScrollable(new UiSelector().scrollable(true));
        appViews2.setAsVerticalList();

        while(testLoop < 4000){
            for (int i=0;i<t.size();i++){

                UiObject noInternet = mDevice.findObject(new UiSelector().textContains("Sem conexão"));
                UiObject serverError = mDevice.findObject(new UiSelector().textContains("Falha de comunicação"));

                if(noInternet.exists() || serverError.exists()){
                    Log.i("STOCK_INFO","Sem internet ou falha do servidor");
                    Thread.sleep(10000);
                    continue;
                }
                appViews2.scrollIntoView(new UiSelector().text(t.get(i).name));

                UiObject icon3 = mDevice.findObject(new UiSelector().text(t.get(i).name));
                if(icon3.exists())
                    icon3.click();
                else
                    continue;

                //Thread.sleep(2000);
                UiObject stockName = mDevice.findObject(new UiSelector().text(t.get(i).name));
                UiObject stockValue = mDevice.findObject(new UiSelector().textContains(","));
                String price = stockValue.getText();

                if(!stockName.exists() && !stockValue.getText().contains("R$"))
                    break;

                Log.i("STOCK_INFO","Stock: "+t.get(i).name+" Preço: "+price);
                Log.i("STOCK_INFO","Stock: "+t.get(i).name+" quantidade: "+t.get(i).number);
                float currPrice = Float.parseFloat(stockValue.getText().replace("R$ ","").replace(",","."));
                Log.i("STOCK_INFO","Stock: "+t.get(i).name+" valor Médio: "+t.get(i).unitPriceMed);
                Log.i("STOCK_INFO","Stock: "+t.get(i).name+" Situacao: "+((t.get(i).number*currPrice)-(t.get(i).unitPriceMed*t.get(i).number)));
                Log.i("STOCK_INFO", "Total gasto até o momento: " + totalMoney);
                Log.i("STOCK_INFO", "Total vendido até o momento: " + totalMoneyEarned);
                Log.i("STOCK_INFO", "Total investido até o momento: " + (totalMoney - totalMoneyEarned));
                Log.i("STOCK_INFO", "Total de lucro bruto até o momento: " + totalProfit);
                Log.i("STOCK_INFO", "Total de lucro - tax: " + (totalProfit - tax));

                //porcentagem de variacao de uma leitura para outra em relacão a preço
                float percVar = (currPrice - t.get(i).lastPrice)*100 / t.get(i).lastPrice;
                float percVarMedUnit = 0;

                //porcentagem de variacao de uma leitura para outra em relacão a média de preço por unidade
                if(t.get(i).unitPriceMed >0){
                    percVarMedUnit = (currPrice - t.get(i).unitPriceMed)*100 / t.get(i).unitPriceMed;
                }

                Log.i("STOCK_INFO","Valor atual: "+currPrice+" valor anterior: "+t.get(i).lastPrice);
                Log.i("STOCK_INFO","Variação em relação ao preço médio das minhas stocks: "+percVarMedUnit);

                if(percVar < 0){
                    t.get(i).buyInSeq = false;
                    Log.i("STOCK_INFO"," Queda de : "+percVar+ "% objetivo: -"+percToBuy+"%");
                    if((percVar*(-1)) >= percToBuy && buyStatus == true){
                        if(((totalMoney-totalMoneyEarned) + (currPrice*stockNumberForOpen)) < limitToInvest) {
                            if (t.get(i).priceDownSeqNumber < 5 && t.get(i).number < 25) {

                                //if(t.get(i).name.equals("VIIA3F")){
                                    UiObject buy = mDevice.findObject(new UiSelector().text("COMPRA"));

                                    if(buy.exists()){
                                        buy.clickAndWaitForNewWindow();
                                        UiObject qtd = mDevice.findObject(new UiSelector().text("Quantidade"));
                                        while(!qtd.exists())
                                            Thread.sleep(100);

                                        UiObject stockNum = mDevice.findObject(new UiSelector().text("1"));
                                        if(stockNum.exists())
                                            stockNum.setText(String.valueOf(stockNumberForOpen));
                                        Thread.sleep(500);

                                        UiObject buyEnd = mDevice.findObject(new UiSelector().text("Comprar"));
                                        Log.i("STOCK_INFO", "Checando compra: "+ price);
                                        UiObject checkValue = mDevice.findObject(new UiSelector().text(price));
                                        if(buyEnd.exists() && checkValue.exists()) {
                                            Log.i("STOCK_INFO", "Preço não alterou, compra realizada: "+checkValue.getText());
                                            //buyEnd.clickAndWaitForNewWindow();
                                        }else{
                                            Log.i("STOCK_INFO", "Erro");
                                        }
                                        Thread.sleep(1000);
                                        //mDevice.pressBack();
                                        mDevice.pressBack();
                                    }

                                //}

                                Log.i("STOCK_INFO", "---Compra " + t.get(i).name + " porcentagem queda = " + percVar + " value: " + (currPrice * stockNumberForOpen));
                                Log.i("STOCK_INFO", "Preço médio unitario antes da compra: " + t.get(i).unitPriceMed);
                                t.get(i).unitPriceMed = ((t.get(i).unitPriceMed * t.get(i).number) + (currPrice * stockNumberForOpen)) / (t.get(i).number + stockNumberForOpen);
                                Log.i("STOCK_INFO", "Preço médio unitario depois da compra: " + t.get(i).unitPriceMed);
                                t.get(i).number = (int) (t.get(i).number + stockNumberForOpen);
                                totalMoney = totalMoney + (currPrice * stockNumberForOpen);
                                tax = tax + ((currPrice * stockNumberForOpen) * 0.0325F) / 100;
                            } else {
                                Log.e("STOCK_INFO", "Stock  " + t.get(i).name + "com queda sequencial (5) de preço ou limite de cotas atingido (25) : " + t.get(i).priceDownSeqNumber+" / "+t.get(i).number);
                            }
                        }else{
                            Log.i("STOCK_INFO","Limite seria ultrapassado: "+((totalMoney-totalMoneyEarned) + (currPrice*stockNumberForOpen)) +"/"+limitToInvest);
                        }
                    }else{
                        Log.i("STOCK_INFO"," Não atendeu objetivos - Queda de "+percVar+ "% objetivo: -"+percToBuy+"%");
                    }
                }else if (percVarMedUnit >= percToSell && t.get(i).number > 0) {

                    //if(t.get(i).name.equals("VIIA3F")){
                        UiObject sell = mDevice.findObject(new UiSelector().text("VENDA"));

                        if(sell.exists()){
                            sell.clickAndWaitForNewWindow();
                            UiObject qtd = mDevice.findObject(new UiSelector().text("Quantidade"));
                            while(!qtd.exists())
                                Thread.sleep(500);

                            UiObject stockNum = mDevice.findObject(new UiSelector().text("1"));
                            if(stockNum.exists())
                                stockNum.setText(String.valueOf(t.get(i).number));
                            Thread.sleep(500);
                            UiObject sellEnd = mDevice.findObject(new UiSelector().text("Vender"));
                            Log.i("STOCK_INFO", "Checando venda: "+ price);
                            UiObject checkValue = mDevice.findObject(new UiSelector().text(price));

                            if(sellEnd.exists() && checkValue.exists()){
                                //sellEnd.clickAndWaitForNewWindow();
                                Log.i("STOCK_INFO", "Preço não alterou, venda realizada: "+checkValue.getText());
                            }else {
                                Log.i("STOCK_INFO", "erro");
                            }

                            Thread.sleep(1000);
                            //mDevice.pressBack();
                            mDevice.pressBack();
                        }

                    //}

                    Log.i("STOCK_INFO", "---Venda " + t.get(i).name + "perc = " + percVar + " value: " + (currPrice * t.get(i).number));
                    t.get(i).profit = t.get(i).profit + (currPrice * t.get(i).number) - ( t.get(i).unitPriceMed * t.get(i).number);
                    Log.i("STOCK_INFO", "Lucro com a stock: " + t.get(i).profit);
                    totalMoneyEarned = totalMoneyEarned + (currPrice * t.get(i).number);
                    tax = tax + ((currPrice * t.get(i).number)*0.0325F)/100;
                    t.get(i).number = 0;
                    t.get(i).unitPriceMed = 0;
                    Log.i("STOCK_INFO","Total comprado até o momento: "+ totalMoney);
                    totalProfit = totalProfit + t.get(i).profit ;

                }else{
                    Log.i("STOCK_INFO"," Preço em Alta: "+percVar+ "% objetivo: +"+percToSell+"%");
                    Log.i("STOCK_INFO","-- NENHUMA OPERAÇÃO --");
                }
                if (percVar <0){
                    t.get(i).priceDownSeqNumber = t.get(i).priceDownSeqNumber++;
                    t.get(i).priceUpSeqNumber=0;
                }else{
                    t.get(i).priceDownSeqNumber = 0;
                    t.get(i).priceUpSeqNumber = t.get(i).priceUpSeqNumber++;
                }

                if (LocalDateTime.now().getHour() == 16 && LocalDateTime.now().getMinute() > 30) {
                    Log.i("STOCK_INFO","Parando de comprar e dimunuindo porcentagem de venda");
                    buyStatus = false;
                    percToSell = 0.1F;
                }

                if (LocalDateTime.now().getHour() == 17) {
                    Log.i("STOCK_INFO","Diminuindo porcentagem para venda");
                    buyStatus = false;
                    percToSell = 0.05F;
                }

                t.get(i).lastPrice = currPrice;

                mDevice.pressBack();

                String filToEndName = "/data/local/tmp/end.txt";
                File fileToEnd = new File(filToEndName);
                if(fileToEnd.exists())
                    System.exit(0);

                Thread.sleep(2000);
                mDevice.swipe(540,660,540,1800,2);
            }

            testLoop++;
        }
        Log.i("STOCK_INFO","FIM");
    }
}

class Stock{
    String name;
    float lastPrice;
    int number;
    float totalValue;
    float unitPriceMed;
    int priceUpSeqNumber;
    int priceDownSeqNumber;
    boolean buyInSeq;
    float profit;

    public Stock(String pName, int pNumber, float pUnitPriceMed){
        this.name = pName;
        this.unitPriceMed = pUnitPriceMed;
        this.lastPrice = 0;
        this.totalValue = 0;
        this.number = pNumber;
        this.priceUpSeqNumber = 0;
        this.priceDownSeqNumber = 0;
        this.buyInSeq = false;
        this.profit = 0;
    }
}