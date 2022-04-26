import osu_file_reader
import tkinter as tk
from tkinter import filedialog
from zipfile import ZipFile

def get_file_path_from_dialog():
  root = tk.Tk()
  root.withdraw()

  file_path = filedialog.askopenfilename()
  return file_path

class OszReader:
  def __init__(self):
    self._file_path = ''
    self._zip = None
    self.data = None
    self.filenames = []

    self._mp3_name = ''
    self._artist = ''
    self._diff_filenames = []
    self._song_name = ''
    self._jpg_names = []
    self._diff_names = []

  def _read_zipfile(self, file_path):
    self._zip = ZipFile(file_path)
    self.filenames = self._zip.namelist()
    data = {filename:self._zip.read(filename) for filename in self.filenames}

    for diff in self.get_diff_filenames():
      data[diff] = osu_file_reader.parse_osu_file(data[diff])
    
    return data

  def filter_data_keys(self, keys):
    return {k: self.data[k] for k in keys}

  def get_data_from_file_dialog(self):
    self._file_path = get_file_path_from_dialog()
    self.data = self._read_zipfile(self._file_path)
    return self.data

  def get_mp3_name(self):
    if not self._mp3_name:
      return next((filename for filename in self.filenames if '.mp3' in filename), '')
    return self._mp3_name

  def get_diff_filenames(self):
    if not self._diff_filenames:
      self._diff_filenames = list(filter(lambda filename: '.osu' in filename, self.filenames))
    return self._diff_filenames

  def get_diff_names(self):
    if not self._diff_names:
      def parse_diff_names_out(diff_filename):
        start_idx = diff_filename.index('[') + 1
        end_idx = diff_filename.index(']', start_idx) - 1
        return diff_filename[start_idx: end_idx + 1]

      self._diff_names = [parse_diff_names_out(diff_filename) for diff_filename in self.get_diff_filenames()]
    return self._diff_names

  def get_jpg_filenames(self):
    if not self._jpg_names:
      self._jpg_names = list(filter(lambda filename: '.jpg' in filename, self.filenames))
    return self._jpg_names

  def get_artist(self):
    if not self._artist:
      self._artist = self.get_diff_filenames()[0].split(' - ')[0]
    return self._artist

  def get_song_name(self):
    if not self._song_name:
      self._song_name = self.get_diff_filenames()[0].split(' - ')[1].split(' (')[0]
    return self._song_name

if __name__ == '__main__':
  osz = OszReader()
  osz.get_data_from_file_dialog()
