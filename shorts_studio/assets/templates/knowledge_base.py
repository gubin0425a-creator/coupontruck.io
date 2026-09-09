# -*- coding: utf-8 -*-
"""
신비한 건축사전 & 지식형 쇼츠를 위한 100% 무료 오프라인 지식 베이스
원카AI의 4단계 서사 구조 (Hook -> Problem -> Solution -> Punchline) 기반 14개 에피소드
"""

CURATED_TOPICS = [
    {
        "id": "ep01_lotte_damper",
        "title": "123층 롯데타워 꼭대기에 400톤 추가 매달린 이유",
        "category": "초고층 빌딩 공학",
        "scenes": [
            {
                "type": "hook",
                "narrator": "국내 최고 123층 롯데타워 꼭대기에는 왜 400톤짜리 거대한 추가 매달려 있을까요?",
                "visual_prompt": "Futuristic skyscraper 123 floors top view, massive 400 ton tuned mass damper swinging pendulum inside glass tower, cinematic lighting, 8k vertical 9:16",
                "infographic": {"label": "TMD 감쇠장치", "dimension": "400 TON", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "초속 80미터 태풍이나 강진이 발생하면, 초고층 빌딩 상층부는 1미터 이상 휘청거리며 붕괴 위기에 직면합니다.",
                "visual_prompt": "Dramatic storm typhoon striking modern skyscraper, building swaying visual simulation, stress lines, red warning atmosphere, 8k vertical 9:16",
                "infographic": {"label": "풍하중 위험", "dimension": "풍속 80m/s", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "이를 막는 천재적인 기술이 바로 TMD입니다. 건물이 오른쪽으로 흔들리면 추가 왼쪽으로 움직여 진동 에너지를 상쇄시킵니다.",
                "visual_prompt": "Engineering cross-section diagram of tuned mass damper, hydraulic cylinders counteracting building motion, blue and red energy vectors, 8k vertical 9:16",
                "infographic": {"label": "진동 상쇄 원리", "dimension": "-70% 흔들림", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "보이지 않는 곳에서 수만 명의 생명을 지키는 1초의 공학! 다음 건축 미스터리가 궁금하다면 지금 구독하세요.",
                "visual_prompt": "Stunning golden hour sunset view of Lotte World Tower Seoul, glittering architectural triumph, vertical 9:16 cinematic",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 좋아요", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "롯데타워 꼭대기에 400톤 괴물 추가 숨겨진 소름돋는 이유?! #Shorts",
                "초고층 빌딩이 강풍에도 절대 부러지지 않는 비밀 #신비한건축사전",
                "123층에서 1미터 흔들리면 어떻게 될까? 엔지니어들의 천재적 해법"
            ],
            "description": "국내 최고 높이 123층 롯데타워 꼭대기에는 400톤에 달하는 거대한 진동 흡수 장치(TMD)가 숨겨져 있습니다. 태풍과 지진의 극한 하중을 어떻게 버텨내는지 공학적 비밀을 1분 만에 파헤칩니다.\n\n⏱️ 타임라인\n00:00 롯데타워 꼭대기의 거대한 추\n00:07 1미터 흔들리는 빌딩의 위기\n00:20 TMD 감쇠기의 천재적 원리\n00:45 안전을 지키는 1초의 과학\n\n#Shorts #신비한건축사전 #롯데타워 #건축공학 #초고층빌딩 #과학상식 #토목공학",
            "tags": [
                "롯데타워", "TMD", "동조질량감쇠기", "신비한건축사전", "원카AI", "건축쇼츠", "초고층빌딩",
                "지진대비", "내진설계", "면진구조", "토목공학", "과학유튜브", "1분지식", "흥미진진",
                "세계의건축", "지식쇼츠", "공학비밀", "타이베이101", "댐퍼추", "빌딩흔들림"
            ],
            "pinned_comment": "📌 건물이 흔들리는 걸 몸으로 느껴본 적 있으신가요? 여러분이 알고 계신 가장 신기한 빌딩을 댓글로 알려주세요!"
        }
    },
    {
        "id": "ep02_underwater_tunnel",
        "title": "수심 50m 해저터널은 왜 바닷물에 찌그러지지 않을까?",
        "category": "해양 토목 공학",
        "scenes": [
            {
                "type": "hook",
                "narrator": "수심 50미터 칠흑 같은 바다 밑에 뚫린 해저터널. 엄청난 수압에도 왜 절대 무너지지 않을까요?",
                "visual_prompt": "Deep underwater highway tunnel submerged deep under ocean water, dramatic lighting, glass and steel cross section, fish swimming outside, 8k vertical 9:16",
                "infographic": {"label": "수심 측정", "dimension": "수심 50m", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "수심 50미터에서 터널 벽면이 받는 압력은 무려 1제곱미터당 50톤! 자동차 수십 대가 짓누르는 힘입니다.",
                "visual_prompt": "Crushing water pressure vectors pressing against curved tunnel concrete walls, high pressure underwater physics simulation, 8k vertical 9:16",
                "infographic": {"label": "수압 하중", "dimension": "50 ton/m²", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "비밀은 '침매 공법'과 '아치 구조'입니다. 육상에서 제작한 거대한 콘크리트 함을 가라앉힌 뒤 수압을 이용해 초밀착 압축 밀봉합니다.",
                "visual_prompt": "Giant precast immersed tunnel tube segment lowering into ocean floor trench, hydrostatic pressure sealing rubber gasket, 8k vertical 9:16",
                "infographic": {"label": "침매터널 수압밀봉", "dimension": "완전 방수 Gasket", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "바다 밑을 도로로 바꾸는 인간의 무한한 도전! 더 놀라운 토목의 비밀을 보고 싶다면 구독을 눌러주세요.",
                "visual_prompt": "Cars driving through modern high tech underwater tunnel with ambient lighting, brilliant engineering marvel, vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 알림설정", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "수심 50m 바닷속 터널이 안 터지는 소름돋는 원리?! #Shorts",
                "바다 밑에 도로를 깔았다고? 침매터널의 충격적인 공학 비밀",
                "수압 50톤을 버티는 해저터널 제작과정 1분 요약"
            ],
            "description": "수심 50m 바다 밑바닥을 가로지르는 해저터널! 어떻게 1제곱미터당 50톤의 무지막지한 수압을 버티고 물 한 방울 새지 않는 걸까요? 세계 최고 수준의 침매공법과 아치형 방수 기술을 알아봅니다.\n\n⏱️ 타임라인\n00:00 해저터널의 엄청난 수압\n00:08 1m²당 50톤의 압력\n00:22 침매공법과 천재적 수압 밀봉\n00:48 바다 속 도로의 완성\n\n#Shorts #신비한건축사전 #해저터널 #침매터널 #토목공학 #가덕도해저터널 #공학상식",
            "tags": [
                "해저터널", "침매공법", "거가대교", "토목공학", "신비한건축사전", "원카AI", "수압",
                "방수기술", "건축미스터리", "세계의다리", "터널공사", "공학이야기", "과학쇼츠", "신기한지식"
            ],
            "pinned_comment": "📌 바다 밑으로 달리는 기분, 직접 경험해 보셨나요? 여러분의 생각을 댓글로 들려주세요!"
        }
    },
    {
        "id": "ep03_sinkhole_wall",
        "title": "도심 한복판 지하 80m를 파는데 땅이 안 꺼지는 이유",
        "category": "지하 굴착 공학",
        "scenes": [
            {
                "type": "hook",
                "narrator": "수천억 원대 고층 빌딩 바로 옆에서 지하 80미터를 파내려가는데, 왜 주변 건물은 끄떡없을까요?",
                "visual_prompt": "Massive deep urban foundation excavation site next to skyscrapers, crane lowering reinforced steel cages deep into earth, 8k vertical 9:16",
                "infographic": {"label": "굴착 깊이", "dimension": "지하 -80m", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "흙을 무작정 파내면 지하수가 터져 나오고, 흙벽이 무너지며 도심 전체가 싱크홀에 집어삼켜질 수 있습니다.",
                "visual_prompt": "Ground collapse simulation and sinkhole danger diagram, groundwater rushing through soil layers, warning graphic, 8k vertical 9:16",
                "infographic": {"label": "싱크홀 위험", "dimension": "지하수 붕괴", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "해답은 바로 '지하 연속벽(슬러리 월)' 기술입니다. 벤토나이트 안정액을 채워 벽을 보호하며 땅속에 거대한 콘크리트 철벽을 세웁니다.",
                "visual_prompt": "Diaphragm wall slurry wall construction diagram, bentonite slurry trench supporting soil pressure, concrete pumping, 8k vertical 9:16",
                "infographic": {"label": "슬러리월(지하연속벽)", "dimension": "두께 1.5m 철벽", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "보이지 않는 땅속에서 도시를 떠받치는 단단한 방패! 다음 지하 비밀이 궁금하다면 구독을 잊지 마세요.",
                "visual_prompt": "Futuristic clean subterranean foundation architecture supporting modern gleaming city above, cinematic vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독하고 지식 얻기", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "도심에 지하 80m 구멍을 뚫어도 건물 안 무너지는 이유 #Shorts",
                "싱크홀 막는 땅속 콘크리트 철벽! 슬러리월 공법의 비밀",
                "고층빌딩 바로 옆에서 지하를 파는 기상천외한 공학 기술"
            ],
            "description": "초고층 빌딩 주변에서 지하 수십 미터를 파낼 때 도로가 가라앉지 않는 비결! 지하연속벽(Slurry Wall)과 벤토나이트 안정액의 놀라운 공학 원리를 파헤칩니다.\n\n#Shorts #신비한건축사전 #슬러리월 #지하연속벽 #싱크홀 #토목기술 #건축공학",
            "tags": [
                "슬러리월", "지하연속벽", "싱크홀예방", "지하굴착", "신비한건축사전", "토목공학", "건축시공",
                "벤토나이트", "기초공사", "도심토목", "과학원리", "1분과학", "원카AI"
            ],
            "pinned_comment": "📌 우리 동네 공사 현장에도 이 기술이 쓰였을까요? 궁금한 토목 기술을 댓글로 남겨주세요!"
        }
    },
    {
        "id": "ep04_pisa_tower",
        "title": "피사의 사탑은 왜 800년 동안 쓰러지지 않았을까?",
        "category": "지반 공학 미스터리",
        "scenes": [
            {
                "type": "hook",
                "narrator": "무려 5.5도나 기울어져 곧 쓰러질 것 같은 피사의 사탑. 왜 800년 동안 지진에도 멀쩡할까요?",
                "visual_prompt": "Leaning Tower of Pisa dramatic low angle view, tilting white marble bell tower against blue sky, historic Italy, vertical 9:16 8k",
                "infographic": {"label": "기울기 각도", "dimension": "5.5도 기울어짐", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "1만 4천 톤의 육중한 석조 탑이 연약한 진흙 지반 위에 서 있어, 물리학 법칙상 이미 무너졌어야 정상입니다.",
                "visual_prompt": "Cross section diagram of soft silt clay ground under Leaning Tower of Pisa, gravitational center shift vector, 8k vertical 9:16",
                "infographic": {"label": "구조 하중", "dimension": "14,500 TON", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "놀랍게도 탑을 기울어지게 만든 '부드러운 진흙 지반'이 지진파의 공진을 흡수하여 탑의 붕괴를 막아준 역설이 숨어있었습니다.",
                "visual_prompt": "Dynamic soil structure interaction diagram, earthquake seismic waves absorbed by soft soil damping vibration, 8k vertical 9:16",
                "infographic": {"label": "동적 상호작용(DSSI)", "dimension": "지진파 완벽 흡수", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "최악의 단점이 최고의 방패가 된 세기의 기적! 더 흥미로운 건축 이야기를 원하시면 구독하세요.",
                "visual_prompt": "Sunset illuminated Leaning tower of pisa with tourists marveling at historic engineering miracle, vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 좋아요", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "피사의 사탑이 800년 동안 안 쓰러진 충격적 반전?! #Shorts",
                "지진 4번 맞고도 살아남은 피사의 사탑 기적의 원리",
                "물리학자들도 경악한 피사의 사탑 지반 공학 미스터리"
            ],
            "description": "기울어진 채 800년을 버텨온 피사의 사탑! 탑을 무너뜨릴 뻔했던 진흙 지반이 오히려 지진으로부터 탑을 구했다는 충격적인 과학적 사실을 공개합니다.\n\n#Shorts #신비한건축사전 #피사의사탑 #지반공학 #건축역사 #공학미스터리 #과학이야기",
            "tags": [
                "피사의사탑", "건축미스터리", "지진원리", "지반공학", "신비한건축사전", "이탈리아건축", "세계불가사의",
                "토목상식", "물리학", "원카AI", "지식쇼츠", "역사속과학"
            ],
            "pinned_comment": "📌 피사의 사탑을 실제로 보면 생각보다 훨씬 많이 기울어져 있다고 합니다! 여러분은 가보신 적 있나요?"
        }
    },
    {
        "id": "ep05_bridge_cable",
        "title": "바다 위 거대한 현수교는 와이어 몇 줄로 어떻게 버틸까?",
        "category": "교량 구조 역학",
        "scenes": [
            {
                "type": "hook",
                "narrator": "수만 톤의 자동차가 오가는 바다 위 거대한 다리. 겨우 몇 가닥의 쇠줄이 어떻게 다리를 지탱할까요?",
                "visual_prompt": "Epic grand suspension bridge crossing turbulent ocean bay, massive steel cables glowing in morning mist, 8k vertical 9:16",
                "infographic": {"label": "케이블 하중", "dimension": "수만 톤 지탱", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "강풍과 파도, 수만 톤의 교통 하중이 걸리면 와이어는 쉽게 끊어지거나 피로 파괴가 발생할 위험이 큽니다.",
                "visual_prompt": "Tension stress lines stretching across bridge cable suspension system, turbulent sea gale wind blowing, 8k vertical 9:16",
                "infographic": {"label": "인장 응력", "dimension": "극한 인장력", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "비밀은 수만 가닥의 강선을 촘촘히 엮은 '주케이블'과 양 끝을 암반에 묻어버린 거대한 '앵커리지 콘크리트 덩어리'입니다.",
                "visual_prompt": "Cutaway cross section showing suspension cable composed of 30000 high tensile steel wires bundled tight, anchored in massive concrete bunker, 8k vertical 9:16",
                "infographic": {"label": "주케이블 단면", "dimension": "강선 3만 가닥 융합", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "가장 얇은 강철로 가장 거대한 바다를 건너는 기술! 다음 교량의 비밀도 구독하고 만나보세요.",
                "visual_prompt": "Golden gate / Akashi Kaikyo suspension bridge illuminated at night with beautiful traffic light trails, 8k vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 알림설정", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "바다 위 수만톤 다리를 철사 몇 줄로 버티는 소름돋는 원리?! #Shorts",
                "현수교 케이블을 칼로 자르면 어떻게 될까? 교량 공학의 비밀",
                "수만 톤을 매단 강철 와이어의 소름돋는 내부 구조 #신비한건축사전"
            ],
            "description": "바다를 건너는 거대한 현수교! 얇아 보이는 케이블이 어떻게 수만 톤의 자동차와 다리 무게를 거뜬히 지탱하는지 주케이블과 앵커리지의 공학적 비밀을 밝힙니다.\n\n#Shorts #신비한건축사전 #현수교 #광안대교 #이순신대교 #교량공학 #토목공학",
            "tags": [
                "현수교", "주케이블", "앵커리지", "교량공학", "신비한건축사전", "토목공학", "원카AI",
                "이순신대교", "광안대교", "골든게이트브릿지", "건축지식", "과학원리"
            ],
            "pinned_comment": "📌 바람 부는 다리를 건널 때 흔들리는 느낌을 받아본 적 있으신가요? 여러분의 경험을 남겨주세요!"
        }
    },
    {
        "id": "ep06_dome_roof",
        "title": "기둥 하나 없는 거대한 돔 천장은 왜 안 무너질까?",
        "category": "공간 구조 역학",
        "scenes": [
            {
                "type": "hook",
                "narrator": "축구장 크기의 거대한 돔 경기장 천장. 가운데 기둥이 하나도 없는데 왜 머리 위로 쏟아지지 않을까요?",
                "visual_prompt": "Vast indoor stadium with enormous curved dome roof ceiling without a single central pillar, glowing lights, dramatic scale, vertical 9:16",
                "infographic": {"label": "기둥 없는 공간", "dimension": "직경 200m 무지주", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "수천 톤에 달하는 지붕 무게는 중심부에 엄청난 중력을 가해 평평한 구조라면 순식간에 붕괴하고 맙니다.",
                "visual_prompt": "Downward gravity load vectors pressing on flat roof vs curved structure, red collapse simulation, 8k vertical 9:16",
                "infographic": {"label": "중력 하중", "dimension": "수천 톤 수직하중", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "해답은 '아치(Arch)와 트러스'입니다. 지붕의 무게를 수평 방향의 압축력으로 분산시켜 가장자리 기둥으로 흘려보냅니다.",
                "visual_prompt": "Engineering stress analysis of dome truss, forces flowing smoothly outward along curved geodesic dome shell, 8k vertical 9:16",
                "infographic": {"label": "트러스 하중분산", "dimension": "측면 압축력 분산", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "기둥을 없애고 하늘을 덮어버린 공학의 마법! 더 놀라운 구조의 비밀을 구독하고 확인하세요.",
                "visual_prompt": "Stunning exterior aerial view of glowing futuristic geodesic dome stadium at night, 8k vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독하고 지식 채우기", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "기둥 하나 없이 축구장 덮은 돔 천장의 소름돋는 비밀 #Shorts",
                "수천 톤 지붕이 머리 위로 안 떨어지는 천재적 물리 법칙",
                "로마 판테온부터 고척돔까지! 기둥 없는 지붕의 원리"
            ],
            "description": "기둥 없이 수백 미터의 공간을 덮는 돔 구조의 비밀! 아치 구조와 지오데식 트러스가 어떻게 수천 톤의 중력을 분산시키는지 알아봅니다.\n\n#Shorts #신비한건축사전 #돔경기장 #트러스구조 #아치공법 #건축공학 #고척돔",
            "tags": ["돔구조", "고척돔", "판테온", "트러스", "아치", "신비한건축사전", "건축구조", "토목공학", "원카AI"]
        }
    },
    {
        "id": "ep07_dam_concrete",
        "title": "수백억 톤 물을 막는 거대 댐의 콘크리트는 왜 굳는데 수십 년이 걸릴까?",
        "category": "수자원 댐 공학",
        "scenes": [
            {
                "type": "hook",
                "narrator": "수백억 톤의 물을 가로막는 거대한 댐. 댐 내부의 콘크리트는 왜 완공 후 수십 년 동안 굳고 있을까요?",
                "visual_prompt": "Monolithic massive hydroelectric concrete gravity dam holding back enormous reservoir lake, water gushing through spillway, vertical 9:16",
                "infographic": {"label": "저수 용량", "dimension": "수백억 톤 수압", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "콘크리트는 굳으면서 섭씨 70도 이상의 수화열을 뿜어냅니다. 두꺼운 댐 내부가 과열되면 균열이 생겨 댐이 터질 수 있습니다.",
                "visual_prompt": "Thermal infrared simulation of concrete dam core showing boiling hydration heat, crack propagation danger, 8k vertical 9:16",
                "infographic": {"label": "수화열 위험", "dimension": "내부 온도 70°C", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "엔지니어들은 댐 내부에 수천 킬로미터의 냉각 파이프를 깔고 얼음물을 흘려보내 인공적으로 열을 식히며 천천히 양생합니다.",
                "visual_prompt": "Internal engineering cutaway showing maze of cooling pipes pumping ice cold water through curing mass concrete blocks, 8k vertical 9:16",
                "infographic": {"label": "냉각 파이프라인", "dimension": "인공 냉각 제어", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "단단함을 위해 스스로 뜨거워지는 콘크리트와의 사투! 다음 거대 토목의 비밀을 구독하고 확인하세요.",
                "visual_prompt": "Majestic Hoover Dam / Three Gorges Dam standing mighty against the canyon under dramatic twilight skies, vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 좋아요", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "거대 댐 안쪽 콘크리트가 굳는데 100년 걸리는 소름돋는 이유 #Shorts",
                "수화열 때문에 댐이 폭발할 뻔했다?! 후버댐의 숨겨진 공학 비밀",
                "콘크리트 속에 얼음물 파이프를 깐 기상천외한 토목 공법"
            ],
            "description": "후버댐과 소양강댐 같은 거대 댐의 콘크리트 양생 비밀! 섭씨 70도를 넘는 수화열 균열을 막기 위해 냉각 파이프를 심은 엔지니어들의 사투를 파헤칩니다.\n\n#Shorts #신비한건축사전 #후버댐 #댐공학 #콘크리트수화열 #토목공학 #거대구조물",
            "tags": ["후버댐", "소양강댐", "콘크리트", "수화열", "댐공사", "토목공학", "신비한건축사전", "원카AI"]
        }
    },
    {
        "id": "ep08_airport_island",
        "title": "바다 한가운데 가라앉는 인공섬 공항을 띄우는 법",
        "category": "해양 매립 토목",
        "scenes": [
            {
                "type": "hook",
                "narrator": "바다 한가운데 흙을 부어 만든 인공섬 공항. 해마다 바닷속으로 가라앉고 있다는 사실을 알고 계셨나요?",
                "visual_prompt": "Aerial view of Kansai airport artificial island runway floating in deep blue ocean, modern airplane landing, vertical 9:16",
                "infographic": {"label": "해양 인공섬", "dimension": "해마다 지반 침하", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "부드러운 해저 점토층이 거대한 공항 무게를 견디지 못하고 이미 13미터 이상 가라앉아 터미널 기둥이 뒤틀릴 위험에 처했습니다.",
                "visual_prompt": "Cross-section showing ocean seabed clay layer squishing under weight of artificial island, sinking building foundation, 8k vertical 9:16",
                "infographic": {"label": "지반 침하", "dimension": "-13m 누적 침하", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "공학자들은 공항 지하 기둥마다 거대한 유압 잭을 설치해, 땅이 가라앉을 때마다 기둥을 들어 올려 수평을 맞추는 잭업 시스템을 가동 중입니다.",
                "visual_prompt": "Underground terminal basement showing thousands of computer-controlled hydraulic jacks lifting steel columns, laser leveling, 8k vertical 9:16",
                "infographic": {"label": "컴퓨터 잭업 시스템", "dimension": "밀리미터 단위 수평조절", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "가라앉는 섬과 끊임없이 싸우며 비행기를 띄우는 놀라운 기술! 다음 해양 공학 이야기도 놓치지 마세요.",
                "visual_prompt": "Night flight taking off over glittering ocean runway of Kansai offshore airport, vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 알림설정", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "바다 밑으로 가라앉는 공항을 기둥째 들어 올리는 소름돋는 기술 #Shorts",
                "간사이 공항이 바다에 잠기지 않는 비밀! 유압 잭업 시스템",
                "13미터 가라앉은 인공섬을 컴퓨터로 수평 맞추는 방법"
            ],
            "description": "바다 위에 지은 간사이 국제공항! 해저 점토층 침하로 13m 이상 가라앉았음에도 공항이 정상 운영되는 비결, 유압 잭업 시스템의 비밀을 밝힙니다.\n\n#Shorts #신비한건축사전 #간사이공항 #인공섬 #지반침하 #토목기술 #공항건설",
            "tags": ["간사이공항", "인공섬", "해양토목", "지반침하", "잭업공법", "신비한건축사전", "원카AI"]
        }
    },
    {
        "id": "ep09_seismic_bearing",
        "title": "규모 7 지진에도 흔들리지 않는 건물의 고무 쿠션 비밀",
        "category": "내진 면진 기술",
        "scenes": [
            {
                "type": "hook",
                "narrator": "규모 7.0의 강진이 땅을 뒤흔들 때, 아파트 바닥 아래 숨겨진 고무 덩어리가 기적을 만듭니다.",
                "visual_prompt": "Cross section view underneath a modern apartment building revealing massive round laminated rubber bearings separating foundation, vertical 9:16",
                "infographic": {"label": "면진 받침", "dimension": "지진격리 고무베어링", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "지반과 건물이 직접 붙어있으면 지진파의 충격이 건물 골조로 직격탄처럼 전달되어 기둥이 꺾이고 맙니다.",
                "visual_prompt": "Violent earthquake ground shaking shockwaves traveling up into unprotected building columns causing severe fracture lines, 8k vertical 9:16",
                "infographic": {"label": "지진 충격파", "dimension": "전단파 직격", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "해답은 '적층 고무 면진 받침'입니다. 고무와 강판을 겹겹이 쌓고 가운데 납 기둥을 박아 땅이 요동쳐도 건물은 제자리에 떠 있게 만듭니다.",
                "visual_prompt": "Laminated rubber bearing flexing sideways while building above remains perfectly level, lead plug absorbing kinetic energy, 8k vertical 9:16",
                "infographic": {"label": "지진력 80% 차단", "dimension": "납심 적층고무", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "땅과 건물을 분리해 버린 세기의 발상! 내 집의 안전 기술이 궁금하다면 지금 구독하세요.",
                "visual_prompt": "Modern earthquake-proof architectural masterpiece standing calm during twilight city lights, vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 좋아요", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "규모 7 지진 와도 아파트 안 무너지는 소름돋는 고무 패드?! #Shorts",
                "땅이 갈라져도 건물은 가만히 있는 천재적인 면진 장치",
                "건물 밑바닥에 숨겨진 1억짜리 지진 방패의 실체 #신비한건축사전"
            ],
            "description": "지진이 와도 건물 내부가 평온한 비결! 땅과 건물 사이에 고무와 납으로 만든 면진 받침(Base Isolation)을 설치해 지진 에너지를 80% 이상 흡수하는 기술을 소개합니다.\n\n#Shorts #신비한건축사전 #내진설계 #면진구조 #지진대비 #건축공학 #안전기술",
            "tags": ["면진설계", "내진설계", "적층고무", "지진대비", "신비한건축사전", "건축기술", "원카AI"]
        }
    },
    {
        "id": "ep10_burj_khalifa",
        "title": "세계 1위 828m 부르즈 할리파는 사막 모래 위에 어떻게 서 있을까?",
        "category": "초고층 기초 공학",
        "scenes": [
            {
                "type": "hook",
                "narrator": "세계에서 가장 높은 828미터 부르즈 할리파. 부슬부슬 부서지는 사막 모래 위에 어떻게 단단히 서 있을까요?",
                "visual_prompt": "Burj Khalifa soaring piercing into clouds over Dubai desert landscape, extreme vertical grandeur, 8k vertical 9:16",
                "infographic": {"label": "빌딩 높이", "dimension": "828 METERS", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "사막의 모래와 석회암은 단단한 암반이 없어, 50만 톤의 건물 무게를 지탱하지 못하고 그대로 침몰할 위험이 컸습니다.",
                "visual_prompt": "Geological cross-section showing weak porous desert sandstone shifting under immense building weight, 8k vertical 9:16",
                "infographic": {"label": "건물 총중량", "dimension": "500,000 TON", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "해답은 194개의 거대한 콘크리트 말뚝입니다. 지하 50미터까지 박아 넣고 모래와 말뚝 사이의 '마찰력'만으로 빌딩을 띄워 올렸습니다.",
                "visual_prompt": "3D engineering diagram of 194 friction piles drilled 50 meters deep into earth, skin friction resistance vectors holding foundation, vertical 9:16",
                "infographic": {"label": "마찰말뚝 기초", "dimension": "지하 50m 194개 파일", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "모래의 마찰력으로 중력을 이겨낸 인류 역대 최고의 타워! 다음 세계의 건축도 구독하고 감상하세요.",
                "visual_prompt": "Sparkling night aerial shot of Burj Khalifa illuminated with fountains dancing below, cinematic vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 알림설정", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "모래 위에 지은 828m 빌딩이 쓰러지지 않는 충격적 원리?! #Shorts",
                "부르즈 할리파 밑바닥에 숨겨진 194개의 거대 말뚝 비밀",
                "암반도 없는 사막에 세계 1위 초고층을 세운 한국 엔지니어들"
            ],
            "description": "세계 최고층 828m 부르즈 할리파! 단단한 암반 없는 두바이 사막에서 50만 톤의 하중을 오직 마찰말뚝(Friction Pile) 공법으로 버텨낸 경이로운 토목 기술을 소개합니다.\n\n#Shorts #신비한건축사전 #부르즈할리파 #초고층빌딩 #삼성물산 #마찰말뚝 #사막건축",
            "tags": ["부르즈할리파", "두바이", "초고층빌딩", "기초공학", "마찰말뚝", "신비한건축사전", "원카AI"]
        }
    },
    {
        "id": "ep11_tbm_subway",
        "title": "두더지처럼 땅을 파고 들어가는 200억짜리 거대 굴착기 TBM의 정체",
        "category": "기계 토목 기술",
        "scenes": [
            {
                "type": "hook",
                "narrator": "우리가 자는 사이 도시 지하에서 조용히 터널을 뚫는 길이 100미터짜리 거대 기계의 정체는 무엇일까요?",
                "visual_prompt": "Massive Tunnel Boring Machine cutterhead with rotating disc cutters digging through dark earth bedrock subterranean, vertical 9:16",
                "infographic": {"label": "기계 길이", "dimension": "100m 거대 TBM", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "폭약을 터뜨려 굴착하면 소음과 진동으로 지상의 건물에 균열이 가고, 붕괴 사고가 일어날 수 있습니다.",
                "visual_prompt": "Explosive drill and blast vibration waves causing ground cracks and disruption in street above, red warning visual, 8k vertical 9:16",
                "infographic": {"label": "발파 소음/진동", "dimension": "지상 균열 위험", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "해답은 쉴드 TBM입니다. 원형 커터 헤드로 암반을 갈아내면서 동시에 뒤쪽에서 콘크리트 세그먼트를 조립해 완벽한 터널을 즉시 완성합니다.",
                "visual_prompt": "Cutaway mechanism of TBM assembling precast concrete segment rings while digging simultaneously, robotic precision, 8k vertical 9:16",
                "infographic": {"label": "무진동 굴착 및 세그먼트", "dimension": "동시 굴착 & 시공", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "지하철과 GTX를 만드는 미래 지하 문명의 주역! 더 놀라운 기계 공학을 구독하고 확인하세요.",
                "visual_prompt": "Clean newly completed high tech circular metro tunnel with tracks stretching into distance, 8k vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 좋아요", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "땅속에서 100m짜리 괴물 로봇이 터널 파는 충격적 방법 #Shorts",
                "GTX와 지하철은 어떻게 소음 없이 뚫릴까? 200억 TBM의 비밀",
                "폭약 없이 암반을 갈아버리는 기상천외한 지하 굴착 머신"
            ],
            "description": "도심 지하 수십 미터에서 무진동으로 터널을 뚫는 쉴드 TBM(Tunnel Boring Machine)! 커터 헤드로 돌을 부수고 콘크리트 링을 즉시 조립하는 첨단 토목 기계를 파헤칩니다.\n\n#Shorts #신비한건축사전 #TBM #터널굴착기 #GTX #지하철공사 #기계공학",
            "tags": ["TBM", "쉴드TBM", "터널공사", "GTX", "지하철공학", "신비한건축사전", "원카AI"]
        }
    },
    {
        "id": "ep12_expansion_joint",
        "title": "고속도로 다리마다 쇠창살 틈새를 만들어 놓은 진짜 이유",
        "category": "도로 교량 구조",
        "scenes": [
            {
                "type": "hook",
                "narrator": "차를 타고 고속도로 다리를 지날 때 '덜컹' 소리가 나는 바닥 쇠창살 틈새. 왜 일부러 틈을 벌려 놓았을까요?",
                "visual_prompt": "Close-up macro angle of highway bridge expansion joint finger plate teeth interlocking on asphalt road with cars passing, vertical 9:16",
                "infographic": {"label": "신축이음장치", "dimension": "확장 틈새", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "만약 다리를 틈 없이 하나로 꽉 막아버리면, 한여름 폭염에 아스팔트와 콘크리트가 팽창하면서 다리 상판이 솟구쳐 깨져버립니다.",
                "visual_prompt": "Heat thermal expansion simulation causing concrete bridge deck to buckle and explode upward under intense summer sun, 8k vertical 9:16",
                "infographic": {"label": "열팽창 폭압", "dimension": "상판 좌굴 붕괴", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "이를 막는 장치가 '신축이음장치(Expansion Joint)'입니다. 계절에 따라 다리가 늘어나고 줄어드는 수십 센티미터의 숨통을 열어줍니다.",
                "visual_prompt": "Engineering animation of finger joint sliding open and closed responding to temperature variation, flexible rubber seal, 8k vertical 9:16",
                "infographic": {"label": "온도 신축 흡수", "dimension": "±30cm 유격 확보", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "다리가 살아 숨 쉴 수 있도록 만든 지혜로운 10센티미터! 매일 마주치는 건축의 비밀, 지금 구독하세요.",
                "visual_prompt": "Sunset shot of long scenic highway bridge winding over landscape with smooth flowing traffic, 8k vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 알림설정", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "다리 지날 때마다 덜컹거리는 쇠창살 틈새의 소름돋는 정체?! #Shorts",
                "다리에 일부러 틈을 안 만들면 벌어지는 대참사 #신비한건축사전",
                "여름에 다리가 30cm 늘어난다고? 신축이음장치의 비밀"
            ],
            "description": "고속도로 다리를 건널 때마다 차가 덜컹거리는 이유! 여름철 열팽창으로 다리가 파괴되는 것을 막아주는 신축이음장치(Expansion Joint)의 비밀을 1분 만에 알아봅니다.\n\n#Shorts #신비한건축사전 #신축이음장치 #교량공학 #열팽창 #도로공학 #교통안전",
            "tags": ["신축이음", "익스팬션조인트", "교량공학", "열팽창", "신비한건축사전", "도로공학", "원카AI"]
        }
    },
    {
        "id": "ep13_canal_locks",
        "title": "배가 산을 넘어 태평양에서 대서양으로 건너가는 기상천외한 방법",
        "category": "운하 수문 공학",
        "scenes": [
            {
                "type": "hook",
                "narrator": "해수면보다 무려 26미터나 높은 산꼭대기 호수를 거대한 화물선이 어떻게 오르내릴 수 있을까요?",
                "visual_prompt": "Massive container ship passing through huge concrete canal lock chamber surrounded by tropical jungle hills, vertical 9:16",
                "infographic": {"label": "수위 차이", "dimension": "해수면 +26m", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "파나마 지협의 거대한 산맥을 깎아내려 바닷길을 뚫으려 했지만, 산사태와 해수면 차이로 공사는 파산하고 말았습니다.",
                "visual_prompt": "Historical mountain collapse and mudslide crushing early sea-level canal attempt, red disaster lines, 8k vertical 9:16",
                "infographic": {"label": "지형 난제", "dimension": "산악 관통 실패", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "해답은 '물로 만든 엘리베이터(갑문)'입니다. 배를 챔버에 넣고 물을 채워 배를 들어 올린 뒤, 산 위의 가툰 호수를 건너게 만들었습니다.",
                "visual_prompt": "Step-by-step 3D infographic of canal lock chambers filling with water, raising giant ship like a hydraulic elevator, 8k vertical 9:16",
                "infographic": {"label": "계단식 갑문 엘리베이터", "dimension": "중력식 무동력 급수", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "지구를 잘라 배에게 길을 열어준 100년 토목의 정점! 다음 세계의 기적도 구독하고 만나보세요.",
                "visual_prompt": "Spectacular aerial view of modern Panama Canal locks opening gate allowing mega ship to enter ocean, vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 좋아요", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "수만톤 배가 산꼭대기 호수를 건너는 기상천외한 원리 #Shorts",
                "물로 만든 엘리베이터?! 파나마 운하 갑문의 충격적 공학",
                "태평양과 대서양이 바로 안 만나는 이유 #신비한건축사전"
            ],
            "description": "해발 26m 가툰 호수를 거대한 화물선이 계단처럼 물을 채워 건너는 파나마 운하! 펌프 없이 오직 중력으로 배를 띄우는 100년 토목 역사의 경이를 파헤칩니다.\n\n#Shorts #신비한건축사전 #파나마운하 #갑문공학 #물엘리베이터 #세계지리 #토목역사",
            "tags": ["파나마운하", "갑문", "수에즈운하", "운하공학", "신비한건축사전", "토목기적", "원카AI"]
        }
    },
    {
        "id": "ep14_glass_bridge",
        "title": "수백 미터 절벽 위 유리 다리에 해머를 내리쳐도 안 깨지는 이유",
        "category": "특수 재료 구조",
        "scenes": [
            {
                "type": "hook",
                "narrator": "수백 미터 아찔한 절벽 사이에 놓인 투명 유리 다리. 무거운 해머로 강하게 내리쳐도 왜 안전할까요?",
                "visual_prompt": "Terrifying high altitude transparent glass suspension bridge spanning between two misty jagged mountain cliffs, tourists walking, vertical 9:16",
                "infographic": {"label": "절벽 높이", "dimension": "해발 300m 절벽", "target": "top_center"}
            },
            {
                "type": "problem",
                "narrator": "일반 유리는 충격을 받으면 한순간에 산산조각 나며 수백 명이 허공으로 추락할 수 있는 치명적 재료입니다.",
                "visual_prompt": "Glass shattering into sharp shards animation with red warning graphics over dizzying canyon abyss, 8k vertical 9:16",
                "infographic": {"label": "유리 취성 파괴", "dimension": "추락 위험", "target": "center"}
            },
            {
                "type": "solution",
                "narrator": "비밀은 '3중 접합 강화유리'입니다. 강화유리 사이에 탄성 강한 PVB 특수 필름을 넣어, 유리가 깨져도 필름이 파편을 꽉 잡아 40톤 트럭도 버텨냅니다.",
                "visual_prompt": "Layered explosion cross section of triple laminated safety glass with tough transparent PVB polymer interlayer resisting shock, vertical 9:16",
                "infographic": {"label": "3중 PVB 접합유리", "dimension": "40톤 하중 지탱", "target": "center"}
            },
            {
                "type": "punchline",
                "narrator": "허공 위에 안전한 길을 만드는 투명한 방패 기술! 건축의 숨겨진 비밀을 더 알고 싶다면 구독하세요.",
                "visual_prompt": "Heroic panoramic view of mountain glass walkway gleaming under golden sunlight with tourists enjoying the view, vertical 9:16",
                "infographic": {"label": "신비한 건축사전", "dimension": "구독 & 알림설정", "target": "bottom_center"}
            }
        ],
        "seo": {
            "titles": [
                "절벽 위 유리 다리를 해머로 박살내도 안 무너지는 소름돋는 이유?! #Shorts",
                "40톤 트럭이 지나가도 멀쩡한 특수 접합유리의 공학 비밀",
                "발밑 300m 낭떠러지! 유리 다리에 숨겨진 3중 방패 기술"
            ],
            "description": "해발 300m 절벽 위 투명 유리 다리! 쇠망치로 때려 금이 가도 사람이 절대 떨어지지 않는 3중 접합 PVB 강화유리의 경이로운 안전 과학을 1분 만에 설명합니다.\n\n#Shorts #신비한건축사전 #유리다리 #접합유리 #건축재료 #강화유리 #스카이워크",
            "tags": ["유리다리", "스카이워크", "접합유리", "강화유리", "신비한건축사전", "안전기술", "원카AI"]
        }
    }
]

def get_curated_topics(count=14):
    """지정된 개수만큼 큐레이션된 에피소드 반환 (최대 14개)"""
    return CURATED_TOPICS[:count]
