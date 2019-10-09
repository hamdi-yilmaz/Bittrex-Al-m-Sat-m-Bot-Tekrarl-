from __future__ import division
import numpy
from bittrex.bittrex import Bittrex
from datetime import datetime
import sqlite3
from time import sleep
import os


my_bittrex = Bittrex("",
                     "")

databaseName= 'C:\\Users\\hh\\Desktop\\PycharmProjects 01092018\\08_gun_bot\\Bittrex\\emir_takip.db'



def baz_market_sec():
    baz_market = raw_input("Baz market secin (varsayilan BTC ) (USDT  -  BTC)") or "BTC"
    
    return (baz_market + "-").upper()

def market_sec(baz_market):
    market = raw_input("Hangi altcoin islemi yapilacak !!!! Baz " + baz_market + "!!!!! (SC, ETH, DGB, ... ) : ")
    return baz_market + market.upper()

def islem_turu():
    while True:
        tur = raw_input("Alim (a) / Satim (s)  (varsayilan 'a'): ") or "a"  # alim / satim turu
        if tur == 'a' or tur == 's':
            break
        else:
            print ("yanlis bir secim yaptiniz")
            continue
    return tur

def alim_miktari_belirle(baz_market):
    if baz_market == "BTC-" :
        alim_miktari = float(raw_input(baz_market + "bazinda islem miktari (Kullanilabilir: )(En dusuk 0.0006(varsayilan)): ") or 0.0006)
        
    elif baz_market== "USDT-":
        alim_miktari = float(raw_input(baz_market + "bazinda islem miktari (Kullanilabilir: )(En dusuk 5(varsayilan)): ") or 5)
    else:
        print ("baz market seciminde hata olustu")
    return alim_miktari

def max_islem_sayisi_belirle(alim_miktari, baz_market):
    if baz_market== "BTC-":
        max_islem_sayisi = alim_miktari / 0.0006
    elif baz_market== "USDT-":
        max_islem_sayisi = alim_miktari / 5
    else:
        print ("Max islem sayisi belirlenirken hata olustu")
    return max_islem_sayisi

def islem_fiyati(tur, currencyPair, tip):
    if tur == 'a':
        while True:
            maksimum = my_bittrex.get_ticker(currencyPair)['result']['Bid']                        #alim defterindeki max rakami alir
            print ("                                             %.8f" % maksimum)
            islem_fiyati = float(raw_input("Islem fiatini "+tip+" limiti (max: %.8f): "% maksimum) or maksimum)
            if islem_fiyati > float(maksimum):
                print ("Hata. Maksimum degerden fazla oldu. Maks:   %.8f" % maksimum)
                continue
            else:
                return islem_fiyati


    if tur == 's':
        while True:
            minimum =  my_bittrex.get_ticker(currencyPair)['result']['Ask']                      # satim defterinde en kucuk deger
            print ("                                             %.8f" % minimum)
            islem_fiyati = float(raw_input("Islem fiatini "+tip+" limiti (min: %.8f):  " % minimum) or minimum)
            if islem_fiyati < float(minimum):
                print("Hata. Minimum degerden daha dusuk oldu. Min: %.8f" % minimum )
                continue
            else:
                return islem_fiyati

def database_kayit_buy(borsa, market, time, kazanc_orani, order_number, price, amount, tekrar_sayisi):
    with sqlite3.connect(databaseName) as db:
        cursor = db.cursor()
        sql = "insert into Sirali_Emirler (BORSA, MARKET, TIME, KAZANC_ORANI, BUY_ORDER_NUMBER, BUY_PRICE, BUY_AMOUNT, STATUS, TEKRAR) values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (borsa, market, time, kazanc_orani, order_number, price, amount, 'Alim_emri_verildi', tekrar_sayisi))
        db.commit()

def database_kayit_sell(borsa, market, time, kazanc_orani, order_number, price, amount, tekrar_sayisi):
    with sqlite3.connect(databaseName) as db:
        cursor = db.cursor()
        sql = "insert into Sirali_Emirler (BORSA, MARKET, TIME, KAZANC_ORANI, SELL_ORDER_NUMBER, SELL_PRICE, SELL_AMOUNT, STATUS, TEKRAR) values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (borsa, market, time, kazanc_orani, order_number, price, amount, 'Satim_emri_verildi', tekrar_sayisi))
        db.commit()

def main():
    print ('-------------------- Bittrex Tekrarli Alim Satim Botu --------------------')
    print ("- Sadece bittrex borsasinda kullanilir.")
    print ('- Yeni otomatik emir verilmesini saglar.')
    print ('- Otomatik emir verilmesi icin kontrol.py calisir halde olmalidir.')

    # borsa = raw_input("Islam yapilacak borsayi secin (Poloniex (p) / Bittrex (b) ) : ")

    baz_market = baz_market_sec()
    market = market_sec( baz_market )
    islemTuru = islem_turu()

    # en dusuk ve en buyuk degerler alinarak islem araligi tespit edilir. Alim ve satima gore minimum maksimum deger
    #kontrolu yapilir.

    islem_fiyati_ust = islem_fiyati(islemTuru, market , 'ust')
    while True:
        islem_fiyati_alt = islem_fiyati(islemTuru, market , 'alt')
        if islem_fiyati_ust >= islem_fiyati_alt:
            break
        else:
            print("Alt degeri ust degerden daha dusuk veya esit belirlemelisiniz.")
            continue

    # kullanilabilir miktari alim ve satimda farkli olacak
    alim_miktari = alim_miktari_belirle(baz_market)

    max_islem_sayisi = max_islem_sayisi_belirle(alim_miktari , baz_market)   
    print("!!!!!!! Sadece 1 islem yapilacaksa kucuk degeri kullanir, tekrar ile karistirma!!!!!!!")
    islem_sayisi = int(raw_input("Emir kac parca olacak? (En fazla "+ str(int(max_islem_sayisi)) +" (varsayilan)) : ") or max_islem_sayisi)

    tekrar_sayisi = int(raw_input("Kac tekrar olacak? ((varsayilan 10)) : ") or 10)
    


    if islem_fiyati_alt >=  0.00000125:
        kazanc_orani_default = 0.8
    else:
        kazanc_orani_default= (0.000001 / islem_fiyati_alt) + 0.1

    while True:
        kazanc_orani = float(raw_input("Kazanc orani yuzde olarak (En dusuk " + str(kazanc_orani_default) +  "(varsayilan)): ") or kazanc_orani_default)
        if kazanc_orani >= kazanc_orani_default:
            break
        else:
            print(str(kazanc_orani_default)+ ' den dusuk yazamazsiniz.')


    fiyatlar = numpy.linspace(islem_fiyati_alt, islem_fiyati_ust, islem_sayisi)


    for x in fiyatlar:
        x= float("{0:.8f}".format(x))
        amount = (alim_miktari / islem_sayisi) / x     #x = fiyat bu hesaplama ile btc miktarini coine cevirdi
        if islemTuru == 'a':                          # eger alim islemi secildi ise
            results = my_bittrex.buy_limit(market, amount, x)

            database_kayit_buy('Bittrex', market, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                kazanc_orani, results['result']['uuid'], x, amount, tekrar_sayisi)
            print results

        if islemTuru == 's':                           # satim secili ise
            # results = polo.sell(market, x, amount)
            results = my_bittrex.sell_limit(market, amount, x)
            
            database_kayit_sell('Bittrex', market, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                kazanc_orani, results['result']['uuid'], x, amount, tekrar_sayisi)
            print results
        sleep(1)





if __name__ == "__main__":
    main()