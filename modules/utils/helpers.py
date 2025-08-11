import cv2

def crop_face_from_frame(frame, face_rect):
    # face_rect = (x,y,w,h)
    x,y,w,h = face_rect
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    roi = gray[y:y+h, x:x+w]
    return roi
