import json
import datetime
import requests

def get_about(about_url):

  print(f"Fetching {about_url}")
  try:
    response = requests.get(about_url, timeout=5)
    response.raise_for_status()  # Raise an error if response code is not 2xx
  except requests.exceptions.RequestException as e:
    print(f"  {e}")
    return e
  print(f"  Fetched {about_url}")

  try:
    data = json.loads(response.text)
  except json.JSONDecodeError as e:
    print(f"  Error parsing JSON from {about_url}:\n  {e}")
    return e

  return data

def equivalent_dicts(servers, about):
  diff = False
  for k1, v1 in servers.items():
    if k1.startswith("x_"): continue
    if k1 not in about:
      print(f"  key '{k1}' not in /about response")
      #diff = True
  print("  ---")
  for k2, v2 in about.items():
    if k2.startswith("x_"): continue
    if k2 not in servers:
      print(f"  key '{k2}' not in /about response")
      diff = True
    if diff == False and servers[k2] != v2:
      print(f"  servers[{k2}] != about[{k2}]")
      diff = True
  return diff

def write(fname, data):
  print(f"Writing {fname}")
  with open(fname, 'w') as f:
    f.write(data)

fname_in   = '../servers.new.json'
fname_out  = '../servers.new.updated.json'
fname_all1 = '../all_.txt.new'
fname_all2 = '../all.txt.new'

with open(fname_in) as f:
  print(f"Reading {fname_in}")
  servers = json.load(f)

changed = False
all_file_str1 = ""
all_file_str2 = ""
for idx in range(len(servers['servers'])):
  server = servers['servers'][idx]
  if server['id'] == 'CSA':
    # https://github.com/hapi-server/server-issues/issues/18
    continue
  about = get_about(server['url'] + '/about') 
  server['x_LastUpdateAttempt'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
  if isinstance(about, Exception):
    server['x_LastUpdateError'] = str(about)
  else:
    server['x_LastUpdateError'] = False
    del about["HAPI"]
    del about["status"]
    if equivalent_dicts(server, about) == False:
      print(f"  No difference between servers.json[{server['id']}] and {server['url']}")
    else:
      changed = True
      print(f"  Difference between servers.json[{server['id']}] and {server['url']}/about")
      server["x_LastUpdateChange"] = server["x_LastUpdateAttempt"]
      print(f"servers.json[{server['id']}]")
      print(json.dumps(server, indent=2))
      print(f"{server['url']}/about")
      print(json.dumps(about, indent=2))
      servers['servers'][idx] = {**server, **about}

  all_file_str1 += f"{server['url']}, {server['title']}, {server['id']}, {server['contact']}, {server['contactID']}\n"
  all_file_str2 += f"{server['url']}\n"

if changed == False:
  print(f"No changes to servers.json. Updating only x_ fields.")

servers = json.dumps(servers, ensure_ascii=False, separators=(',', ': '), indent=2)
write(fname_out, servers)

if changed == True:
  write(fname_all1, all_file_str1)
  write(fname_all2, all_file_str2)
else:
  print(f"No changes to servers.json. Not writing {fname_all1} or {fname_all2}.")