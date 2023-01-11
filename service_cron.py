import os
import ast
import time
from collections import Counter
from datetime import datetime
import logging
import sqlite3
import pandas as pd

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)
con = sqlite3.connect('cctv.db')
cur = con.cursor()
logging.info("KONEKSI DATABASE BERHASIL")
temp=""
counter=0
# def job():
while True:
    z={}
    time.sleep(20)
    f = open('temp.txt', 'r')
    api=f.read()
    logging.info("temp: "+temp)
    logging.info("api: "+api)
    if temp!=api:
        logging.info("MENAMBAHKAN DATA KE LIST_MINUTES")
        temp=api
        dictapi = ast.literal_eval(api)
        id=dictapi['id']
        dictapi.pop('id')
        dictapi.pop('time')
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d-%m-%Y %H:%M:%S.%f")

        total_kr_down=dictapi['total_kr_down']
        Bus_down=dictapi['Bus_down']
        car_down=dictapi['car_down']
        truck_down=dictapi['truck_down']
        total_kr_up=dictapi['total_kr_up']
        Bus_up=dictapi['Bus_up']
        car_up=dictapi['car_up']
        truck_up=dictapi['truck_up']
        id_location=id
        timestamp=timestampStr

        z.update({"total_kr_down": total_kr_down})
        z.update({"Bus_down": Bus_down})
        z.update({"car_down": car_down})
        z.update({"truck_down": truck_down})
        z.update({"total_kr_up": total_kr_up})
        z.update({"Bus_up": Bus_up})
        z.update({"car_up": car_up})
        z.update({"truck_up": truck_up})

        if sum(z.values())==0:
            logging.error("KONEKSI KE CCTV TERPUTUS")
            os.system("docker restart aicctv")
        else:
            logging.info("CCTV DAN AI RUNNING")

        try:
            cur.execute("INSERT INTO aicctv (ID_LOCATION,TOTAL_KR_DOWN,BUS_DOWN,CAR_DOWN,TRUCK_DOWN,TOTAL_KR_UP,BUS_UP,CAR_UP,TRUCK_UP,TIME) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (id,total_kr_down,Bus_down,car_down,truck_down,total_kr_up,Bus_up,car_up,truck_up,timestamp))
            con.commit()
        except sqlite3.Error as err:
            logging.error("ERROR: "+str(err))
        z.update({"id": id})
        z.update({"time": timestampStr})
        
    else:
        logging.info("DATA TXT MASIH SAMA")
        continue

    




