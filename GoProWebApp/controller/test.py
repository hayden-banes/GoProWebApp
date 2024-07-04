# import requests

# identifier = '4933'
# base_url = f"http://172.2{identifier[1]}.1{identifier[2]}{identifier[3]}.51:8080"
# response = requests.get(base_url + '/gopro/media/list', timeout=2).json()

# latest_img_dir = response['media'][-1]['d']
# latest_img_name = response['media'][-1]['fs'][-1]['n']
# print(latest_img_dir)
# print(latest_img_name)

from pathlib import Path


dest_path = path = (Path(__file__).parent / "media/images").resolve()
print(dest_path)