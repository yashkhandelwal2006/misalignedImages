import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import imutils
import re

def find_nearest_in_dict(new_ele_list):
    diff_count_dict = {}
    max_len = -1
    final_list = []
    for new_ele in new_ele_list:
        flg = 0
        if new_ele in diff_count_dict:
            flg = 1
            diff_count_dict[new_ele].append(new_ele)
            if max_len < len(diff_count_dict[new_ele]):
                max_len = len(diff_count_dict[new_ele])
                final_list = diff_count_dict[new_ele]
        else:
            for key in diff_count_dict:
                if int(new_ele) in list(range(int(key) - 2, int(key) + 3)):
                    flg = 1
                    diff_count_dict[key].append(new_ele)
                    if max_len < len(diff_count_dict[key]):
                        max_len = len(diff_count_dict[key])
                        final_list = diff_count_dict[key]
                    break
        if flg == 0:
            diff_count_dict[new_ele] = [new_ele]
    return final_list


def find_rotation_angle_from_lines(all_lines):
    d = {'positive':[], 'negative':[]}
    for line in all_lines:
        x1, y1, x2, y2, theta = line
        angle = 90 - 180*theta/3.1415926
        if y2 - y1 < 0:
            d['positive'].append(angle)
        else:
            d['negative'].append(angle)
    final_rotation_angle = 0
    if len(d['positive']) > 0.6*len(all_lines):
        final_angles = find_nearest_in_dict(d['positive'])
        final_rotation_angle = sum(final_angles) / len(final_angles)
    if len(d['negative']) > 0.6*len(all_lines):
        final_angles = find_nearest_in_dict(d['negative'])
        final_rotation_angle = sum(final_angles) / len(final_angles)
    return final_rotation_angle * -1


def get_hough_lines(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    lines = cv2.HoughLines(edges,1,np.pi/180, 200)
    all_lines = []
    for line in lines:
        for r,theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*r
            y0 = b*r
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            angle = 90 - 180*theta/3.1415926
            if y2 - y1 < x2 - x1 and (x2 - x1) > img.shape[1]//5 and int(angle) in range(-40, 40):
                all_lines.append([x1, y1, x2, y2, theta])
                #cv2.line(img, (x1,y1),(x2,y2), (0,255,255), 2)
    #plt.imshow(img)
    #plt.show()
    return all_lines


def get_orientation_from_bboxes(img):
    bboxes, only_text = get_text_bboxes(img)
    count = 0
    for box in bboxes:
        if box[1][2] < box[1][3]:
            count += 1
    if count > len(bboxes) // 2:
        print('left/right')
        img1 = imutils.rotate(img, 90)
        img2 = imutils.rotate(img, -90)
        b1 ,_ = get_text_bboxes(img1, r"--psm 11")
        b2 ,_ = get_text_bboxes(img2, r"--psm 11")
        if len(b1) > len(b2):
            img = img1
        else:
            img = img2
    else:
        print('normal/upside down')
        img1 = img.copy()
        img2 = imutils.rotate(img, 180)
        b1 ,_ = get_text_bboxes(img1, r"--psm 11")
        b2 ,_ = get_text_bboxes(img2, r"--psm 11")
        if len(b1) > len(b2):
            img = img1
        else:
            img = img2
    return img
        

def get_text_bboxes(img, config=r"--psm 12"):
    d = pytesseract.image_to_data(img, output_type=Output.DICT, config=config)
    n_boxes = len(d['level'])
    all_text_and_bbox = []
    only_text = ''
    for i in range(n_boxes):
        text = d['text'][i]
        if len(text.strip()) > 4 and len(text.strip()) < 15:
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            all_text_and_bbox.append([text, [x,y,w,h]])
            only_text += text + ' '
    return all_text_and_bbox, only_text



def get_correct_allignment(img):
    try:
        rot_data = pytesseract.image_to_osd(img)
        rot = re.search('(?<=Rotate: )\d+', rot_data).group(0)
        conf = re.search('(?<=Orientation confidence: )[\d\.]+', rot_data).group(0)
        conf = 0
        if float(conf) >= 0.8:
            if int(rot) in [90, 180, 270]:
                img = imutils.rotate(img, 360 - int(rot))
        else:
            img = get_orientation_from_bboxes(img)
    except:
        img = get_orientation_from_bboxes(img)
    return img


def alignment_correction(img):
    img = get_correct_allignment(img)
    all_lines = get_hough_lines(img)
    angle = find_rotation_angle_from_lines(all_lines)
    img = imutils.rotate(img, angle)
    return img
