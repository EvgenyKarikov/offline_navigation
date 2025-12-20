import os, sys
import torch
import open3d as o3d
import numpy as np
from skydiffusion import SkyDiffusion  # Из repo

model = SkyDiffusion.from_pretrained('opendatalab/skydiffusion')  # Загрузка предобученной

def img_to_bev(img_path, depth_path):
    img = np.array(Image.open(img_path))
    depth = np.load(depth_path)
    # Project to 3D (упрощённо, assume camera intrinsics from GSV)
    points = project_depth_to_points(img, depth, fx=500, fy=500, cx=320, cy=320)  # Custom func
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    # Diffusion synthesis to BEV
    bev = model.generate_bev(pcd, resolution=1.0)  # Output: tensor (H,W,3) elevation+RGB
    o3d.io.write_point_cloud("local_pcd.ply", pcd)  # Для viz
    return bev

# Batch process
for file in os.listdir('gsv_images'):
    if file.endswith('.jpg'):
        img_to_bev(f'gsv_images/{file}', f'gsv_images/{file[:-4]}.npy')
# Merge BEVs manually or via SLAM (ORB-SLAM3) for full map