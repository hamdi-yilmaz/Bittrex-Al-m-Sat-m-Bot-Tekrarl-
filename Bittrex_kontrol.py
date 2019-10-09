from __future__ import print_function
from __future__ import division
import numpy
from bittrex.bittrex import Bittrex
from datetime import datetime
import sqlite3
from time import sleep


                                                                
my_bittrex = Bittrex("",
                     "")                                                                                           # bittrex api keys

databaseName= 'C:\\Users\\hh\\Desktop\\PycharmProjects 01092018\\08_gun_bot\\Bittrex\\emir_takip.db'                # database uzantisi
bekleme_suresi = 600                                                                                                # islemler arasi bekleme suresi.

def database_kayit_ikincil_emir(tipi, order_number, ikincil_order_number, amount, fiyat):

    if tipi == 'buy':
        with sqlite3.connect(databaseName) as db:
            cursor = db.cursor()
            cursor.execute('''UPDATE Sirali_Emirler 
                            SET STATUS = 'ikincil_alim_emri_verildi', 
                            BUY_ORDER_NUMBER = ? ,
                            BUY_AMOUNT = ?,
                            BUY_PRICE = ?,
                            TIME_ikinci = ?
                            WHERE SELL_ORDER_NUMBER = ? ''',
                           (ikincil_order_number,amount,fiyat, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),order_number))
            db.commit()
    elif tipi == 'sell':
        with sqlite3.connect(databaseName) as db:
            cursor = db.cursor()
            cursor.execute('''UPDATE Sirali_Emirler 
                            SET STATUS = 'ikincil_satim_emri_verildi', 
                            SELL_ORDER_NUMBER = ? ,
                            SELL_AMOUNT = ?,
                            SELL_PRICE = ?,
                            TIME_ikinci = ?
                            WHERE BUY_ORDER_NUMBER = ?''',
                           (ikincil_order_number, amount, fiyat, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),order_number))
            db.commit()


def database_kayit_iptal(order_number):
    with sqlite3.connect(databaseName) as db:
        cursor = db.cursor()
        cursor.execute('''UPDATE Sirali_Emirler SET STATUS = 'iptal_edilmis' WHERE SELL_ORDER_NUMBER = ? OR BUY_ORDER_NUMBER = ?''',
                       (order_number, order_number))
        db.commit()

def database_kayit_tekrar_sifirla(order_number):
    with sqlite3.connect(databaseName) as db:
        cursor = db.cursor()
        cursor.execute('''UPDATE Sirali_Emirler SET TEKRAR = 0 WHERE SELL_ORDER_NUMBER = ? OR BUY_ORDER_NUMBER = ?''',
                       (order_number, order_number))
        db.commit()

def database_kayit_tamam_satis(order_number):                       #ikincil emri satis olan tamamlandi
    with sqlite3.connect(databaseName) as db:
        cursor = db.cursor()
        cursor.execute('''UPDATE Sirali_Emirler SET STATUS = 'satis_tamamlandi' WHERE SELL_ORDER_NUMBER = ? OR BUY_ORDER_NUMBER = ?''',
                       (order_number, order_number))
        db.commit()

def database_kayit_tamam_alis(order_number):                        # ikincil emri alis olan tamamlandi
    with sqlite3.connect(databaseName) as db:
        cursor = db.cursor()
        cursor.execute('''UPDATE Sirali_Emirler SET STATUS = 'alis_tamamlandi' WHERE SELL_ORDER_NUMBER = ? OR BUY_ORDER_NUMBER = ?''',
                       (order_number, order_number))
        db.commit()


