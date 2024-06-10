import requests
import sys
sys.path.append('../../')
from tools.saveto.save_json import save_json
from datetime import datetime
import os
import pyproj
from shapely.geometry import LineString


offset = 0
max_offset = 500000

all_data = []
while offset < max_offset:
    url_base = f'https://gisportal.binamarga.pu.go.id/arcgis/rest/services/ELRS/IRI_2_2023/MapServer/0/query?f=json&where=(1%3D1)%20AND%20(1%3D1)&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=OBJECTID%20ASC&outSR=102100&resultOffset={offset}&resultRecordCount=2000'
    print(f'Offset: {offset}')
    print(url_base)
    response = requests.get(url_base)
    print(response.url)
    
    if response.status_code == 200:
        data = response.json()
        
        features = data['features']
        for feature in features:
            atributes = feature['attributes']

            atributes['MEAN_IRI_DETAIL'] = atributes['MEAN_IRI']
            if atributes['MEAN_IRI_DETAIL'] < 4:
                atributes['MEAN_IRI_DETAIL'] = 'Baik'
            elif atributes['MEAN_IRI_DETAIL'] >= 4 and atributes['MEAN_IRI_DETAIL'] < 8:
                atributes['MEAN_IRI_DETAIL'] = 'Sedang'
            elif atributes['MEAN_IRI_DETAIL'] >= 8 and atributes['MEAN_IRI_DETAIL'] < 12:
                atributes['MEAN_IRI_DETAIL'] = 'Rusak Ringan'
            elif atributes['MEAN_IRI_DETAIL'] >= 12:
                atributes['MEAN_IRI_DETAIL'] = 'Rusak Berat'

            atributes['MEAN_IRI_POK_DETAIL'] = atributes['MEAN_IRI_POK']
            if atributes['MEAN_IRI_POK_DETAIL'] < 4:
                atributes['MEAN_IRI_POK_DETAIL'] = 'Baik'
            elif atributes['MEAN_IRI_POK_DETAIL'] >= 4 and atributes['MEAN_IRI_POK_DETAIL'] < 8:
                atributes['MEAN_IRI_POK_DETAIL'] = 'Sedang'
            elif atributes['MEAN_IRI_POK_DETAIL'] >= 8 and atributes['MEAN_IRI_POK_DETAIL'] < 12:
                atributes['MEAN_IRI_POK_DETAIL'] = 'Rusak Ringan'
            elif atributes['MEAN_IRI_POK_DETAIL'] >= 12:
                atributes['MEAN_IRI_POK_DETAIL'] = 'Rusak Berat'



            geometry = feature['geometry']['paths']
            for path in geometry:
                xs = geometry
                for coordinate in xs:
                    x = coordinate[0][0]
                    y = coordinate[0][1]

                    x2 = coordinate[1][0]
                    y2 = coordinate[1][1]
                    wgs84 = pyproj.Proj(projparams = 'epsg:4326')
                    InputGrid = pyproj.Proj(projparams = 'epsg:3857')

                    corcor1 = pyproj.transform(InputGrid, wgs84, x, y)
                    corcor2 = pyproj.transform(InputGrid, wgs84, x2, y2)
                    
                    corcor = LineString([corcor1, corcor2])
                    print(type(corcor))

                    data_loop = {
                            'attributes': atributes,
                            'geometry': {
                                'type' : 'LineString',
                                'coordinates': list(corcor.coords)
                            }
                        }
                    all_data.append(data_loop)

    offset += 2000

dir = os.path.join('data')
os.makedirs(dir, exist_ok=True)

filename = 'data_jalan_rusak_binamarga.json'

local = f'YOUR LOCAL PATH/{filename}'
s3_path = f'YOUR S3 PATH/{filename}'
data = {
    'link': 'https://binamarga.pu.go.id/kondisi_jalan.html',
    'domain': 'binamarga.pu.go.id',
    'crawling_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'crawling_time_epoch': int(datetime.now().timestamp()),
    'path_data_raw': s3_path,
    'path_data_clean': None,
    'data' : all_data
}
save_json(data, os.path.join('data', filename))


