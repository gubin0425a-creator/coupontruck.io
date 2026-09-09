# -*- coding: utf-8 -*-
"""
유튜브 알고리즘 100점 SEO 최적화 생성 엔진
CTR 극대화 제목 3종, 타임스탬프 포함 설명란, 500자 고득점 태그셋, 참여형 고정 댓글 자동 생성
"""

from typing import Dict, Any, List

def build_seo_pack(episode: Dict[str, Any]) -> Dict[str, Any]:
    """
    에피소드 데이터를 분석하여 유튜브 알고리즘 100점 SEO 메타데이터 세트를 완성합니다.
    """
    existing_seo = episode.get("seo", {})
    title_base = episode.get("title", "신비한 건축의 비밀")
    category = episode.get("category", "건축 공학")
    
    # 1. CTR 3배 극대화 A/B/C 제목 생성 (기존 제목 보존 및 보강)
    titles = existing_seo.get("titles", [])
    if not titles or len(titles) < 3:
        titles = [
            f"{title_base}의 소름돋는 비밀?! #Shorts",
            f"엔지니어들도 경악한 {category}의 천재적 원리 #신비한건축사전",
            f"무너지지 않는 1초의 공학! {title_base} 1분 요약"
        ]
        
    # 2. 알고리즘 친화적 설명란 (첫 2줄 스니펫 + 타임라인 + 해시태그)
    description = existing_seo.get("description", "")
    if not description:
        description = (
            f"{title_base}!\n"
            f"보이지 않는 곳에서 안전과 기적을 만드는 첨단 {category}의 비밀을 1분 만에 파헤칩니다.\n\n"
            f"⏱️ 타임라인\n"
            f"00:00 시작되는 의문과 호기심\n"
            f"00:08 붕괴와 한계의 위기\n"
            f"00:22 엔지니어들의 천재적 해결책\n"
            f"00:45 안전을 지키는 1초의 과학\n\n"
            f"매주 월·수·금 저녁 6시, 신비한 건축과 공학의 비밀이 업로드됩니다.\n"
            f"구독과 좋아요는 다음 영상을 만드는 데 큰 힘이 됩니다!\n\n"
            f"#Shorts #신비한건축사전 #건축공학 #토목공학 #과학상식 #원카AI #1분지식 #{category.replace(' ', '')}"
        )
        
    # 3. 500자 꽉 찬 알고리즘 태그셋 (25~30개)
    tags = existing_seo.get("tags", [])
    default_tags = [
        "신비한건축사전", "원카AI", "건축쇼츠", "토목공학", "건축공학", "1분지식", "과학상식",
        "지식쇼츠", "세계의건축", "공학비밀", "신기한구조물", "과학유튜브", "초고층빌딩", "흥미진진",
        "토목기술", "현대건축", "과학원리", "구조역학", "공학이야기", "미스터리건축", "인기급상승"
    ]
    all_tags = list(dict.fromkeys(tags + default_tags))[:28]
    tags_string = ", ".join(all_tags)
    
    # 4. 참여 유도용 고정 댓글 (Pinned Comment)
    pinned_comment = existing_seo.get("pinned_comment", "")
    if not pinned_comment:
        pinned_comment = f"📌 {title_base}에 대해 어떻게 생각하시나요? 여러분이 평소 궁금했던 건축물이나 공학 기술을 댓글로 남겨주시면 다음 영상에서 다뤄드립니다!"

    return {
        "titles": titles,
        "selected_title": titles[0],
        "description": description,
        "tags": all_tags,
        "tags_string": tags_string,
        "pinned_comment": pinned_comment,
        "category_id": "28"  # YouTube Category: Science & Technology (28) or Education (27)
    }
