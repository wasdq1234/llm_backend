#!/usr/bin/env python3
"""
FastAPI 엔드포인트 테스트 UI 실행 스크립트
"""

import subprocess
import sys
import os

def main():
    """Streamlit 테스트 UI 실행"""
    print("🔧 FastAPI 엔드포인트 테스터를 시작합니다...")
    print("📝 사용법:")
    print("   1. FastAPI 서버가 실행 중인지 확인하세요 (http://localhost:8000)")
    print("   2. 브라우저에서 Streamlit UI를 사용하여 API를 테스트하세요")
    print("   3. 종료하려면 Ctrl+C를 누르세요")
    print("-" * 50)
    
    try:
        # Streamlit 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "test_ui.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 테스트 UI를 종료합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("💡 streamlit이 설치되어 있는지 확인하세요: pip install streamlit")

if __name__ == "__main__":
    main() 