# -*- coding: utf-8 -*-
import unittest
from ocr import CaptchaCracker
import os
import base64
import cv2
import numpy as np

class TestCaptchaCracker(unittest.TestCase):
    def setUp(self):
        self.cracker = CaptchaCracker()
        self.debug_dir = "debug_images"
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
    
    def test_crack_captcha(self):
        """测试验证码破解"""
        # 读取测试图片
        target_path = "./target_imgs.png"
        search_path = "./shibie.png"
        
        if not os.path.exists(target_path) or not os.path.exists(search_path):
            self.skipTest("测试图片不存在")
        
        with open(target_path, "rb") as f:
            target_base64 = base64.b64encode(f.read()).decode()
            
        with open(search_path, "rb") as f:
            search_base64 = base64.b64encode(f.read()).decode()
        
        # 测试破解
        result = self.cracker.crack_captcha(target_base64, search_base64)
        
        self.assertIsNotNone(result)
        self.assertIn("success", result)
        self.assertIn("points", result)
        self.assertIn("message", result)
        self.assertIn("debug_image", result)
        
        if result["success"]:
            print(f"找到点击位置: {result['points']}")
            print(f"调试图片保存在: {result['debug_image']}")

    def test_single_icon_match(self):
        """测试单个图标的匹配"""
        # 读取目标图标和搜索图片
        target_path = "./target_icon_0.png"
        search_path = "./shibie.png"
        
        if not os.path.exists(target_path) or not os.path.exists(search_path):
            self.skipTest("测试图片不存在")
        
        # 读取图片
        target_icon = cv2.imread(target_path)
        search_img = cv2.imread(search_path)
        
        # 保存原始图片
        cv2.imwrite(os.path.join(self.debug_dir, "1_target_original.png"), target_icon)
        cv2.imwrite(os.path.join(self.debug_dir, "1_search_original.png"), search_img)
        
        # 转为灰度图
        target_gray = cv2.cvtColor(target_icon, cv2.COLOR_BGR2GRAY)
        search_gray = cv2.cvtColor(search_img, cv2.COLOR_BGR2GRAY)
        
        # 保存灰度图
        cv2.imwrite(os.path.join(self.debug_dir, "2_target_gray.png"), target_gray)
        cv2.imwrite(os.path.join(self.debug_dir, "2_search_gray.png"), search_gray)
        
        # 尝试不同的二值化方法
        # 1. 普通二值化
        _, target_bin1 = cv2.threshold(target_gray, 240, 255, cv2.THRESH_BINARY_INV)
        _, search_bin1 = cv2.threshold(search_gray, 240, 255, cv2.THRESH_BINARY_INV)
        cv2.imwrite(os.path.join(self.debug_dir, "3_target_bin_normal.png"), target_bin1)
        cv2.imwrite(os.path.join(self.debug_dir, "3_search_bin_normal.png"), search_bin1)
        
        # 2. Otsu二值化
        _, target_bin2 = cv2.threshold(target_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        _, search_bin2 = cv2.threshold(search_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        cv2.imwrite(os.path.join(self.debug_dir, "4_target_bin_otsu.png"), target_bin2)
        cv2.imwrite(os.path.join(self.debug_dir, "4_search_bin_otsu.png"), search_bin2)
        
        # 3. 自适应二值化
        target_bin3 = cv2.adaptiveThreshold(target_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY_INV, 11, 2)
        search_bin3 = cv2.adaptiveThreshold(search_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY_INV, 11, 2)
        cv2.imwrite(os.path.join(self.debug_dir, "5_target_bin_adaptive.png"), target_bin3)
        cv2.imwrite(os.path.join(self.debug_dir, "5_search_bin_adaptive.png"), search_bin3)
        
        # 对每种二值化结果进行模板匹配
        for i, (target_bin, search_bin, method_name) in enumerate([
            (target_bin1, search_bin1, "normal"),
            (target_bin2, search_bin2, "otsu"),
            (target_bin3, search_bin3, "adaptive")
        ]):
            # 模板匹配
            result = cv2.matchTemplate(search_bin, target_bin, cv2.TM_CCOEFF_NORMED)
            
            # 保存匹配结果热力图
            result_norm = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            cv2.imwrite(os.path.join(self.debug_dir, f"6_match_heatmap_{method_name}.png"), result_norm)
            
            # 设置阈值
            threshold = 0.1
            locations = np.where(result >= threshold)
            
            # 获取匹配位置
            points = []
            h, w = target_bin.shape
            debug_img = search_img.copy()
            
            for pt in zip(*locations[::-1]):
                # 计算中心点
                center_x = pt[0] + w//2
                center_y = pt[1] + h//2
                points.append((center_x, center_y))
                
                # 在调试图像上标记
                cv2.rectangle(debug_img, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
                cv2.circle(debug_img, (center_x, center_y), 5, (0, 0, 255), -1)
                cv2.putText(debug_img, f"({center_x}, {center_y})", 
                          (center_x+10, center_y+10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # 保存匹配结果图
            cv2.imwrite(os.path.join(self.debug_dir, f"7_match_result_{method_name}.png"), debug_img)
            
            # 打印匹配结果
            print(f"\n{method_name.upper()} 二值化方法找到 {len(points)} 个匹配位置:")
            for pt in points:
                print(f"坐标: {pt}")
        
        # 验证是否找到匹配位置
        self.assertTrue(len(points) > 0, "未找到匹配位置")

    def test_feature_matching(self):
        """测试不同的特征匹配方法"""
        # 读取图片
        target_path = "./target_icon_0.png"
        search_path = "./shibie.png"
        
        if not os.path.exists(target_path) or not os.path.exists(search_path):
            self.skipTest("测试图片不存在")
        
        target_img = cv2.imread(target_path)
        search_img = cv2.imread(search_path)
        
        # 转为灰度图
        target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
        search_gray = cv2.cvtColor(search_img, cv2.COLOR_BGR2GRAY)
        
        # 定义特征检测器
        detectors = {
            'sift': cv2.SIFT_create(),
            'orb': cv2.ORB_create(),
            # 'surf': cv2.xfeatures2d.SURF_create(),  # SURF是专利算法，需要额外编译OpenCV
            'akaze': cv2.AKAZE_create(),
            'brisk': cv2.BRISK_create()
        }
        
        for name, detector in detectors.items():
            print(f"\n测试 {name.upper()} 特征匹配:")
            
            # 检测关键点和描述符
            kp1, des1 = detector.detectAndCompute(target_gray, None)
            kp2, des2 = detector.detectAndCompute(search_gray, None)
            
            if des1 is None or des2 is None:
                print(f"{name} 未检测到特征点")
                continue
            
            # 绘制关键点
            target_kp = target_img.copy()
            search_kp = search_img.copy()
            cv2.drawKeypoints(target_gray, kp1, target_kp)
            cv2.drawKeypoints(search_gray, kp2, search_kp)
            cv2.imwrite(os.path.join(self.debug_dir, f"8_{name}_target_keypoints.png"), target_kp)
            cv2.imwrite(os.path.join(self.debug_dir, f"8_{name}_search_keypoints.png"), search_kp)
            
            # 特征匹配
            if name == 'orb' or name == 'brisk':
                # ORB和BRISK使用汉明距离
                matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            else:
                # 其他使用L2距离
                matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
            
            matches = matcher.match(des1, des2)
            
            # 根据距离排序
            matches = sorted(matches, key=lambda x: x.distance)
            
            # 选择最佳匹配
            good_matches = matches[:10]  # 取前10个最佳匹配
            
            # 获取匹配点坐标
            points = []
            debug_img = search_img.copy()
            
            for match in good_matches:
                # 获取关键点坐标
                x, y = kp2[match.trainIdx].pt
                center_x, center_y = int(x), int(y)
                points.append((center_x, center_y))
                
                # 在图像上标记
                cv2.circle(debug_img, (center_x, center_y), 5, (0, 0, 255), -1)
                cv2.putText(debug_img, f"D:{match.distance:.1f}", 
                          (center_x+10, center_y+10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # 绘制匹配结果
            match_img = cv2.drawMatches(target_img, kp1, search_img, kp2, good_matches, None,
                                      flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            
            # 保存结果
            cv2.imwrite(os.path.join(self.debug_dir, f"9_{name}_matches.png"), match_img)
            cv2.imwrite(os.path.join(self.debug_dir, f"9_{name}_points.png"), debug_img)
            
            # 打印结果
            print(f"找到 {len(points)} 个匹配点:")
            for i, pt in enumerate(points):
                print(f"点 {i+1}: {pt}, 距离: {good_matches[i].distance:.1f}")

    def test_preprocessing(self):
        """测试不同的图像预处理方法"""
        target_path = "./target_icon_0.png"
        search_path = "./shibie.png"
        
        if not os.path.exists(target_path) or not os.path.exists(search_path):
            self.skipTest("测试图片不存在")
        
        # 读取图片
        target_img = cv2.imread(target_path)
        search_img = cv2.imread(search_path)
        
        # 保存原始图片
        cv2.imwrite(os.path.join(self.debug_dir, "1_target_original.png"), target_img)
        cv2.imwrite(os.path.join(self.debug_dir, "1_search_original.png"), search_img)
        
        # 1. 边缘检测
        target_edges = cv2.Canny(target_img, 100, 200)
        search_edges = cv2.Canny(search_img, 100, 200)
        cv2.imwrite(os.path.join(self.debug_dir, "2_target_edges.png"), target_edges)
        cv2.imwrite(os.path.join(self.debug_dir, "2_search_edges.png"), search_edges)
        
        # 2. 轮廓检测
        target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
        search_gray = cv2.cvtColor(search_img, cv2.COLOR_BGR2GRAY)
        
        # 使用高斯模糊减少噪声
        target_blur = cv2.GaussianBlur(target_gray, (5, 5), 0)
        search_blur = cv2.GaussianBlur(search_gray, (5, 5), 0)
        cv2.imwrite(os.path.join(self.debug_dir, "3_target_blur.png"), target_blur)
        cv2.imwrite(os.path.join(self.debug_dir, "3_search_blur.png"), search_blur)
        
        # 使用自适应阈值
        target_thresh = cv2.adaptiveThreshold(
            target_blur, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        search_thresh = cv2.adaptiveThreshold(
            search_blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        cv2.imwrite(os.path.join(self.debug_dir, "4_target_thresh.png"), target_thresh)
        cv2.imwrite(os.path.join(self.debug_dir, "4_search_thresh.png"), search_thresh)
        
        # 3. 形态学操作
        kernel = np.ones((3,3), np.uint8)
        target_morph = cv2.morphologyEx(target_thresh, cv2.MORPH_CLOSE, kernel)
        search_morph = cv2.morphologyEx(search_thresh, cv2.MORPH_CLOSE, kernel)
        cv2.imwrite(os.path.join(self.debug_dir, "5_target_morph.png"), target_morph)
        cv2.imwrite(os.path.join(self.debug_dir, "5_search_morph.png"), search_morph)
        
        # 4. 轮廓检测和绘制
        target_contours, _ = cv2.findContours(target_morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        search_contours, _ = cv2.findContours(search_morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        target_draw = target_img.copy()
        search_draw = search_img.copy()
        
        cv2.drawContours(target_draw, target_contours, -1, (0,255,0), 2)
        cv2.drawContours(search_draw, search_contours, -1, (0,255,0), 2)
        cv2.imwrite(os.path.join(self.debug_dir, "6_target_contours.png"), target_draw)
        cv2.imwrite(os.path.join(self.debug_dir, "6_search_contours.png"), search_draw)
        
        # 5. 模板匹配
        methods = [
            ('TM_CCOEFF', cv2.TM_CCOEFF),
            ('TM_CCOEFF_NORMED', cv2.TM_CCOEFF_NORMED),
            ('TM_CCORR', cv2.TM_CCORR),
            ('TM_CCORR_NORMED', cv2.TM_CCORR_NORMED),
            ('TM_SQDIFF', cv2.TM_SQDIFF),
            ('TM_SQDIFF_NORMED', cv2.TM_SQDIFF_NORMED)
        ]
        
        for method_name, method in methods:
            print(f"\n测试 {method_name} 匹配方法:")
            result = cv2.matchTemplate(search_morph, target_morph, method)
            
            # 对于TM_SQDIFF和TM_SQDIFF_NORMED，最小值是最佳匹配
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                top_left = min_loc
                match_val = min_val
            else:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                top_left = max_loc
                match_val = max_val
            
            h, w = target_morph.shape
            bottom_right = (top_left[0] + w, top_left[1] + h)
            center = (top_left[0] + w//2, top_left[1] + h//2)
            
            result_img = search_img.copy()
            cv2.rectangle(result_img, top_left, bottom_right, (0,255,0), 2)
            cv2.circle(result_img, center, 5, (0,0,255), -1)
            cv2.putText(result_img, f"Match: {match_val:.3f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            
            cv2.imwrite(os.path.join(self.debug_dir, f"7_match_{method_name}.png"), result_img)
            print(f"匹配值: {match_val:.3f}, 中心点: {center}")

    def test_direct_match(self):
        """直接进行模板匹配测试"""
        target_path = "./target_icon_0.png"
        search_path = "./shibie.png"
        
        if not os.path.exists(target_path) or not os.path.exists(search_path):
            self.skipTest("测试图片不存在")
        
        # 读取图片
        target_img = cv2.imread(target_path)
        search_img = cv2.imread(search_path)
        
        # 保存原始图片
        cv2.imwrite(os.path.join(self.debug_dir, "1_target_original.png"), target_img)
        cv2.imwrite(os.path.join(self.debug_dir, "1_search_original.png"), search_img)
        
        # 定义不同的匹配方法
        methods = [
            ('TM_CCOEFF', cv2.TM_CCOEFF),
            ('TM_CCOEFF_NORMED', cv2.TM_CCOEFF_NORMED),
            ('TM_CCORR', cv2.TM_CCORR),
            ('TM_CCORR_NORMED', cv2.TM_CCORR_NORMED),
            ('TM_SQDIFF', cv2.TM_SQDIFF),
            ('TM_SQDIFF_NORMED', cv2.TM_SQDIFF_NORMED)
        ]
        
        for method_name, method in methods:
            print(f"\n测试 {method_name} 匹配方法:")
            
            # 直接进行模板匹配
            result = cv2.matchTemplate(search_img, target_img, method)
            
            # 保存匹配结果热力图
            result_norm = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            cv2.imwrite(os.path.join(self.debug_dir, f"2_heatmap_{method_name}.png"), result_norm)
            
            # 获取最佳匹配位置
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                top_left = min_loc
                match_val = min_val
            else:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                top_left = max_loc
                match_val = max_val
            
            # 计算匹配区域
            h, w = target_img.shape[:2]
            bottom_right = (top_left[0] + w, top_left[1] + h)
            center = (top_left[0] + w//2, top_left[1] + h//2)
            
            # 在原图上标记匹配位置
            result_img = search_img.copy()
            cv2.rectangle(result_img, top_left, bottom_right, (0,255,0), 2)
            cv2.circle(result_img, center, 5, (0,0,255), -1)
            cv2.putText(result_img, f"Match: {match_val:.3f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            
            # 保存结果
            cv2.imwrite(os.path.join(self.debug_dir, f"3_result_{method_name}.png"), result_img)
            print(f"匹配值: {match_val:.3f}, 中心点: {center}")

if __name__ == "__main__":
    unittest.main() 