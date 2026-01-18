---
date: 2024-07-09
status: Permanent
tags:
  - Study/Camera
aliases:
  - 시간 동기화
  - TimeSync
keywords: 
related notes: 
reference: 
author: 
url: 
dg-publish: true
---
# EXIF (EXchangeble Image file Format)
- 휴대폰 및 카메라로 촬영한 이미지에는 EXIF 라고 하는 메타정보가 있으며, 이미지 이름, 크기, 촬영일시, 카메라 정보, GPS, 노출 정보 등 다양한 정보가 있음
- Python 에서는 PIL 패키지를 사용하여 EXIF 를 읽을 수 있음

## EXIF 정보 출력
- PIL 패키지로 이미지 파일 읽은 뒤, tag 정보 (`tag_id`) 를 (`key, value`) 형태로 읽기

```python
from PIL import Image 
from PIL.ExifTags import TAGS 

def get_image_exif(image): 
	img = Image.open(image) 
	img_info = img._getexif() 
	
	for tag_id in img_info: 
		tag = TAGS.get(tag_id, tag_id) 
		data = img_info.get(tag_id) 
		print(f'{tag} : {data}') 
	img.close() 
	
image ='20150404_095727.jpg' 
print(get_image_exif(image))
```

![[Attachments/General/Pasted image 20240709162213.png]]

### 이미지 촬영 일시만 출력
- "DateTime, DateTimeOriginal, DateTimeDigitized" Tag 정보를 통해 촬영 일시 확인

```python
from PIL import Image 
from PIL.ExifTags 
import TAGS 

def get_image_exif(image): 
	img = Image.open(image) 
	img_info = img._getexif() 
	
	for tag_id in img_info:
		tag = TAGS.get(tag_id, tag_id) 
		data = img_info.get(tag_id) 
		
		if tag == 'DateTime' or tag =='DateTimeOriginal': 
			print(f'{tag} : {data}') 
	img.close()
	
image ='20150404_095727.jpg' 
print(get_image_exif(image))
```

![[Attachments/General/Pasted image 20240709162416.png]]

