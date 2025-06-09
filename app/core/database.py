"""
Supabase 데이터베이스 연결 설정
"""
from typing import Optional

from supabase import create_client, Client
from app.core.config import settings

# Supabase 클라이언트 인스턴스
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Supabase 클라이언트 인스턴스를 반환합니다."""
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError(
                "SUPABASE_URL과 SUPABASE_KEY 환경 변수가 설정되어야 합니다."
            )
        
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    return _supabase_client


def close_supabase_client():
    """Supabase 클라이언트 연결을 종료합니다."""
    global _supabase_client
    if _supabase_client:
        # Supabase 클라이언트는 명시적 연결 종료가 필요 없음
        _supabase_client = None 