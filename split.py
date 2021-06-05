from pdf2image import convert_from_path
import os
import cv2
import numpy as np
import shutil
import matplotlib.pyplot as plt
import yaml
from chart import Menu, Label
from drive_api import upload_with_ocr, get_menu_items, get_date, delete_docs

if __name__ == '__main__':
    images = convert_from_path('data/data.pdf')
    monthly_menus = []

    for i, img in enumerate(images):
        img = np.array(img, dtype=np.uint8)
        if img.shape[0] > img.shape[1]:
            img = np.rot90(img, 3)
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

        fnames = []
        labels = []
        menus = []
        count = 0   # avoid date format error.

        for j, cnt in enumerate(contours):
            if cv2.contourArea(cnt) > 12600:
                x, y, w, h = cv2.boundingRect(cnt)
                plt.imsave(f'images/{i}_{j}.png', img[y:y + h - 35, x:x + w])
                menus.append(Menu(f'{i}_{j}.png', x=x, y=y))
            elif cv2.contourArea(cnt) > 9000:
                x, y, w, h = cv2.boundingRect(cnt)
                plt.imsave(f'images/{i}_{j}.png', img[y:y + h, x:x + w])
                label = Label(f'{i}_{j}.png', x=x, y=y)
                if count > 2:
                    fid = upload_with_ocr(label.fname)
                    label.value = get_date(fid)
                    delete_docs(fid)
                labels.append(label)
                count += 1

        del menus[0]
        menus.reverse()

        for menu in menus:
            for label in labels[3:]:
                if abs(label.x - menu.x) < 4:
                    menu.date = label.value
                    break

            if abs(labels[2].y - menu.y) < 10:
                menu.meal_type = 0
            elif abs(labels[1].y - menu.y) < 10:
                menu.meal_type = 1
            else:
                menu.meal_type = 2

        monthly_menus.append(menus)

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

    with open('outputs/menu.yml') as file:
        obj = yaml.safe_load(file)
        for week, menus in enumerate(monthly_menus):
            # meal_type: 0 -> breakfast, 1 -> lunch, 2 -> dinner
            for f in menus:
                fid = upload_with_ocr(f.fname)
                menu_items = get_menu_items(fid)
                obj.setdefault(f.date, {})
                obj[f.date].setdefault('breakfast', [])
                obj[f.date].setdefault('lunch', [])
                obj[f.date].setdefault('dinner', [])

                if f.meal_type == 0:
                    obj[f.date]['breakfast'] = menu_items
                elif f.meal_type == 1:
                    obj[f.date]['lunch'] = menu_items
                else:
                    obj[f.date]['dinner'] = menu_items

                delete_docs(fid)

    with open('outputs/menu.yml', 'w') as file:
        yaml.dump(obj, file, encoding='utf-8')

    shutil.rmtree('images')
    os.mkdir('images')
