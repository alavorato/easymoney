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

        float percToBuy = -0.1F;
        float percToSell = 0.1F;
        int stockNumberForOpen = 5;
        boolean buyStatus = true;
        int testLoop = 0;
        float totalMoney = 0;
        float totalMoneyEarned = 0;
        float totalProfit = 0;
        float limitToInvest = 2000.0F;
        float tax = 0;
        UiDevice mDevice = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        ArrayList<Stock> t = new ArrayList<>();
        String day = LocalDateTime.now().getYear() + "-" + LocalDateTime.now().getMonth().getValue() + "-" + LocalDateTime.now().getDayOfMonth();
        Log.i("STOCK_INFO", "Data: " + day);


        t.add(new Stock("CPFE3F", 0, 0));
        t.add(new Stock("ABEV3F", 0, 0));
        t.add(new Stock("CSMG3F", 0, 0));
        t.add(new Stock("CSNA3F", 0, 0));
        t.add(new Stock("ELET3F", 0, 0));
        t.add(new Stock("PETR3F", 0, 0));
        t.add(new Stock("BMGB4F", 0, 0));
        t.add(new Stock("BBDC3F", 0, 0));
        t.add(new Stock("GGBR3F", 0, 0));
        t.add(new Stock("TAEE3F", 0, 0));


        UiScrollable appViews2 = new UiScrollable(new UiSelector().scrollable(true));
        appViews2.setAsVerticalList();

        while (testLoop < 1000000) {
            for (int i = 0; i < t.size(); i++) {

                UiObject noInternet = mDevice.findObject(new UiSelector().textContains("Sem conexão"));
                UiObject serverError = mDevice.findObject(new UiSelector().textContains("Falha de comunicação"));

                if (noInternet.exists() || serverError.exists()) {
                    Log.i("STOCK_INFO", "Sem internet ou falha do servidor");
                    Thread.sleep(10000);
                    continue;
                }
                appViews2.scrollIntoView(new UiSelector().text(t.get(i).name));

                UiObject stockSelected = mDevice.findObject(new UiSelector().text(t.get(i).name));
                if (stockSelected.exists())
                    stockSelected.clickAndWaitForNewWindow();
                else
                    continue;

                UiObject stockValueSell = mDevice.findObject(new UiSelector().descriptionContains("AskPriceLbl_Container"));
                UiObject stockValueBuy = mDevice.findObject(new UiSelector().descriptionContains("BidPriceLbl_Container"));

                try{
                    float currPriceSell = Float.parseFloat(stockValueSell.getChild(new UiSelector().index(0)).getText().replace("R$ ", "").replace(",", "."));
                    float currPriceBuy = Float.parseFloat(stockValueBuy.getChild(new UiSelector().index(0)).getText().replace("R$ ", "").replace(",", "."));

                    Log.i("STOCK_INFO", "Stock: " + t.get(i).name + " SellPrice: " + currPriceSell +" BuyPrice: "+currPriceBuy);
                    //porcentagem de variacao de uma leitura para outra em relacão a preço
                    float percVarBuy = (currPriceBuy - t.get(i).lastPriceBuy) * 100 / t.get(i).lastPriceBuy;
                    float percVarSell = (currPriceSell - t.get(i).lastPriceSell) * 100 / t.get(i).lastPriceSell;
                    float percVarMedUnit = 0;

                    //porcentagem de variacao de uma leitura para outra em relacão a média de preço por unidade
                    if (t.get(i).unitPriceMed > 0) {
                        percVarMedUnit = (currPriceSell - t.get(i).unitPriceMed) * 100 / t.get(i).unitPriceMed;
                    }

                    Log.i("STOCK_INFO", "Stock: " + t.get(i).name +" Valor atual Compra: " + currPriceBuy + " valor anterior: " + t.get(i).lastPriceBuy);
                    Log.i("STOCK_INFO", "Stock: " + t.get(i).name +" Valor atual Venda: " + currPriceSell + " valor anterior: " + t.get(i).lastPriceSell);

                    if(percVarBuy < percToBuy){
                        Log.i("STOCK_INFO", "Stock: " + t.get(i).name + " COMPRA REALIZADA");
                        t.get(i).totalValue = t.get(i).totalValue + currPriceBuy * stockNumberForOpen;
                        Log.i("STOCK_INFO", "total: " + t.get(i).totalValue + " / " + (t.get(i).number+stockNumberForOpen));
                        t.get(i).unitPriceMed = ((t.get(i).unitPriceMed * t.get(i).number) + (currPriceBuy * stockNumberForOpen)) / (t.get(i).number + stockNumberForOpen);
                        Log.i("STOCK_INFO", "media de preço por stock: " + t.get(i).unitPriceMed);
                        t.get(i).number = t.get(i).number + stockNumberForOpen;

                    }

                    if(percVarMedUnit >= percToSell && t.get(i).number>0){
                        Log.i("STOCK_INFO", "Stock: " + t.get(i).name + " VENDA REALIZADA");
                        t.get(i).profit = t.get(i).profit + ((currPriceSell * t.get(i).number) - t.get(i).totalValue);
                        Log.i("STOCK_INFO", "profit: " + t.get(i).profit );
                        t.get(i).number = 0;
                    }
                    t.get(i).lastPriceSell = currPriceSell;
                    t.get(i).lastPriceBuy= currPriceBuy;

                    mDevice.pressBack();

                }catch (Exception e){
                    Log.i("STOCK_INFO", "Stock: " + t.get(i).name +" SOME ERROR TO READ PRICE");
                    mDevice.pressBack();
                    continue;
                }


                Thread.sleep(2000);
                mDevice.swipe(540, 660, 540, 1800, 2);
            }
            Log.i("STOCK_INFO", "Leitura: "+testLoop);
            testLoop++;
        }
        Log.i("STOCK_INFO", "FIM");
    }
}

class Stock {
    String name;
    float lastPriceSell;
    float lastPriceBuy;
    int number;
    float totalValue;
    float unitPriceMed;
    int priceUpSeqNumber;
    int priceDownSeqNumber;
    boolean buyInSeq;
    float profit;

    public Stock(String pName, int pNumber, float pUnitPriceMed) {
        this.name = pName;
        this.unitPriceMed = pUnitPriceMed;
        this.lastPriceSell = 0;
        this.lastPriceBuy = 0;
        this.totalValue = 0;
        this.number = pNumber;
        this.priceUpSeqNumber = 0;
        this.priceDownSeqNumber = 0;
        this.buyInSeq = false;
        this.profit = 0;
    }
}