def db_baglan(durum):
    if durum == 'Satim_emri_verildi':
        conn = sqlite3.connect(databaseName)
        cursor = conn.execute("SELECT MARKET, KAZANC_ORANI, STATUS, SELL_ORDER_NUMBER, SELL_PRICE, SELL_AMOUNT "
                              "FROM Sirali_Emirler "
                              "WHERE STATUS == ? ", (durum,)
                              )
        veri = cursor.fetchall()
        conn.close()
        return veri

    elif durum == 'Alim_emri_verildi':
        conn = sqlite3.connect(databaseName)
        cursor = conn.execute("SELECT MARKET, KAZANC_ORANI, STATUS, BUY_ORDER_NUMBER, BUY_PRICE, BUY_AMOUNT "
                              "FROM Sirali_Emirler "
                              "WHERE STATUS == ?  ", (durum,)
                              )
        veri = cursor.fetchall()
        conn.close()
        return veri

    elif durum == 'ikincil_alim_emri_verildi':
        conn = sqlite3.connect(databaseName)
        cursor = conn.execute("SELECT MARKET, STATUS, BUY_ORDER_NUMBER "
                              "FROM Sirali_Emirler "
                              "WHERE STATUS == ?  ", (durum,)
                              )
        veri = cursor.fetchall()
        conn.close()
        return veri

    elif durum == 'ikincil_satim_emri_verildi':
        conn = sqlite3.connect(databaseName)
        cursor = conn.execute("SELECT MARKET, STATUS, SELL_ORDER_NUMBER "
                              "FROM Sirali_Emirler "
                              "WHERE STATUS == ?  ", (durum,)
                              )
        veri = cursor.fetchall()
        conn.close()
        return veri

    elif durum == 'satis_tamamlandi':
        conn = sqlite3.connect(databaseName)
        cursor = conn.execute("SELECT MARKET, KAZANC_ORANI, BUY_PRICE, BUY_AMOUNT, TEKRAR, BUY_ORDER_NUMBER "
                              "FROM Sirali_Emirler "
                              "WHERE STATUS == ? AND TEKRAR > 0 ", (durum,)
                              )
        veri = cursor.fetchall()
        conn.close()
        return veri

    elif durum == 'alis_tamamlandi':
        conn = sqlite3.connect(databaseName)
        cursor = conn.execute("SELECT MARKET, KAZANC_ORANI, SELL_PRICE, SELL_AMOUNT, TEKRAR, BUY_ORDER_NUMBER "
                              "FROM Sirali_Emirler "
                              "WHERE STATUS == ? AND TEKRAR > 0 ", (durum,)
                              )
        veri = cursor.fetchall()
        conn.close()
        return veri


# diger taraftan gun_bot icin
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



# Emirin son durumu kontorl edilir. Bunun ici ayrica sorgu yok.
def emir_durum_kontrolu(order_number):
    kontrol = my_bittrex.get_order(order_number)
    if kontrol['result']['IsOpen'] == True:
        return 0                                                                                                                        # 0 >>> emir bekliyor
    elif kontrol['result']['QuantityRemaining'] == kontrol['result']['Quantity']:
        database_kayit_iptal(order_number)
        print(order_number, 'Iptal edilmis')
        return 1                                                                                                                        # 1 >>> emir iptal edilmis
    elif kontrol['result']['QuantityRemaining'] == 0:
        print(str(kontrol['result']['Exchange']) + '\t' + str(kontrol['result']['Type']) + '\t' + str(kontrol['result']['Price'])  )
        print(order_number, 'Emir gerceklesti')
        return 2                                                                                                                        # 2 >>> emir tamamlanmis
    else:
        return 3                                                                                                                        # 3 >>> mala bagladiginda bunu dondurecek


def satim_emri_tara():
    veri = db_baglan('Satim_emri_verildi')
    for x in veri:
        market      = x[0]
        oran        = x[1]
        order_number = x[3]
        fiyat       = x[4] * (100 - oran)/100
        fiyat       = float("{0:.8f}".format(fiyat))
        amount      = x[5] * 1.005

        if emir_durum_kontrolu(order_number) == 2:
                ikincil_order = my_bittrex.buy_limit(market, amount, fiyat)
                print ('Ikincil alim emri verildi - '+ str(ikincil_order['result']['uuid']) + '\t' + market + '\t' + str(fiyat) + '\t' + str(amount) )
                print ('----------------------------------------')
                database_kayit_ikincil_emir('buy', order_number , ikincil_order['result']['uuid'] , amount ,fiyat)

