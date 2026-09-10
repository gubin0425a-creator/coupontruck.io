import os
import sys
import time
import json
import re

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'coupons.json')
OFFERS_FILE = os.path.join(BASE_DIR, 'data', 'offers.json')

def update_temu_in_db(code, referral_url):
    print(f'\n[자동 감지 성공] 테무 추천코드/링크 추출 완료: {code} | {referral_url}')
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data.get('categories', {}).get('shopping', {}).get('items', []):
            if '테무' in item.get('name', '') or 'Temu' in item.get('name', ''):
                item['code'] = code
                item['url'] = referral_url
                item['badge'] = '최대 30%'
                item['is_active'] = True
                item['expires'] = '2026-12-31'
                item['type'] = 'REFERRAL'
                break
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print('data/coupons.json 테무 전용 코드로 업데이트 완료!')

    if os.path.exists(OFFERS_FILE):
        with open(OFFERS_FILE, 'r', encoding='utf-8') as f:
            offers = json.load(f)
        
        for o in offers:
            if '테무' in o.get('title', '') or 'Temu' in o.get('title', ''):
                o['coupon_code'] = code
                o['target_url'] = referral_url
                o['affiliate_url'] = referral_url
                o['end_date'] = '2026-12-31'
                o['badge'] = '최대 30%'
                o['type'] = 'REFERRAL'
                break
        
        with open(OFFERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(offers, f, ensure_ascii=False, indent=2)
        print('data/offers.json 테무 전용 코드로 업데이트 완료!')

def main():
    active_port_file = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort')
    if not os.path.exists(active_port_file):
        print('DevToolsActivePort not found')
        return

    with open(active_port_file, 'r') as f:
        lines = [l.strip() for l in f]
    port, path = lines[0], lines[1]
    ws_endpoint = f'ws://127.0.0.1:{port}{path}'

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_endpoint)
        context = browser.contexts[0]
        
        temu_page = None
        for page in context.pages:
            if 'temu.com' in page.url:
                temu_page = page
                break
        
        if not temu_page:
            temu_page = context.new_page()
            temu_page.goto('https://www.temu.com/login.html', wait_until='domcontentloaded')

        print('테무 탭 모니터링 시작... (로그인 대기 중)')
        
        for attempt in range(60):
            try:
                url = temu_page.url
                if 'login' not in url:
                    print(f'로그인 감지됨! 현재 URL: {url}')
                    if 'affiliate' not in url:
                        temu_page.goto('https://www.temu.com/kr/affiliate-program.html', wait_until='domcontentloaded')
                        time.sleep(3)
                    
                    content = temu_page.content()
                    link_match = re.search(r'https://temu\.to/k/[a-zA-Z0-9]+', content)
                    
                    inputs = temu_page.locator('input').all()
                    extracted_link = None
                    extracted_code = None
                    for inp in inputs:
                        v = inp.get_attribute('value') or ''
                        if 'temu.to' in v:
                            extracted_link = v
                        elif len(v) in [8, 9, 10] and v.isalnum():
                            extracted_code = v
                    
                    if link_match and not extracted_link:
                        extracted_link = link_match.group(0)
                    
                    if extracted_link:
                        code = extracted_code or (extracted_link.split('/')[-1] if '/' in extracted_link else 'TEMU2026')
                        update_temu_in_db(code, extracted_link)
                        return
            except Exception as e:
                pass
            time.sleep(3)
        
        print('시간 초과: 로그인이 완료되지 않았습니다.')

if __name__ == '__main__':
    main()
