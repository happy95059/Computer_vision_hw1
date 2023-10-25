import cv2

# 打开摄像头
cap = cv2.VideoCapture(0)

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 创建窗口
cv2.namedWindow("Video Capture")

# 是否开始录制
recording = False

while True:
    # 读取当前帧
    ret, frame = cap.read()

    # 显示当前帧
    cv2.imshow("Video Capture", frame)

    # 等待按键输入，等待时间为1毫秒
    key = cv2.waitKey(1) & 0xFF

    # 按下 'w' 键，保存当前帧
    if key == ord('3'):
        cv2.imwrite('origin_background.jpg', frame)
        print("Saved a frame.")

    # 按下 'q' 键，退出循环
    elif key == ord('1'):
        break

# 释放摄像头资源
cap.release()

# 关闭窗口
cv2.destroyAllWindows()



