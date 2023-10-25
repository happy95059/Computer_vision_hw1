import cv2
import numpy as np
import random


#for test
# in:BGR img   out:BGR img   method = black , 
def change_color2background(img,center,target,method='black'):
    if method == 'point' or method == 'black':
        ###first method base on point
        not_target = np.logical_not(target).astype(int)
        if method == 'black':
            new_img = img * not_target + target * [110,47,81]


    new_img = np.clip(new_img, 0, 255).astype(np.uint8)
    return new_img

# in:BGR img  out: center ,mask  method= 'color' , 'edge'
def get_dice_direction(origin_pic,method="color"):
    # color range
    up_bound = np.array([60,20,256])
    down_bound = np.array([30,-1,160])
    pic = cv2.cvtColor(origin_pic, cv2.COLOR_BGR2HSV)
    pic = np.array(pic)
    #####in range
    dice = (pic<up_bound).prod(axis=2) * (pic>down_bound).prod(axis=2)
    temp = np.zeros([pic.shape[0],pic.shape[1]])
    ###use filter to find max index
    for x in range(pic.shape[1]-check_filter[0]-1):
        for y in range(pic.shape[0]-check_filter[1]-1):
            temp[y,x] = np.sum(dice[y:y+check_filter[1],x:x+check_filter[0]])
    max_index = np.unravel_index(np.argmax(temp), temp.shape)
    ###
    temp = np.zeros(dice.shape)
    #find dice_center
    dice_center = np.array(max_index)[::-1]+(check_filter/2).astype('int')
    ###only save some color which near the center
    x_slice = slice(int(dice_center[0]-check_filter[0]/2),int(dice_center[0]+check_filter[0]/2))
    y_slice = slice(int(dice_center[1]-check_filter[1]/2),int(dice_center[1]+check_filter[1]/2))
    temp[y_slice,x_slice] = 1
    temp  = cv2.dilate(temp, (5,5), iterations=1)
    dice = dice * temp
    #update coint_center
    dice = np.array(dice)
    y, x = np.nonzero(dice)
    if len(x)>0 and len(y)>0:
        dice_center = np.mean(np.column_stack((x, y)), axis=0).astype(int)
    else:
        return [None],None
    x_slice = slice(max(0,int(dice_center[0]-check_filter[0]/2-15)),min(500,int(dice_center[0]+check_filter[0]/2+15)))
    y_slice = slice(max(0,int(dice_center[1]-check_filter[1]/2-15)),min(500,int(dice_center[1]+check_filter[1]/2+15)))
    ###

    # let detect look good
    dice = cv2.dilate(dice, (5,5), iterations=2)
    dice = cv2.erode(dice, (5,5), iterations=1)
    print(np.sum(dice))
    #if dice small means not dice
    if np.sum(dice)<4000:
        return [None],None
     ###  color base
    if method=='color':
        #expend to rgb
        dice = dice[:,:,np.newaxis]
        dice = np.repeat(dice, 3, axis=2)
        return dice_center,dice
    ###  edge base
    elif method=='edge':
        print(y_slice,x_slice)

        edge_img = cv2.cvtColor(origin_pic[y_slice,x_slice], cv2.COLOR_BGR2GRAY)
        edge_img = cv2.Canny(edge_img,5,150)
        cv2.imshow('bb',edge_img)
        contours, hierarchy = cv2.findContours(edge_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dice = np.zeros(origin_pic.shape)
        cv2.drawContours(dice[y_slice,x_slice], contours, -1, (1, 1, 1), thickness=cv2.FILLED)
        dice  = cv2.dilate(dice, (5,5), iterations=3)
        
        return dice_center,dice

# in:BGR img ,center  out:BGR img
def change_dice_color(origin_img,center,dice='1'):
    if dice =='1':
        dice = cv2.imread('dice_1.jpg')

    img = origin_img.copy()
    x_slice = slice(max(0,int(center[0]-40)),min(work_area[0][1]-work_area[0][0],int(center[0]-40+dice.shape[1])))
    y_slice = slice(max(0,int(center[1]-30)),min(work_area[1][1]-work_area[1][0],int(center[1]-30+dice.shape[0])))
    try:
        img[y_slice,x_slice] = dice
    except:
        return img

    return img

###print edge img
def show_edge(origin_pic):
    edge_img = cv2.cvtColor(origin_pic, cv2.COLOR_BGR2GRAY)
    edge_img = cv2.Canny(edge_img,5,150)
    cv2.imshow('edge', edge_img)
# mousemove event listeners
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        # 獲取滑鼠位置的HSV值
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color = hsv_image[y, x]
        
        # 顯示座標和RGB值在視窗下方
        text = f"Mouse: ({x}, {y}), HSV: {color}"
        cv2.putText(frame, text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        print('HSV:',color)
        print('(x,y) =' , x,y)
# main code
def open_camera():
    global origin
    global frame
    global work_area
    global check_filter
    work_area = [[128,507],[171,420]]
    work_area = [[150,507],[147,464]]
    frame_count = 0
    #dice size
    check_filter = np.array([80,60])
    x_slice = slice(work_area[0][0],work_area[0][1])
    y_slice = slice(work_area[1][0],work_area[1][1])
 
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('origin')

    width = int(cap.get(3))
    height = int(cap.get(4))


    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 5.0, (width, height))
    
    cv2.setMouseCallback('origin', mouse_callback)
    # 檢查攝影機是否成功打開
    if not cap.isOpened():
        print("無法打開攝影機。")
        return
    while True:
        frame_count +=1
        # 讀取一幀視訊
        ret,  frame = cap.read()
        # 檢查讀取是否成功
        if not ret:
            print("無法讀取視訊。")
            break  

        origin = frame.copy()
        dice = frame.copy()
        test = frame.copy()
        homework_3 = frame.copy()
        work_img = frame[y_slice,x_slice].copy()
        # detect dice
        center,dice_mask = get_dice_direction(work_img,'edge')
        if center[0]!=None: 
            #pic_test = change_color2background(work_img,center,dice_mask,'black')
            # paste dice picture
            pic_dice = change_dice_color(work_img,center,'1')
        else :
            #pic_test = work_img
            pic_dice = work_img
        dice[y_slice,x_slice] = pic_dice
        #test[y_slice,x_slice] = pic_test


        cv2.imshow('origin', origin)
        cv2.imshow('dice', dice)
        #cv2.imshow('test',test)
        #hw3

        out.write(dice)
        show_edge(work_img)

        if cv2.waitKey(1) & 0xFF == ord('1'):
            break

    # 釋放攝影機資源
    cap.release()
    cv2.destroyAllWindows()









if __name__ == "__main__":
    open_camera()
