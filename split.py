from pdf2image import convert_from_path
import os
import cv2
import numpy as np
import shutil
import datetime
import matplotlib.pyplot as plt
import yaml
from drive_api import upload_with_ocr, get_menu_items, delete_docs

if __name__ == '__main__':
    images = convert_from_path('data/data.pdf')
    out_files = []

    for i, img in enumerate(images):
        img = np.array(img, dtype=np.uint8)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray = cv2.bitwise_not(gray)

        bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)
        cols = bw.shape[1]
        horizontal_size = int(cols / 30)
        horizontal_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
        horizontal = cv2.morphologyEx(bw, cv2.MORPH_OPEN, horizontal_structure)

        rows = bw.shape[0]
        vertical_size = int(rows / 30)
        vertical_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
        vertical = cv2.morphologyEx(bw, cv2.MORPH_OPEN, vertical_structure)

        dst = cv2.addWeighted(horizontal, 0.5, vertical, 0.5, 0)
        dst = np.where(dst > 0, 255, dst)
        contours, _ = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        rects = []
        fnames = []

        for j, cnt in enumerate(contours):
            if cv2.contourArea(cnt) > 12600.0:
                x, y, w, h = cv2.boundingRect(cnt)
                plt.imsave(f'images/{i}_{j}.png', img[y:y + h - 35, x:x + w])
                fnames.append(f'{i}_{j}.png')

        fnames.pop(0)
        fnames.reverse()
        out_files.append(fnames)

        plt.figure(figsize=(12, 10))
        plt.imshow(img)
        plt.show()

        plt.figure(figsize=(12, 10))
        plt.imshow(vertical, cmap='gray')
        plt.show()

        plt.figure(figsize=(12, 10))
        plt.imshow(horizontal, cmap='gray')
        plt.show()

        plt.figure(figsize=(12, 10))
        plt.imshow(dst, cmap='gray')
        plt.show()

    today = datetime.datetime.now()
    obj = dict()

    for week, menus in enumerate(out_files):
        # meal_type: 0 -> breakfast, 1 -> lunch, 2 -> dinner
        delta = 0
        meal_type = 0
        if week > 0:
            today = today + datetime.timedelta(days=7)
        for f in menus:
            if delta > 6:
                delta = 0
                meal_type = 0 if meal_type == 2 else meal_type % 2 + 1
            fid = upload_with_ocr(f)
            menu_items = get_menu_items(fid)
            day = today + datetime.timedelta(days=delta)
            daystr = day.strftime('%Y/%m/%d')
            obj.setdefault(daystr, {})
            obj[daystr].setdefault('breakfast', '')
            obj[daystr].setdefault('lunch', '')
            obj[daystr].setdefault('dinner', '')

            if meal_type == 0:
                obj[daystr]['breakfast'] = menu_items
            elif meal_type == 1:
                obj[daystr]['lunch'] = menu_items
            else:
                obj[daystr]['dinner'] = menu_items

            delete_docs(fid)
            delta += 1

    with open('outputs/menu.yml', 'w') as file:
        yaml.dump(obj, file)

    shutil.rmtree('images')
    os.mkdir('images')
