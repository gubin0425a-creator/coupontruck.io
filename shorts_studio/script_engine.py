# -*- coding: utf-8 -*-
"""
신비한 건축사전 4단계 서사 대본 생성 엔진
(Hook -> Problem -> Solution -> Punchline)
Gemini 무료 티어 API 지원 및 100% 무료 오프라인 지식 베이스 자동 폴백
"""

import json
import logging
from typing import List, Dict, Any
from .config import GEMINI_API_KEY
from .assets.templates.knowledge_base import CURATED_TOPICS, get_curated_topics

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """당신은 구독자 100만 지식/건축 쇼츠 전문 채널 '신비한 건축사전'과 원카AI의 수석 작가입니다.
시청자의 이탈을 방지하고 끝까지 보게 만드는 4단계 서사 구조로 숏폼 대본을 작성해야 합니다.

[4단계 서사 구조]
1. Hook (도입 0~7초): 일상에서 흔히 보거나 극적인 상황에 대한 충격적인 질문 던지기 ("왜 ~할까요?")
2. Problem (난관 7~20초): 해당 구조물이나 기술이 직면한 물리적 위험, 한계, 붕괴 위기 강조
3. Solution (해결 20~45초): 공학자/엔지니어들의 천재적인 원리와 설계 해법을 쉽고 명쾌하게 설명
4. Punchline (요약 45~55초): 핵심 요약 1줄 + 다음 편 기대감과 구독/좋아요 유도

반드시 유효한 JSON 형식으로만 응답하세요."""

def generate_batch_scripts(theme: str = "건축과 토목의 신비한 공학 비밀", count: int = 14, api_key: str = None) -> List[Dict[str, Any]]:
    """
    30일치(14편) 에피소드 대본을 생성하거나 엄선된 데이터베이스에서 로드합니다.
    """
    effective_api_key = api_key or GEMINI_API_KEY
    
    # 1. Gemini API 키가 제공된 경우 동적 생성 시도
    if effective_api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=effective_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            테마: '{theme}'
            요청: 총 {count}개의 숏폼 영상 기획안과 대본을 생성하세요.
            각 에피소드는 4개의 씬(hook, problem, solution, punchline)으로 구성됩니다.
            
            다음 JSON 스키마를 반드시 준수하세요:
            [
              {{
                "id": "ep_01",
                "title": "에피소드 제목",
                "category": "분야",
                "scenes": [
                  {{
                    "type": "hook",
                    "narrator": "나레이션 대사 (한국어, 흥미유발)",
                    "visual_prompt": "Pollinations AI visual prompt in English, cinematic, 9:16 vertical 8k",
                    "infographic": {{"label": "측정항목", "dimension": "수치/치수", "target": "top_center"}}
                  }},
                  {{
                    "type": "problem",
                    "narrator": "나레이션 대사",
                    "visual_prompt": "English visual prompt",
                    "infographic": {{"label": "위험항목", "dimension": "수치", "target": "center"}}
                  }},
                  {{
                    "type": "solution",
                    "narrator": "나레이션 대사",
                    "visual_prompt": "English visual prompt",
                    "infographic": {{"label": "해법기술", "dimension": "핵심원리", "target": "center"}}
                  }},
                  {{
                    "type": "punchline",
                    "narrator": "나레이션 대사",
                    "visual_prompt": "English visual prompt",
                    "infographic": {{"label": "신비한 건축사전", "dimension": "구독 & 좋아요", "target": "bottom_center"}}
                  }}
                ]
              }}
            ]
            """
            
            response = model.generate_content(
                contents=[{"role": "user", "parts": [SYSTEM_PROMPT + "\n\n" + prompt]}],
                generation_config={"response_mime_type": "application/json"}
            )
            
            data = json.loads(response.text)
            if isinstance(data, list) and len(data) >= count:
                logger.info(f"Gemini API로 {len(data)}개 에피소드 동적 생성 성공")
                return data[:count]
        except Exception as e:
            logger.warning(f"Gemini API 동적 생성 실패 또는 키 미설정, 내장 지식 베이스로 자동 전환: {e}")

    # 2. 무료 오프라인 엄선 데이터베이스 사용 (크레딧 0원 보장)
    logger.info(f"내장 오프라인 지식 베이스에서 {count}개 에피소드 로드")
    curated = get_curated_topics(count)
    return curated
