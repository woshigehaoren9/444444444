#-*- coding:utf-8 -*-
import dlib, os, cv2
import numpy as np

class recognizer:

    # 构造函数，创建实例时应输入2个模型文件带路径的文件名
    def __init__(self, PREDICTOR_PATH, FACE_REC_MODEL_PATH):
        self.detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor(PREDICTOR_PATH)
        self.face_rec_model = dlib.face_recognition_model_v1(FACE_REC_MODEL_PATH)

    # 根据人脸检测结果，计算一张图片中最大的人脸是所有人脸中的第几个
    def getMaxFaceIndex(self, rects):
        maxArea = 0
        maxFaceIndex = 0
        if len(rects) > 1:
            for i, d in enumerate(rects):
                if d.area() > maxArea:
                    maxFaceIndex = i
                    maxArea = d.area()
        return maxFaceIndex

    # 计算图片中指定人脸边框的左上角和右下角的位置
    def getMaxFaceRectangle(self, rects, adjust):

        faceIndex = self.getMaxFaceIndex(rects)

        # 获取最大人脸的方框左上角的位置并向左上角调整一定的位置
        rectangleLT = (rects[faceIndex].left()-adjust, rects[faceIndex].top()-adjust)

        # 获取最大人脸的方框右下角的位置并向右下角调整一定的位置
        rectangleRB = (rects[faceIndex].right()+adjust, rects[faceIndex].bottom()+adjust)
        return (rectangleLT, rectangleRB)

    #根据左上角和右下角的坐标，在照片中画长方形。
    def drawRectangle(self, image, rectangleLT, rectangleRB):
        # 在人脸范围画一个红色的框
        cv2.rectangle(image, rectangleLT, rectangleRB, (255, 0, 0), 2)

    # 在rgb图片中找到最大的脸，并画框
    def drawMaxRectangle(self, image, rects):

        # 根据rects找到最大的人脸，并获取边框左上角和右下角2个点的位置
        rectangleLT, rectangleRB = self.getMaxFaceRectangle(rects, 8)

        # 根据左上角、右下角位置画RGB红色框
        cv2.rectangle(image, rectangleLT, rectangleRB, (255, 225, 0), 2)

    # 计算两个128维向量的"欧式距离"。结果越小表示两者越"像"。
    def featureCompare(self, vectors_1, vectors_2):
        feature_1 = np.array(vectors_1)
        feature_2 = np.array(vectors_2)
        dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
        return dist

    # 获取rgb图片中指定序号人脸的68个定位点
    def _getFaceShapeByIndex(self, rgbImage, rects, index):
        return self.shape_predictor(rgbImage, rects[index])

    # 获取rgb图片中指定序号的人脸特征
    def getFaceFingerprintByIndex(self, rgbImage, rects, index):
        faceShape = self._getFaceShapeByIndex(rgbImage, rects, index)
        return self.face_rec_model.compute_face_descriptor(rgbImage, faceShape)

    # 获取rgb图片中最大人脸的特征，该方法不检测图片中是否存在人脸
    def getMaxFaceFingerprint(self, rects, rgbImage):
        maxIndex = self.getMaxFaceIndex(rects)
        #print('max=', maxIndex)
        face_shape = self.shape_predictor(rgbImage, rects[maxIndex])
        #print('shape:', face_shape)
        face_fingerprint = self.face_rec_model.compute_face_descriptor(rgbImage, face_shape)
        #print('rec compute')
        return face_fingerprint

    # 把人脸特征存为npy文件
    def saveMaxFaceFingerprintToFile(self, maxFaceFingerprint, npyFilePath):
        vectors = np.array([])
        for i, num in enumerate(maxFaceFingerprint):
            vectors = np.append(vectors, num)
        np.save(npyFilePath, vectors)

        if os.path.exists(npyFilePath):
            return True
        else:
            return False

    # 获取人脸检测结果
    def getRgbImageRects(self, rgbImage):
        return self.detector(rgbImage, 1)

    # 人脸录入
    def take_photo(self,frame):
        '''
        :param frame: the opencv frame
        :return:
                    num: result code 0- no face,1- one face, 2- more than one face
                    frame_photo:
                    frame_feature:
        '''

        #复制frame 一张显示拍照后的照片
        frame_photo = frame.copy()
        #另一张显示人脸特征点
        frame_feature = frame.copy()
        # 带入模型检测人脸
        rects = self.getRgbImageRects(frame_photo)

        face_fingerprint = None

        # 如果未检测到人脸
        if len(rects) == 0:
            return 0,frame_photo,frame_feature,face_fingerprint
        # 如果检测到的人脸为一张
        elif len(rects) == 1:

            self.drawMaxRectangle(frame_photo, rects)  # 在图像上画出矩形框

            # 在照片中标出人脸68个特征点

            landmarks = np.matrix([[p.x, p.y] for p in self.shape_predictor(frame_feature, rects[0]).parts()])
            for idx, point in enumerate(landmarks):
                # 68点的坐标
                pos = (point[0, 0], point[0, 1])
                # print(idx, pos)
                # 利用cv2.circle给每个特征点画一个圈，共68个
                cv2.circle(frame_feature, pos, 2, color=(0, 255, 0))
            # 获取左上角以及右下角的坐标
            rectangleLT, rectangleRB = self.getMaxFaceRectangle(rects, 20)
            # 根据两点坐标截取图像
            frame_feature_show = frame_feature[rectangleLT[1]:rectangleRB[1], rectangleLT[0]:rectangleRB[0]]

            # 记录人脸特征点的数据
            took_current_cv2image = frame
            face_fingerprint = self.getMaxFaceFingerprint(rects, took_current_cv2image)

            return 1,frame_photo,frame_feature_show,face_fingerprint
        # 当人脸个数多余一个时
        else:
            self.drawMaxRectangle(frame_photo, rects)  # 在图像上画出矩形框
            return 2, frame_photo, frame_feature, face_fingerprint

    def extract_face_fingerprint_from_image(self, image):
        """
        :param image: cv2 BGR image
        :return:
            code: -1 图片读取失败, 0 无人脸, 1 单人脸, 2 多人脸
            frame_photo: 标注图
            frame_feature_show: 人脸局部图
            face_fingerprint: 128维特征
        """
        if image is None:
            return -1, None, None, None

        frame_photo = image.copy()
        frame_feature = image.copy()
        rects = self.getRgbImageRects(frame_photo)
        face_fingerprint = None

        if len(rects) == 0:
            return 0, frame_photo, frame_feature, face_fingerprint

        if len(rects) > 1:
            self.drawMaxRectangle(frame_photo, rects)
            return 2, frame_photo, frame_feature, face_fingerprint

        self.drawMaxRectangle(frame_photo, rects)

        landmarks = np.matrix([[p.x, p.y] for p in self.shape_predictor(frame_feature, rects[0]).parts()])
        for point in landmarks:
            pos = (point[0, 0], point[0, 1])
            cv2.circle(frame_feature, pos, 2, color=(0, 255, 0))

        rectangleLT, rectangleRB = self.getMaxFaceRectangle(rects, 20)
        h, w = frame_feature.shape[:2]
        x1, y1 = max(0, rectangleLT[0]), max(0, rectangleLT[1])
        x2, y2 = min(w, rectangleRB[0]), min(h, rectangleRB[1])
        frame_feature_show = frame_feature[y1:y2, x1:x2]

        face_fingerprint = self.getMaxFaceFingerprint(rects, image)
        return 1, frame_photo, frame_feature_show, face_fingerprint

    def extract_face_fingerprint_from_image_path(self, image_path):
        try:
            image_data = np.fromfile(image_path, dtype=np.uint8)
            image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        except Exception:
            image = None
        return self.extract_face_fingerprint_from_image(image)

    # CheckIn
    def check_in(self,frame,student_info_all):
        print("checkin")
        frame_photo = frame.copy()
        #took_current_cv2image = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        # 带入模型检测人脸
        rects = self.getRgbImageRects(frame_photo)

        search_result = None

        # 如果未检测到人脸
        if len(rects) == 0:
            return 0, frame_photo,search_result
        # 如果检测到的人脸为一张及以上
        elif len(rects) >= 1:

            self.drawMaxRectangle(frame_photo, rects)  # 在图像上画出矩形框

            # 找到最大的人脸
            current_fingerprint = self.getMaxFaceFingerprint(rects, frame_photo)
            # 寻找最相似脸的信息
            search_result = self.searchSimilarStudent(current_fingerprint,student_info_all)

            return 1, frame_photo, search_result

    # 在全局数据结构中搜索最相近的人脸
    def searchSimilarStudent(self, checkinSudentStudentDesc, student_infor_all):

        checkinStudentInfo = None
        maxSimilarity = 0.0

        # 当前帧的人脸特征与数据库学生的特征进行比对，获取最像的学生
        for i, playerInfo in enumerate(student_infor_all):

            dist = self.featureCompare(checkinSudentStudentDesc, playerInfo['feature'])

            if (1 - dist >= maxSimilarity):
                maxSimilarity = 1 - dist
                checkinStudentInfo = [playerInfo['sid'], playerInfo['name'], round(maxSimilarity * 100, 2)]

        return checkinStudentInfo

