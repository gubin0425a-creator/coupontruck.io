import socket, json, os, struct, sys
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

active_port_file = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort')
with open(active_port_file, 'r') as f:
    lines = [l.strip() for l in f]
port, path = lines[0], lines[1]

def send_frame(s, msg):
    data = msg.encode('utf-8')
    length = len(data)
    frame = bytearray([0x81])
    mask = os.urandom(4)
    if length <= 125:
        frame.append(0x80 | length)
    elif length <= 65535:
        frame.append(0x80 | 126)
        frame.extend(struct.pack('!H', length))
    else:
        frame.append(0x80 | 127)
        frame.extend(struct.pack('!Q', length))
    frame.extend(mask)
    for i, b in enumerate(data):
        frame.append(b ^ mask[i % 4])
    s.sendall(frame)

def recv_frame(s):
    hdr = s.recv(2)
    if not hdr: return None
    b1, b2 = hdr[0], hdr[1]
    length = b2 & 0x7F
    if length == 126:
        length = struct.unpack('!H', s.recv(2))[0]
    elif length == 127:
        length = struct.unpack('!Q', s.recv(8))[0]
    data = b''
    while len(data) < length:
        chunk = s.recv(length - len(data))
        if not chunk: break
        data += chunk
    return data.decode('utf-8', errors='replace')

s = socket.socket()
s.connect(('127.0.0.1', int(port)))
req = (
    f'GET {path} HTTP/1.1\r\n'
    f'Host: 127.0.0.1:{port}\r\n'
    'Upgrade: websocket\r\n'
    'Connection: Upgrade\r\n'
    'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n'
    'Sec-WebSocket-Version: 13\r\n\r\n'
)
s.sendall(req.encode('utf-8'))
resp = s.recv(1024)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'coupons.json')
OFFERS_FILE = os.path.join(BASE_DIR, 'data', 'offers.json')

def update_airalo_in_db(code, ref_url):
    print(f'\n🎉 [자동 감지 성공] 에어알로 추천코드 추출 완료: {code} | {ref_url}')
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data.get('categories', {}).get('travel', {}).get('items', []):
            if '에어알로' in item.get('name', '') or 'Airalo' in item.get('name', ''):
                item['code'] = code
                item['url'] = ref_url
                item['badge'] = '$3 할인'
                item['desc'] = '전세계 200+ 국가 eSIM 첫 구매 시 US$3 즉시할인 추천코드'
                item['is_active'] = True
                item['expires'] = '2026-12-31'
                item['type'] = 'REFERRAL'
                break
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print('✅ data/coupons.json 에어알로 업데이트 완료!')

    if os.path.exists(OFFERS_FILE):
        with open(OFFERS_FILE, 'r', encoding='utf-8') as f:
            offers = json.load(f)
        for o in offers:
            if '에어알로' in o.get('title', '') or 'Airalo' in o.get('title', ''):
                o['coupon_code'] = code
                o['target_url'] = ref_url
                o['affiliate_url'] = ref_url
                o['end_date'] = '2026-12-31'
                o['badge'] = '$3 할인'
                o['type'] = 'REFERRAL'
                break
        with open(OFFERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(offers, f, ensure_ascii=False, indent=2)
        print('✅ data/offers.json 에어알로 업데이트 완료!')

cmd_id = 1
def call_api(s, method, params=None, session_id=None):
    global cmd_id
    cmd = {'id': cmd_id, 'method': method}
    if params: cmd['params'] = params
    if session_id: cmd['sessionId'] = session_id
    send_frame(s, json.dumps(cmd))
    my_id = cmd_id
    cmd_id += 1
    s.settimeout(6.0)
    while True:
        msg = recv_frame(s)
        if not msg: return None
        try:
            res = json.loads(msg)
            if res.get('id') == my_id:
                return res
        except:
            pass

print('🔍 에어알로(Airalo) 탭 모니터링 시작... (로그인 대기 중)')
for attempt in range(60):
    try:
        targets_res = call_api(s, 'Target.getTargets')
        airalo_tid = None
        current_url = None
        for t in targets_res.get('result', {}).get('targetInfos', []):
            if 'airalo.com' in t.get('url', ''):
                airalo_tid = t.get('targetId')
                current_url = t.get('url', '')
                break

        if airalo_tid and current_url and 'login' not in current_url:
            print(f'로그인 감지됨! 현재 URL: {current_url}')
            att_res = call_api(s, 'Target.attachToTarget', {'targetId': airalo_tid, 'flatten': True})
            sess_id = att_res.get('result', {}).get('sessionId') if att_res else None
            if sess_id:
                if 'share-and-earn' not in current_url:
                    call_api(s, 'Page.navigate', {'url': 'https://www.airalo.com/ko/share-and-earn'}, session_id=sess_id)
                    import time
                    time.sleep(3)

                eval_script = "JSON.stringify({ url: location.href, text: document.body.innerText, inputs: Array.from(document.querySelectorAll('input')).map(i => i.value).filter(Boolean) })"
                ev = call_api(s, 'Runtime.evaluate', {'expression': eval_script}, session_id=sess_id)
                val_str = ev.get('result', {}).get('result', {}).get('value')
                if val_str:
                    d = json.loads(val_str)
                    txt = d.get('text', '')
                    inputs = d.get('inputs', [])
                    code = None
                    import re
                    for inp in inputs:
                        if re.match(r'^[A-Z0-9]{5,10}$', inp.strip()):
                            code = inp.strip()
                            break
                    if not code:
                        matches = re.findall(r'\b([A-Z]{4}[0-9]{3,5})\b', txt)
                        if matches: code = matches[0]
                    if code:
                        ref_url = f'https://www.airalo.com/ko?r={code}'
                        update_airalo_in_db(code, ref_url)
                        break
    except Exception as e:
        pass
    import time
    time.sleep(3)

s.close()
