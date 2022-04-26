def get_section_indexes(osu_file_lines, section_name):
  try:
    idx = osu_file_lines.index(section_name) + 1
    end_idx = osu_file_lines.index('', idx)
    return idx, end_idx
  except ValueError:
    return -1, -1

def parse_kv_section(osu_file_lines, section_name):
  idx, end_idx = get_section_indexes(osu_file_lines, section_name)
  section = {}
  
  for i in range(idx, end_idx):
    key, value = osu_file_lines[i].split(':')
    section[key] = value.strip()

  return section

def parse_list_section(osu_file_lines, section_name):
  idx, end_idx = get_section_indexes(osu_file_lines, section_name)
  return osu_file_lines[idx:end_idx]

def parse_comma_separated(osu_file_lines, section_name, syntax):
  idx, end_idx = get_section_indexes(osu_file_lines, section_name)
  section = []

  for i in range(idx, end_idx):
    values = osu_file_lines[i].split(',')
    section.append(dict(zip(syntax, values)))

  return section

def parse_osu_file(osu_file):
  osu_file_str = osu_file.decode('utf-8')
  osu_file_lines = osu_file_str.split('\r\n')
  parsed_osu_file = {}

  parsed_osu_file['General'] = parse_kv_section(osu_file_lines, '[General]')
  parsed_osu_file['Editor'] = parse_kv_section(osu_file_lines, '[Editor]')
  parsed_osu_file['Metadata'] = parse_kv_section(osu_file_lines, '[Metadata]')
  parsed_osu_file['Difficulty'] = parse_kv_section(osu_file_lines, '[Difficulty]')
  # this one isn't parsed correctly
  parsed_osu_file['Events'] = parse_list_section(osu_file_lines, '[Events]') 
  parsed_osu_file['TimingPoints'] = parse_comma_separated(osu_file_lines, '[TimingPoints]',
    ['time','beatLength','meter','sampleSet','sampleIndex','volume','uninherited','effects']) 
  parsed_osu_file['Colours'] = parse_kv_section(osu_file_lines, '[Colours]') 
  parsed_osu_file['HitObjects'] = parse_comma_separated(osu_file_lines, '[HitObjects]',
    ['x','y','time','type','hitSound','objectParams','hitSample']) 

  return parsed_osu_file
  