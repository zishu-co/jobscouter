# -*- coding: utf-8 -*-
import cv2
import numpy as np
from PIL import Image
import base64
import io
import time
import os

class CaptchaCracker:
    def __init__(self):
        self.debug = True  # 调试模式默认开启
        self.debug_dir = "debug_images"  # 调试图片保存目录
        
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
    
    def _save_debug_image(self, image, name):
        """保存调试图片"""
        timestamp = int(time.time())
        path = os.path.join(self.debug_dir, f"{name}_{timestamp}.png")
        cv2.imwrite(path, image)
        return path
    
    def base64_to_image(self, base64_str):
        """将Base64字符串转换为OpenCV图像"""
        try:
            if ',' in base64_str:
                base64_str = base64_str.split(',')[1]
            img_data = base64.b64decode(base64_str)
            img = Image.open(io.BytesIO(img_data))
            cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            return cv_img
        except Exception as e:
            print(f"Base64转换图片失败: {str(e)}")
            return None

    def split_target_icons(self, target_img):
        """切割目标图案"""
        try:
            # 转为灰度图
            gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
            
            # 二值化
            _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
            
            # 查找轮廓
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 按x坐标排序轮廓
            contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
            
            icons = []
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                # 过滤小面积噪点
                if w * h < 100:
                    continue
                    
                # 裁剪图标并添加边距
                padding = 2
                x, y = max(0, x-padding), max(0, y-padding)
                w, h = min(target_img.shape[1]-x, w+2*padding), min(target_img.shape[0]-y, h+2*padding)
                icon = target_img[y:y+h, x:x+w]
                icons.append(icon)
                
                # 保存调试图片
                self._save_debug_image(icon, f"target_icon_{i}")
            
            return icons
            
        except Exception as e:
            print(f"切割目标图标失败: {str(e)}")
            return []

    def find_icon_locations(self, search_img, target_icon):
        """使用SIFT特征匹配查找图标位置"""
        try:
            # 创建SIFT对象
            sift = cv2.SIFT_create()
            
            # 检测关键点和描述符
            kp1, des1 = sift.detectAndCompute(target_icon, None)
            kp2, des2 = sift.detectAndCompute(search_img, None)
            
            if des1 is None or des2 is None:
                return []
            
            # 创建FLANN匹配器
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            
            # 进行匹配
            matches = flann.knnMatch(des1, des2, k=2)
            
            # 应用比率测试
            good_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:  # 可调整阈值
                    good_matches.append(m)
            
            # 至少需要4个点来找到透视变换
            if len(good_matches) < 4:
                return []
            
            # 获取匹配点的坐标
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            # 使用RANSAC算法找到最佳匹配点
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            matches_mask = mask.ravel().tolist()
            
            points = []
            debug_img = search_img.copy()
            
            # 获取匹配中心点
            for i, match in enumerate(good_matches):
                if matches_mask[i]:
                    pt = dst_pts[i][0]
                    x, y = int(pt[0]), int(pt[1])
                    
                    # 检查是否重复
                    is_duplicate = False
                    for existing_pt in points:
                        if abs(existing_pt[0] - x) < 10 and abs(existing_pt[1] - y) < 10:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        points.append((x, y))
                        # 在调试图像上画出匹配点
                        cv2.circle(debug_img, (x, y), 5, (0, 0, 255), -1)
            
            # 绘制匹配结果
            h, w = target_icon.shape[:2]
            pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
            if M is not None:
                dst = cv2.perspectiveTransform(pts, M)
                cv2.polylines(debug_img, [np.int32(dst)], True, (0, 255, 0), 2)
            
            self._save_debug_image(debug_img, f"match_debug_{time.time()}")
            return points
            
        except Exception as e:
            print(f"查找图标位置失败: {str(e)}")
            return []
    
    def crack_captcha(self, target_base64, search_base64):
        """破解验证码主函数"""
        try:
            # 转换Base64为图像
            target_img = self.base64_to_image(target_base64)
            search_img = self.base64_to_image(search_base64)
            
            if target_img is None or search_img is None:
                return {
                    "success": False,
                    "points": [],
                    "message": "图片转换失败"
                }
            
            # 切割目标图标
            target_icons = self.split_target_icons(target_img)
            if not target_icons:
                return {
                    "success": False,
                    "points": [],
                    "message": "未能提取目标图标"
                }
            
            # 保存原始图片用于调试
            search_img_debug = search_img.copy()
            
            # 查找每个图标的位置
            all_points = []
            for i, icon in enumerate(target_icons):
                points = self.find_icon_locations(search_img, icon)
                if points:
                    all_points.extend(points)
                    
                    # 在调试图片上标记位置
                    for pt in points:
                        cv2.circle(search_img_debug, pt, 5, (0, 0, 255), -1)
                        cv2.putText(search_img_debug, str(i+1), 
                                  (pt[0]+10, pt[1]+10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                                  (0, 0, 255), 2)
            
            # 保存调试图片
            debug_path = self._save_debug_image(search_img_debug, "result")
            
            return {
                "success": len(all_points) > 0,
                "points": all_points,
                "debug_image": debug_path,
                "message": f"找到 {len(all_points)} 个点击位置"
            }
            
        except Exception as e:
            print(f"验证码破解失败: {str(e)}")
            return {
                "success": False,
                "points": [],
                "message": f"验证码破解失败: {str(e)}"
            } 