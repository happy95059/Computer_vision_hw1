import cv2
import numpy as np
import random


# in:BGR img  out: center ,mask  method= 'color' , 'edge'
def get_poker_direction(origin_pic,method="color"):
    # color range
    up_bound = np.array([112,40,256])
    down_bound = np.array([30,-1,160])
    pic = cv2.cvtColor(origin_pic, cv2.COLOR_BGR2HSV)
    pic = np.array(pic)
    #####in range
    poker = (pic<up_bound).prod(axis=2) * (pic>down_bound).prod(axis=2)
    temp = np.zeros([pic.shape[0],pic.shape[1]])
    ###use filter to find max index
    for x in range(pic.shape[1]-check_filter[0]-1):
        for y in range(pic.shape[0]-check_filter[1]-1):
            temp[y,x] = np.sum(poker[y:y+check_filter[1],x:x+check_filter[0]])
    max_index = np.unravel_index(np.argmax(temp), temp.shape)
    ###
    temp = np.zeros(poker.shape)
    #find poker_center
    poker_center = np.array(max_index)[::-1]+(check_filter/2).astype('int')
    ###only save some color which near the center
    x_slice = slice(int(poker_center[0]-check_filter[0]/2),int(poker_center[0]+check_filter[0]/2))
    y_slice = slice(int(poker_center[1]-check_filter[1]/2),int(poker_center[1]+check_filter[1]/2))
    temp[y_slice,x_slice] = 1
    temp  = cv2.dilate(temp, (5,5), iterations=1)
    poker = poker * temp
    #update coint_center
    poker = np.array(poker)
    y, x = np.nonzero(poker)
    if len(x)>0 and len(y)>0:
        poker_center = np.mean(np.column_stack((x, y)), axis=0).astype(int)
    else:
        return [None],None
    x_slice = slice(max(0,int(poker_center[0]-check_filter[0]/2-15)),min(500,int(poker_center[0]+check_filter[0]/2+15)))
    y_slice = slice(max(0,int(poker_center[1]-check_filter[1]/2-15)),min(500,int(poker_center[1]+check_filter[1]/2+15)))
    ###

    # let detect look good
    poker = cv2.dilate(poker, (5,5), iterations=2)
    poker = cv2.erode(poker, (5,5), iterations=1)
    print(np.sum(poker))
    #if poker small means not poker
    if np.sum(poker)<12000:
        return [None],None
     ###  color base
    if method=='color':
        #expend to rgb
        poker = poker[:,:,np.newaxis]
        poker = np.repeat(poker, 3, axis=2)
        return poker_center,poker
    ###  edge base
    elif method=='edge':
        print(y_slice,x_slice)

        edge_img = cv2.cvtColor(origin_pic[y_slice,x_slice], cv2.COLOR_BGR2GRAY)
        edge_img = cv2.Canny(edge_img,5,150)
        cv2.imshow('bb',edge_img)
        contours, hierarchy = cv2.findContours(edge_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        poker = np.zeros(origin_pic.shape)
        cv2.drawContours(poker[y_slice,x_slice], contours, -1, (1, 1, 1), thickness=cv2.FILLED)
        poker  = cv2.dilate(poker, (5,5), iterations=3)
        
        return poker_center,poker

# in:BGR img ,center  out:BGR img
def change_pocker_color(origin_img,center,card='d4'):
    if card =='d4':
        card = cv2.imread('poker_dimon_4.jpg')
    elif card == 'd5':
        card = cv2.imread('poker_dimon_5.jpg')
    img = origin_img.copy()
    x_slice = slice(max(0,int(center[0]-62)),min(work_area[0][1]-work_area[0][0],int(center[0]-62+card.shape[1])))
    y_slice = slice(max(0,int(center[1]-80)),min(work_area[1][1]-work_area[1][0],int(center[1]-80+card.shape[0])))
    try:
        img[y_slice,x_slice] = card
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

# in:BGR img   out:BGR img   method = point , center , black , 
def change_color2background(img,center,target,method='center'):
    if method == 'point' or method == 'black':
        ###first method base on point
        not_target = np.logical_not(target).astype(int)
        if method == 'point':
            temp = get_origin_color(target)
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
# main code
def open_camera():
    global origin
    global frame
    global work_area
    global check_filter
    work_area = [[128,507],[171,420]]
    work_area = [[150,507],[147,464]]
    frame_count = 0
    disapear_poker_flag = False
    cards = ['d4','d5']
    #poker size
    check_filter = np.array([170,200])
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
    while True:
        frame_count +=1
        # 讀取一幀視訊
        ret,  frame = cap.read()
        # 檢查讀取是否成功
        if not ret:
            print("無法讀取視訊。")
            break  

        origin = frame.copy()
        poker = frame.copy()
        hand = frame.copy()
        homework_2 = frame.copy()
        work_img = frame[y_slice,x_slice].copy()
        center,poker_mask = get_poker_direction(work_img,'edge')
        hand_mask = get_hand_direction(work_img)
        pic_hand = change_color2background(work_img,None,hand_mask,'black')
        
        if center[0]!=None:
            pic_poker = change_pocker_color(work_img,center,cards[disapear_poker_flag])
            center_temp = center.copy()
        else:
            pic_poker = work_img
        try:
            if(hand_mask[center_temp[1]][center_temp[0]][0]==1) and frame_count>2:
                disapear_poker_flag = not disapear_poker_flag
                print("change") 
                center_temp = None
                frame_count=0
        except :
            print("no pocker")
        '''
        if disapear_poker_flag:
            pic_hw2 = pic_poker
        else :
            pic_hw2 = work_img
        '''
        pic_hw2 = pic_poker
        poker[y_slice,x_slice] = pic_poker
        hand[y_slice,x_slice]=pic_hand
        homework_2[y_slice,x_slice]=pic_hw2




        cv2.imshow('origin', origin)
        cv2.imshow('poker', poker)
        cv2.imshow('hw2', homework_2)
        #out.write(homework_2)
        show_edge(work_img)

        if cv2.waitKey(1) & 0xFF == ord('1'):
            break

    # 釋放攝影機資源
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    open_camera()
