# -*- coding:utf-8 -*-
import os

# 程序工作路径
WORKING_PATH = os.path.abspath(os.path.dirname(__file__))

# 依赖文件存放路径
SOURCE = os.path.join(WORKING_PATH, "dlib_model")

# 人脸特征点模型文件
PREDICTOR_PATH = os.path.join(SOURCE, "shape_predictor_68_face_landmarks.dat")

# 人脸特征描述模型文件
FACE_REC_MODEL_PATH = os.path.join(SOURCE, "dlib_face_recognition_resnet_model_v1.dat")

# 数据库路径
DATABASE_PATH = "./database/database.db"

# 相似度阈值（大于该值认为识别通过）
SIMILARITY_THRESHOLD = 60.0

# 识别成功后，开门指示灯展示时间（毫秒）
LED_OPEN_TIME = 5000

# 仅本地摄像头索引，按顺序尝试（0 -> 1 -> 2 -> 3）
LOCAL_CAMERA_INDEXES = [0, 1, 2, 3]


def get_camera_sources():
    return list(LOCAL_CAMERA_INDEXES)


def open_camera_capture(cv2_module):
    """
    自动打开第一个可用本地摄像头。
    返回: (cap, source_text, tried_text)
    """
    tried = []
    for source in get_camera_sources():
        backend_candidates = [cv2_module.CAP_DSHOW, cv2_module.CAP_MSMF, None]
        for backend in backend_candidates:
            if backend is None:
                cap = cv2_module.VideoCapture(source)
                backend_name = "AUTO"
            else:
                cap = cv2_module.VideoCapture(source, backend)
                backend_name = "DSHOW" if backend == cv2_module.CAP_DSHOW else "MSMF"

            tried.append(f"{source}({backend_name})")
            if cap.isOpened():
                ok, _ = cap.read()
                if ok:
                    return cap, str(source), "、".join(tried)
            cap.release()
    return None, "", "、".join(tried)


# Attendance rule defaults for strategy engine
DEFAULT_RULE_NAME = "默认考勤策略"
DEFAULT_START_TIME = "08:00"
DEFAULT_END_TIME = "10:00"
DEFAULT_ABSENCE_DEADLINE = "10:00"
DEFAULT_LATE_MINUTES = 10
DEFAULT_DEDUPE_SCOPE = "student+date+rule"