def alim_emri_tara():
    veri = db_baglan('Alim_emri_verildi')
    for x in veri:
        market      = x[0]
        oran        = x[1]
        order_number = x[3]
        fiyat       = x[4] * (100 + oran)/100
        fiyat       = float("{0:.8f}".format(fiyat))
        amount      = x[5] * 0.995

        if emir_durum_kontrolu(order_number) == 2:
                ikincil_order = my_bittrex.sell_limit(market, amount, fiyat)
                print ('Ikincil satim emri verildi - '+ str(ikincil_order['result']['uuid']) + '\t' + market + '\t' + str(fiyat) + '\t' + str(amount) )
                print ('----------------------------------------')
                database_kayit_ikincil_emir('sell', order_number , ikincil_order['result']['uuid'] , amount ,fiyat)

def ikincil_emirler_tara():
    veri1 = db_baglan('ikincil_alim_emri_verildi')
    for x in veri1:
        order_number = x[2]
        if emir_durum_kontrolu(order_number) == 2:
            print ("Ikincil alim tamamlandi")
            print ("----------------------------------------")
            database_kayit_tamam_alis(order_number)

    veri2 = db_baglan('ikincil_satim_emri_verildi')         # daha sonra veri1 + veri2 denenecek
    for y in veri2:
        order_number = y[2]
        if emir_durum_kontrolu(order_number) == 2:
            print ("Ikincil satim tamamlandi")
            print ("----------------------------------------")
            database_kayit_tamam_satis(order_number)


######################## Tekrar islemleri  ##########################

def gun_bot_alis():
    veri = db_baglan('satis_tamamlandi')                    # yeni alis emri girilecek. eski tekrar 0 olacak
    for x in veri:
        market          = x[0]
        kazanc_orani    = x[1]
        fiyat           = x[2] 
        amount          = x[3] 
        tekrar_sayisi   = x[4]
        buy_order_number = x[5]

        if tekrar_sayisi > 0:
                tekrar_sayisi = tekrar_sayisi - 1
                results = my_bittrex.buy_limit(market, amount, fiyat)
                database_kayit_buy('Bittrex', market, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        kazanc_orani, results['result']['uuid'], fiyat, amount, tekrar_sayisi)
                print ("Alim emri verildi")
                print (results)
                print ("----------------------------------------")
                database_kayit_tekrar_sifirla(buy_order_number)
                sleep(1)


def gun_bot_satis():                                        # yeni satis emri girilecek. eski tekrar 0 olacak
    veri = db_baglan('alis_tamamlandi')
    for x in veri:
        market          = x[0]
        kazanc_orani    = x[1]
        fiyat           = x[2] 
        amount          = x[3] 
        tekrar_sayisi   = x[4]
        buy_order_number = x[5]
        if tekrar_sayisi > 0:
                tekrar_sayisi = tekrar_sayisi - 1
                results = my_bittrex.sell_limit(market, amount, fiyat)
                database_kayit_sell('Bittrex', market, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        kazanc_orani, results['result']['uuid'], fiyat, amount, tekrar_sayisi)
                print ("Satim emri verildi")
                print (results)
                print ("----------------------------------------")
                database_kayit_tekrar_sifirla(buy_order_number)
                sleep(1)

#######################################################################

def main():
    
    print ('-------------------- Bittrex Tekrarli Alim Satim Botu --------------------')
    print ('- Kayitli alim satim islemleri '+ str(bekleme_suresi) + ' sn sure araliklari ile kontorl edilir.')
    print ('- Alim ve satim islemleri sonucu kazanc orani dikkate alinarak yeni satim-alim emirleri verilir.')
    print ('- Bu islemler tekar sayisi kadar yinelenir.')
    while True:
        satim_emri_tara()
        alim_emri_tara()
        ikincil_emirler_tara()

        gun_bot_alis()
        gun_bot_satis()
        print('.')
        sleep(bekleme_suresi)                  # islemler arasi bekleme suresi.
        

                                    # STATUS: 'Satim_emri_verildi'
                                            # 'Alim_emri_verildi'
                                            # 'iptal_edilmis'
                                            # 'ikincil_alim_emri_verildi'
                                            # 'ikincil_satim_emri_verildi'
                                            # 'tamamlandi'
                                            # 'alis_tamamlandi' durumunda eger tekrar sayisi 0 dan buyukse yeni satis emri verilir
                                            # 'satis_tamamlandi' durumunda eger tekrar sayisi 0 dan buyukse yeni alis emri verilir


if __name__ == "__main__":
    main()
