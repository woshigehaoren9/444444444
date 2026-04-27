from model.connectsqlite import ConnectSqlite
import numpy as np
import cv2
import datetime
con = ConnectSqlite('./database/database.db')

sql = """INSERT INTO face_data VALUES (NULL,  "王五", 1,"[1,2,3]",1003,"2020-11-13","1004");"""
sql2 = """SELECT student_id FROM face_data;"""

student_id = con.return_all_sid()
print(student_id)
print(datetime.datetime.now())

tableDict = {"Monday":[["Machine Lerning",'C-202',"08:00","10:00"],[],[],[]],
                                    "Tuesday":[["Math",'B-201',"08:00","10:00"],[],[],[]],
                                    "Wednesday":[[],[],[],[]],
                                    "Thursday": [[], [], [], []],
                                    "Friday": [[], [], [], []]}

print(list(tableDict.values())[1])


sql = """SELECT student_id,name,face_data FROM face_data;"""

info = con.fetchall_table(sql)
student_info_all = []
for i in info:
    face_data = i[2]
    face_data = list(map(float, face_data.split('\n')))
    print(len(face_data))
    student_info = {'sid':i[0],'name':i[1],'feature':face_data}
    student_info_all.append(student_info)
print(student_info_all)

from PIL import Image
import numpy as np

# 假设当前内存中的img类型为 32x32x3 type为tensor.uint8类型

face_list = con.return_face_photo()
img_pil = Image.fromarray(np.uint8(face_list[-1]))
img_pil.show()
img_pix = img_pil.toqpixmap()  # QPixmap

img_img = img_pil.toqimage()  # QImage

'''
face_list = con.return_face_photo()
print(type(face_list[-1]))
img_new = np.frombuffer(face_list[-1], dtype=np.uint8)
img_new1 = img_new.reshape((480, 640, 3))
cv2.imshow("cs",img_new1)                                            # 在窗口cs中显示图片
cv2.waitKey(0)
cv2.destroyAllWindows()
'''