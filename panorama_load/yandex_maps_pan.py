import os,sys
from rich import print

import numpy as np
from PIL import Image
import cv2
from streetlevel import streetview
import equilib
from equilib import equi2equi

def pano_yandex(lat, lon, zoom=2):
    
    result = {
        'image':None,
        'pitch':0,
        'roll':0,
        'yaw':0,
        'elevation':0,
        'heading':0,
        'depth':None,
        'lat':lat,
        'lon':lon,
              }
    pano = streetview.find_panorama(lat, lon)
    if pano is None:
        print(f"Панорама не найдена по {lat}, {lon}")
        return result
    
     # Скачивание основной
    img = streetview.get_panorama(pano, zoom=zoom)  # Высочайшее разрешение
    result['yaw'] = pano.heading if pano.heading else 0  # В радианах; конверт в градусы если нужно: np.degrees(heading)
    result['pitch'] = pano.pitch
    result['roll'] = pano.roll
    result['elevation'] = pano.elevation      
    result['lat'] = pano.lat
    result['lon'] = pano.lon
    result['image'] = img    
    return result
    

# def fetch_yandex(lat, lon, num_neighbors=5, output_dir='tmp'):
#     """
#     Ищет панораму по lat/lon, скачивает её + neighbors (ближайшие).
#     Возвращает список (img, depth, heading) для скачанных.
#     """
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
    
#     results = []
#     # Основная панорама
#     pano = streetview.find_panorama(lat, lon)
#     if pano is None:
#         print(f"Панорама не найдена по {lat}, {lon}")
#         return results
    
#     # Скачивание основной
#     img = streetview.get_panorama(pano, zoom=5)  # Высочайшее разрешение
#     heading = pano.heading if pano.heading else 0  # В радианах; конверт в градусы если нужно: np.degrees(heading)
    
#     # Сохранение
#     img_path = os.path.join(output_dir, f"pano_{pano.id}.jpg")
#     img.save(img_path, quality=95)
    
#     # Depth (на undistorted; для панорам — crop center или full, но full distorted)
#     depth_raw = depth_model(img,use_fast=True)['depth']
#     depth = np.array(depth_raw)
    
#     inps = image_processor(images=img, 
#                            return_tensors="pt").to(device)
#     with torch.no_grad():
#         outputs = model(**inps)
#     post_processed_output = image_processor.post_process_depth_estimation(outputs, 
#                                                                           target_sizes=[(img.height, img.width)],
#                                                                           )
#     field_of_view = post_processed_output[0]["field_of_view"]
#     focal_length = post_processed_output[0]["focal_length"]
#     depth = post_processed_output[0]["predicted_depth"]    
#     depth = (depth - depth.min()) / (depth.max() - depth.min())
#     depth = depth * 255.
#     depth = depth.detach().cpu().numpy()
#     depth = Image.fromarray(depth.astype("uint8"))
#     np.save(img_path.replace('.jpg', '.npy'), depth)
    
#     results.append((img, depth, np.degrees(heading) if heading else 0))
#     print(f"Скачано основная: {pano.id}, heading: {results[-1][2]}°")
    
#     # Neighbors (ближайшие панорамы для sequence)
#     if pano.neighbors:
#         for i, neighbor in enumerate(pano.neighbors[:num_neighbors]):
#             n_img = streetview.get_panorama(neighbor, zoom=0)
#             n_heading = neighbor.heading if neighbor.heading else 0
            
#             n_path = os.path.join(output_dir, f"neighbor_{i}_{neighbor.id}.jpg")
#             n_img.save(n_path, quality=95)
            
#             n_depth_raw = depth_model(n_img)['depth']
#             n_depth = np.array(n_depth_raw)
#             np.save(n_path.replace('.jpg', '.npy'), n_depth)
            
#             results.append((n_img, n_depth, np.degrees(n_heading) if n_heading else 0))
#             print(f"Скачано neighbor {i}: {neighbor.id}, heading: {results[-1][2]}°")
    
#     return results

if __name__=="__main__":
    lat, lon = 50.581450, 36.591707
    fetched = pano_yandex(lat, lon, zoom=2)
    
    fetched_image = fetched['image']
    
    rot ={
        'roll':0*fetched['roll'],
        'pitch':fetched['pitch'],
        'yaw':fetched['yaw']
    }
    
    equi = np.array(fetched_image)
    equi = equi[:,:,::-1]
    rotated = equi2equi(equi,rots=rot,mode='bilinear')
    
    rotated_image = Image.fromarray(rotated[:,:,::-1])
    
    pass