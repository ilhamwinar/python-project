import numpy as np
import cv2
import sqlite3
import keyboard

cap = cv2.VideoCapture('KM13.mp4')
con = sqlite3.connect('line.db')
cur = con.cursor()
print("Database telah dibuat dan berhasil terkoneksi ke SQLite")
preview = None
initialPoint = (-1, -1)
list_linex=[]
list_liney=[]
initial_point=[]
flag=0
counter=0

# mouse callback
def drawLine(event,x,y,flags,param):
    global initialPoint,img, preview,flag,counter
    if event == cv2.EVENT_LBUTTONDOWN:
        initialPoint = (x,y)
        preview = img.copy()
        cv2.line(preview, initialPoint, (x,y), (0,255,0), 1)
        list_liney.append(y)
        initial_point.append(initialPoint)
        flag=1
    elif event == cv2.EVENT_MOUSEMOVE:
        if preview is not None:
            preview = img.copy()
            cv2.line(preview, initialPoint, (x,y), (0,255,0), 1)

    elif event == cv2.EVENT_LBUTTONUP:
        if preview is not None:
            preview = None
            cv2.line(img, initialPoint, (x,y), (255,0,0), 1)   
            list_linex.append(x)
            flag=1
            counter=counter+1
    
    if flag==1:
        try:
            print("initial point: "+str(initial_point[0])+" Sumbu X: "+str(list_linex[0])+" Sumbu Y: "+str(list_liney[0]))
            cur.execute("INSERT INTO linecam (id,initial_point,sumbux,sumbuy) VALUES (?,?, ?, ?)", (counter,str(initial_point[0]),list_linex[0],list_liney[0]))
            con.commit()
            print("success")
        except:
            pass    
       
        flag=0
        if len(initial_point)>=1 and len(list_linex)>=1 and len(list_liney)>=1:
            initial_point.clear()
            list_linex.clear()
            list_liney.clear()


if (cap.isOpened()== False): 
    print("Error opening video stream or file")   
scale_percent=100

while True:
    ret, frame = cap.read()
    ## change resolution
    # new_h = int(frame.shape[0] * 80/53)
    # new_w = int(frame.shape[1] * 20/39)
    # frame = cv2.resize(frame, (new_w, new_h))
    print('Resolution: ' + str(frame.shape[0]) + ' x ' + str(frame.shape[1]))
    

    cv2.imshow("image", frame)
    if not ret:
        break
    k = cv2.waitKey(1)
    if k%256 == 27:
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        img=frame
        break


             
cv2.namedWindow("image")
while (True):
    row = cur.execute('''SELECT count(id) FROM linecam''')
    for i in row:
        daftar=list(i)
    print(daftar)
    if daftar[0]<2:
        cv2.setMouseCallback("image", drawLine)
    elif daftar[0]>=2 :
        print("Data Penuh")
        if keyboard.is_pressed('r'):
            sql = 'DELETE FROM linecam'
            cur = con.cursor()
            cur.execute(sql)
            con.commit()
            print("berhasil hapus database")
            continue
    if preview is None:
      cv2.imshow('image',img)
    else :
      cv2.imshow('image',preview)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
      break

cv2.destroyAllWindows()