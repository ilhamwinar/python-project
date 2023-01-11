from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import ast
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import sqlite3
import logging
import time


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)

con = sqlite3.connect('cctv.db')
cur = con.cursor()
logging.info("KONEKSI DATABASE BERHASIL")
#variable declaration
app = FastAPI()
security = HTTPBasic()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

f = open('./temp.txt', 'r')
api=f.read()
dictapi = ast.literal_eval(api)
id_cctv=dictapi['id']
id_cctv_temp=id_cctv
g = open('./config.txt', 'r')
ip_api=g.read()
dictip = ast.literal_eval(ip_api)
ip_jetson=dictip['ip']

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username
    correct_username_bytes = "$2b$12$EZxJr9jH9UzeCUJ3Gz/NAOS1GWpY3RloaopyuK7lRhPSROONEN6uS"
    is_correct_username=verify_password(current_username_bytes, correct_username_bytes)
    current_password_bytes = credentials.password
    correct_password_bytes = "$2b$12$/TvmToFip27Gqnnv7xfareDeHD6MWp3J1sVn00joiTaR2vn/eT7Q2"
    is_correct_password=verify_password(current_password_bytes, correct_password_bytes) 
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/cctv/{id_cctv}")
async def read_current_user(id_cctv,username: str = Depends(get_current_username)):
    if id_cctv_temp != id_cctv:
        raise HTTPException(status_code=400, detail="Wrong CCTV Location") 
 
    z={}
    time.sleep(500/1000)
    try:
        row = cur.execute(''' SELECT TIME, SUM(TOTAL_KR_DOWN) AS TOTAL_KR_DOWN ,SUM(BUS_DOWN) AS BUS_DOWN ,SUM(CAR_DOWN) AS CAR_DOWN,SUM(TRUCK_DOWN) AS TRUCK_DOWN,
            SUM(TOTAL_KR_UP) AS TOTAL_KR_UP ,SUM(BUS_UP) AS BUS_UP ,SUM(CAR_UP) AS CAR_UP,SUM(TRUCK_UP) AS TRUCK_UP FROM (SELECT TIME, SUM(TOTAL_KR_DOWN) AS TOTAL_KR_DOWN ,
            SUM(BUS_DOWN) AS BUS_DOWN,SUM(CAR_DOWN) AS CAR_DOWN,SUM(TRUCK_DOWN) AS TRUCK_DOWN,SUM(TOTAL_KR_UP) AS TOTAL_KR_UP ,SUM(BUS_UP) AS BUS_UP ,SUM(CAR_UP) AS CAR_UP,
            SUM(TRUCK_UP) AS TRUCK_UP FROM aicctv  GROUP BY TIME ORDER BY TIME DESC LIMIT 5); ''')
    except sqlite3.Error as err:
            logging.error("ERROR: "+str(err))

    for i in row:
        time_cctv=i[0]
        total_kr_down=i[1]
        Bus_down=i[2]
        car_down=i[3]
        truck_down=i[4]
        total_kr_up=i[5]
        Bus_up=i[6]
        car_up=i[7]
        truck_up=i[8]
        
    z.update({"total_kr_down": total_kr_down})
    z.update({"Bus_down": Bus_down})
    z.update({"car_down": car_down})
    z.update({"truck_down": truck_down})
    z.update({"total_kr_up": total_kr_up})
    z.update({"Bus_up": Bus_up})
    z.update({"car_up": car_up})
    z.update({"truck_up": truck_up})  
    z.update({"id": id_cctv})
    z.update({"time": time_cctv})
    
    logging.info("SESUDAH DIKALKULASI: "+str(z))

    return z

if __name__ == "__main__":

    
   uvicorn.run("test:app", host=ip_jetson, port=90,log_level="info",reload=True)
