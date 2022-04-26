from osz_reader import OszReader
from zipfile import ZipFile
import json
import math

OSU_X_MAX = 640
OSU_Y_MAX = 480
VULNUS_RANGE = 2

def make_vulnus_archive(osz):
  path = f'{osz.get_song_name()}.zip'
  with ZipFile(path, 'x') as z:
    with z.open('meta.json', 'w') as m:
      m.write(generate_meta_json(osz))

    with z.open('cover.jpg', 'w') as jpg:
      jpg.write(osz.data[osz.get_jpg_filenames()[0]])

    with z.open(osz.get_mp3_name(), 'w') as mp3:
      mp3.write(osz.data[osz.get_mp3_name()])

    for diff_name, diff_filename in zip(osz.get_diff_names(), osz.get_diff_filenames()):
      osu_file_data = osz.data[diff_filename]
      with z.open(f'{diff_name}.json', 'w') as vfile:
        vfile.write(generate_diff_json(diff_name, osu_file_data))

def generate_meta_json(osz):
  return json.dumps({
    '_artist': osz.get_artist(), 
    '_difficulties': list(map(lambda diff_name: f'{diff_name}.json', osz.get_diff_names())), 
    '_mappers': ['LypTea'], 
    '_music': osz.get_mp3_name(), 
    '_title': osz.get_song_name(), 
    '_version': 1}).encode('utf-8')

def generate_diff_json(diff_name, osu_file_data):
  return json.dumps({
    "_approachDistance": 50, 
    "_approachTime": 1, 
    "_name": diff_name.rstrip('.osu'),
    "_notes": convert_notes(osu_file_data)}).encode('utf-8')

def convert_coords(x, y, grid = 9):
  def calculate_point(percentage):
    return transform_range(percentage, [0, 1], [0, grid - 1]) * (VULNUS_RANGE / (grid - 1)) - 1

  return calculate_point(int(x) / OSU_X_MAX), calculate_point(int(y) / OSU_Y_MAX)

def convert_time(time):
  return int(time) / 1000

def transform_range(value, r1, r2):
  return round(((value - r1[0]) / (r1[1] - r1[0])) * (r2[1] - r2[0]) + r2[0])

def sqrt_curve(num, limit=100):
  if limit == 100:
    return math.sqrt(num) * 10

  transform_to_100 = transform_range(num, [0, limit], [0, 100])
  sqrt_curved_num = math.sqrt(transform_to_100) * 10
  return transform_range(sqrt_curved_num, [0, 100], [0, limit])

def convert_notes(osu_file_data, grid = 9):
  """ Converts osu coordinates -> vulnus notes based on a 9x9 grid
  - Scales/transforms all osu coordinates from [0, max_x_coord] -> [0, OSU_X_MAX] for x and y
  - Square root curves twice
  - Maps osu to vulnus notes

  We do this so the notes are as close to the borders as possible
  """

  hit_objects = osu_file_data['HitObjects']
  notes = []
  max_x, max_y = 0, 0

  for ho in hit_objects:
    max_x = max(max_x, int(ho['x']))
    max_y = max(max_y, int(ho['y']))

  for ho in hit_objects:
    centered_x, centered_y = transform_range(int(ho['x']), [0, max_x], [-OSU_X_MAX // 2, OSU_X_MAX // 2]), \
      transform_range(int(ho['y']), [0, max_y], [-OSU_Y_MAX // 2, OSU_Y_MAX // 2])
    is_x_pos, is_y_pos = centered_x > 0, centered_y > 0
    
    converted_x, converted_y = convert_coords(
      transform_range(sqrt_curve(sqrt_curve(abs(centered_x), OSU_X_MAX // 2), OSU_X_MAX // 2) * (1 if is_x_pos else -1), [-OSU_X_MAX // 2, OSU_X_MAX // 2], [0, OSU_X_MAX]), 
      transform_range(sqrt_curve(sqrt_curve(abs(centered_y), OSU_Y_MAX // 2), OSU_Y_MAX // 2) * (1 if is_y_pos else -1), [-OSU_Y_MAX // 2, OSU_Y_MAX // 2], [0, OSU_Y_MAX]),
      grid = grid)
    notes.append({
      '_time': convert_time(ho['time']),
      '_x': converted_x, '_y': converted_y})
  
  return notes

if __name__ == '__main__':
  osz = OszReader()
  osz.get_data_from_file_dialog()
  make_vulnus_archive(osz)
