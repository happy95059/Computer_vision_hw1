import cv2
import numpy as np

# mousemove event listeners
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        # 獲取滑鼠位置的HSV值
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color = hsv_image[y, x]
        
        # 顯示座標和RGB值在視窗下方
        text = f"Mouse: ({x}, {y}), HSV: {color}"
        cv2.putText(frame, text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        print('HSV:',color)
        print('(x,y) =' , x,y)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("无法打开摄像头")
    exit()

cv2.namedWindow("origin")
cv2.setMouseCallback('origin', mouse_callback)

work_area = [[299,429],[245,409]]

x_slice = slice(work_area[0][0],work_area[0][1])
y_slice = slice(work_area[1][0],work_area[1][1])
while True:

    ret, frame = cap.read()

    origin = frame.copy()
    poker = frame.copy()

    poker = frame[y_slice,x_slice,:].copy()

    
    cv2.imshow("origin", origin)
    cv2.imshow("poker", poker)
    # 等待按键输入，等待时间为1毫秒
    key = cv2.waitKey(1) & 0xFF

    # 按下 'w' 键，保存当前帧
    if key == ord('3'):
        cv2.imwrite('poker_dimon_5.jpg', poker)
        print("Saved a frame.")

    # 按下 'q' 键，退出循环
    elif key == ord('1'):
        break

# 释放摄像头资源
cap.release()

# 关闭窗口
cv2.destroyAllWindows()



