import cv2
import numpy as np
import random
frame =0
###print edge img
def show_edge(origin_pic):
    edge_img = cv2.cvtColor(origin_pic, cv2.COLOR_BGR2GRAY)
    edge_img = cv2.Canny(edge_img,5,150)

    # 寻找轮廓
    contours, hierarchy = cv2.findContours(edge_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 创建一个全黑的图像作为填充背景
    filled_image = np.zeros(origin_pic.shape)

    # 在填充图像上绘制轮廓并填充轮廓内的区域
    cv2.drawContours(filled_image, contours, -1, (0, 255, 0), thickness=cv2.FILLED)

    cv2.imshow('edge', filled_image)


# in:BGR img  out: center ,mask       method = 'color' , 'edge'
def get_coint_direction(origin_pic,method='color'):
    # color range
    up_bound = np.array([60,40,256])
    down_bound = np.array([30,0,160])
    #coint size
    check_filter = np.array([50,45])
    pic = cv2.cvtColor(origin_pic, cv2.COLOR_BGR2HSV)
    pic = np.array(pic)
    #####in range
    coint = (pic<up_bound).prod(axis=2) * (pic>down_bound).prod(axis=2)
    temp = np.zeros([pic.shape[0],pic.shape[1]])
    ###use filter to find max index
    for x in range(pic.shape[1]-check_filter[0]-1):
        for y in range(pic.shape[0]-check_filter[1]-1):
            temp[y,x] = np.sum(coint[y:y+check_filter[1],x:x+check_filter[0]])
    max_index = np.unravel_index(np.argmax(temp), temp.shape)
    ###
    temp = np.zeros(coint.shape)
    #find coint_center
    coint_center = np.array(max_index)[::-1]+(check_filter/2).astype('int')
    ###only save some color which near the center
    x_slice = slice(int(coint_center[0]-check_filter[0]/2),int(coint_center[0]+check_filter[0]/2))
    y_slice = slice(int(coint_center[1]-check_filter[1]/2),int(coint_center[1]+check_filter[1]/2))
    temp[y_slice,x_slice] = 1
    coint = coint * temp
    #update coint_center
    coint = np.array(coint)
    y, x = np.nonzero(coint)
    if len(x)>0 and len(y)>0:
        coint_center = np.mean(np.column_stack((x, y)), axis=0).astype(int)
    else:
        return [None],None

    x_slice = slice(int(coint_center[0]-check_filter[0]/2),int(coint_center[0]+check_filter[0]/2))

    y_slice = slice(int(coint_center[1]-check_filter[1]/2),int(coint_center[1]+check_filter[1]/2))
    ###

    # let detect look good
    coint = cv2.dilate(coint, (5,5), iterations=1)
    coint = cv2.erode(coint, (5,5), iterations=1)

    #if coint small means not coint
    if np.sum(coint)<50:
        return [None],None
    ###  color base
    if method=='color':
        #expend to rgb
        coint = coint[:,:,np.newaxis]
        coint = np.repeat(coint, 3, axis=2)
        return coint_center,coint
    ###  edge base
    elif method=='edge':
        edge_img = cv2.cvtColor(origin_pic[y_slice,x_slice], cv2.COLOR_BGR2GRAY)
        edge_img = cv2.Canny(edge_img,5,150)

        contours, hierarchy = cv2.findContours(edge_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        coint = np.zeros(origin_pic.shape)
        cv2.drawContours(coint[y_slice,x_slice], contours, -1, (1, 1, 1), thickness=cv2.FILLED)
        coint  = cv2.dilate(coint, (5,5), iterations=3)
        return coint_center,coint

# in:BGR img   out:BGR img   method = point , center , black , 
def change_color2background(img,center,target,method='center'):
    if method == 'point' or method == 'black':
        ###first method base on point
        not_target = np.logical_not(target).astype(int)
        temp = get_origin_color(target)
        if method == 'point':
            new_img = img * not_target + temp
        elif method == 'black':
            new_img = img * not_target + target * [110,47,81]
        ###
    
    elif method == 'center':
        ###second method base on center
        target_size = np.array([55,55])
        new_img = img.copy()
        temp = np.zeros(img.shape)
        temp[int(center[1]-target_size[1]/2):int(center[1]+target_size[1]/2),
            int(center[0]-target_size[0]/2):int(center[0]+target_size[0]/2)] = 1
        temp = get_origin_color(temp)
        new_img[int(center[1]-target_size[1]/2):int(center[1]+target_size[1]/2),
            int(center[0]-target_size[0]/2):int(center[0]+target_size[0]/2)] = 0
        new_img = new_img + temp
        ###
    else :
        exit('error method')

    new_img = np.clip(new_img, 0, 255).astype(np.uint8)
    return new_img

# in:mask   out:BGR img
def get_origin_color(img_area):
    img = cv2.imread('origin_background.jpg')
    x_slice = slice(work_area[0][0],work_area[0][1])
    y_slice = slice(work_area[1][0],work_area[1][1])
    return img[y_slice,x_slice]*img_area

# in:BGR img  out:mask
def get_hand_direction(pic):
    up_bound = np.array([20,150,256])
    down_bound = np.array([0,60,200])
    pic = cv2.cvtColor(pic, cv2.COLOR_BGR2HSV)
    pic = np.array(pic)
    #範圍內的
    hand = (pic<up_bound).prod(axis=2) * (pic>down_bound).prod(axis=2)
    #擴充到rgb
    hand = hand[:,:,np.newaxis]
    hand = np.repeat(hand, 3, axis=2)

    return hand

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


# main code
def open_camera():
    global origin
    global frame
    global work_area
    work_area = [[152,472],[156,358]]
    disapear_coint_flag = False
    x_slice = slice(work_area[0][0],work_area[0][1])
    y_slice = slice(work_area[1][0],work_area[1][1])
    
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('origin')

    width = int(cap.get(3))
    height = int(cap.get(4))


    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (width, height))

    cv2.setMouseCallback('origin', mouse_callback)
    # 檢查攝影機是否成功打開
    if not cap.isOpened():
        print("無法打開攝影機。")
        return
    frame_count = 0
    while True:
        frame_count +=1
        
        # 讀取一幀視訊
        ret,  frame = cap.read()
        # 檢查讀取是否成功
        if not ret:
            print("無法讀取視訊。")
            break
            
        #print(frame_count)
        origin = frame.copy()
        coint = frame.copy()
        hand = frame.copy()
        homework_1 = frame.copy()
        work_img = frame[y_slice,x_slice].copy()

        center,coint_mask = get_coint_direction(work_img,method='edge')
        hand_mask = get_hand_direction(work_img)
        pic_hand = change_color2background(work_img,None,hand_mask,'black')

        if center[0]!=None:
            pic_coint = change_color2background(work_img,center,coint_mask,'point')
            center_temp = center.copy()
        else:
            pic_coint = work_img
        try:
            if(hand_mask[center_temp[1]][center_temp[0]][0]==1) and frame_count>2:
                disapear_coint_flag = not disapear_coint_flag
                print("change") 
                center_temp = None
                frame_count=0
        except :
            print("no coint")

        if disapear_coint_flag:
            pic_hw1 = pic_coint
        else :
            pic_hw1 = work_img

        coint[y_slice,x_slice]=pic_coint
        hand[y_slice,x_slice]=pic_hand
        homework_1[y_slice,x_slice]=pic_hw1
        #Blur
        homework_1 = cv2.GaussianBlur(homework_1, (5,5), 0)


        cv2.imshow('origin', origin)
        #cv2.imshow('hand', hand)
        cv2.imshow('coint', coint)
        cv2.imshow('homework_1', homework_1)
        show_edge(work_img)
        #out.write(homework_1)

        if cv2.waitKey(1) & 0xFF == ord('1'):
            break

    # 釋放攝影機資源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    open_camera()
