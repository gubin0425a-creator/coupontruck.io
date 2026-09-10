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

send_frame(s, json.dumps({'id': 1, 'method': 'Target.getTargets'}))
s.settimeout(5.0)

temu_tid = None
while True:
    msg = recv_frame(s)
    if not msg: break
    res = json.loads(msg)
    if res.get('id') == 1:
        for t in res.get('result', {}).get('targetInfos', []):
            if t.get('type') == 'page':
                title = t.get('title', '')
                url = t.get('url', '')
                tid = t.get('targetId', '')
                print(f'Page: {title} | {url}')
                if 'temu.com' in url:
                    temu_tid = tid
        break

if temu_tid:
    print(f'\nAttaching to Temu target: {temu_tid}...')
    send_frame(s, json.dumps({'id': 2, 'method': 'Target.attachToTarget', 'params': {'targetId': temu_tid, 'flatten': True}}))
    session_id = None
    while True:
        msg = recv_frame(s)
        if not msg: break
        res = json.loads(msg)
        if res.get('id') == 2:
            session_id = res.get('result', {}).get('sessionId')
            print(f'Session ID: {session_id}')
            break

    if session_id:
        print('Navigating Temu tab to affiliate program...')
        send_frame(s, json.dumps({'id': 3, 'sessionId': session_id, 'method': 'Page.navigate', 'params': {'url': 'https://www.temu.com/kr/affiliate_influencer_program.html'}}))
        while True:
            msg = recv_frame(s)
            if not msg: break
            res = json.loads(msg)
            if res.get('id') == 3:
                print('Navigated:', res)
                break

        import time
        time.sleep(4)

        # Check content
        eval_expr = "JSON.stringify({ url: location.href, title: document.title, inputs: Array.from(document.querySelectorAll('input')).map(i => ({val: i.value, ph: i.placeholder, cls: i.className})), links: Array.from(document.querySelectorAll('a')).map(a => ({href: a.href, text: a.innerText})).filter(a => a.href.includes('temu.to') || a.href.includes('affiliate') || a.text.includes('복사') || a.text.includes('공유') || a.text.includes('코드')), buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText).filter(Boolean), text: document.body.innerText.slice(0, 2500) })"
        send_frame(s, json.dumps({'id': 4, 'sessionId': session_id, 'method': 'Runtime.evaluate', 'params': {'expression': eval_expr}}))
        while True:
            msg = recv_frame(s)
            if not msg: break
            res = json.loads(msg)
            if res.get('id') == 4:
                val = res.get('result', {}).get('result', {}).get('value')
                print('\n--- EVAL RESULT ---')
                print(val)
                break

s.close()
