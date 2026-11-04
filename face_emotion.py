import numpy as np
import cv2
import streamlit as st

def detect_emotion_from_face(img_bytes):
    try:
        from fer import FER
    except ImportError:
        st.error("FER not installed. Run `pip install fer==22.4.0`")
        return None
    
    file_bytes = np.asarray(bytearray(img_bytes.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)
    if frame is None:
        return None
    
    detector = FER(mtcnn=True)  # initialize FER detector
    em, score = detector.top_emotion(frame)
    
    if em:
        return em.lower()
    return None
