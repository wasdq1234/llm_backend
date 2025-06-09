# Supabase 설정 가이드

## 🚨 RLS (Row Level Security) 문제 해결

프로필 생성 시 다음과 같은 에러가 발생한다면:

```
프로필 생성 실패: HTTP 400: {"detail":"프로필 생성 중 오류가 발생했습니다: {'message': 'new row violates row-level security policy for table \"profiles\"', 'code': '42501'..."}
```

이는 Supabase의 Row Level Security 정책 때문입니다.

## 해결 방법

### 방법 1: 개발용 스키마 사용 (권장)

1. **Supabase Dashboard** 접속
2. **SQL Editor**로 이동
3. **`supabase_schema_dev.sql`** 파일의 내용을 복사하여 실행
4. ✅ 이 방법은 RLS를 완전히 비활성화하여 개발하기 편리합니다

### 방법 2: 기존 스키마 수정

이미 `supabase_schema.sql`을 실행했다면:

1. **Supabase Dashboard** → **SQL Editor**
2. 다음 SQL 실행:

```sql
-- 임시 정책 추가 (모든 사용자 접근 허용)
CREATE POLICY "Allow all access to profiles" ON profiles
    FOR ALL USING (true);

CREATE POLICY "Allow all access to careers" ON careers
    FOR ALL USING (true);

CREATE POLICY "Allow all access to projects" ON projects
    FOR ALL USING (true);
```

### 방법 3: RLS 완전 비활성화

1. **Supabase Dashboard** → **SQL Editor**
2. 다음 SQL 실행:

```sql
-- RLS 비활성화
ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE careers DISABLE ROW LEVEL SECURITY;
ALTER TABLE projects DISABLE ROW LEVEL SECURITY;
```

## 프로덕션 환경에서는?

프로덕션 환경에서는 사용자 인증을 구현하고 적절한 RLS 정책을 설정해야 합니다.

### 사용자 인증 후 RLS 재설정

```sql
-- 임시 정책 삭제
DROP POLICY "Allow all access to profiles" ON profiles;
DROP POLICY "Allow all access to careers" ON careers;
DROP POLICY "Allow all access to projects" ON projects;

-- 사용자별 정책 생성
CREATE POLICY "Users can access their own profiles" ON profiles
    FOR ALL USING (auth.uid()::text = id::text);

CREATE POLICY "Users can access their own careers" ON careers
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = careers.profile_id 
            AND auth.uid()::text = profiles.id::text
        )
    );

CREATE POLICY "Users can access their own projects" ON projects
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM careers 
            JOIN profiles ON profiles.id = careers.profile_id
            WHERE careers.id = projects.career_id 
            AND auth.uid()::text = profiles.id::text
        )
    );
```

## 확인 방법

설정이 완료되면 Streamlit UI에서 프로필 생성을 테스트해보세요:

1. **서버 실행**: `python main.py`
2. **UI 실행**: `streamlit run test_ui.py` 또는 새로운 UI 파일 실행
3. **프로필 생성 테스트**: "👤 프로필 관리" → "➕ 프로필 생성"

## 파일 정보

- **`supabase_schema.sql`**: 프로덕션용 스키마 (개발용 임시 정책 포함)
- **`supabase_schema_dev.sql`**: 개발용 스키마 (RLS 비활성화)

## 주의사항

⚠️ **개발용 설정은 보안이 약합니다!**
- 모든 사용자가 모든 데이터에 접근 가능
- 프로덕션에서는 반드시 사용자 인증과 적절한 RLS 정책 구현 필요 