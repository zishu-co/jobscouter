import ddddocr
import cv2

det = ddddocr.DdddOcr(det=True)

with open("test.jpg", 'rb') as f:
    image = f.read()

bboxes = det.detection(image)
print(bboxes)

im = cv2.imread("test.jpg")

for bbox in bboxes:
    x1, y1, x2, y2 = bbox
    im = cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)

cv2.imwrite("result.jpg", im)
