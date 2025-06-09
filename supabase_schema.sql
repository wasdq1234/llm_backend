-- 프로필 관리 시스템 데이터베이스 스키마
-- Supabase에서 실행할 SQL 스크립트

-- 1. 프로필 기본 정보 테이블
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255) UNIQUE NOT NULL,
    bio TEXT, -- 자기소개
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 경력사항 테이블
CREATE TABLE careers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    company_name VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE, -- NULL이면 현재 재직중
    job_description TEXT,
    position VARCHAR(100), -- 직책
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 프로젝트 테이블
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    career_id UUID NOT NULL REFERENCES careers(id) ON DELETE CASCADE,
    project_name VARCHAR(200) NOT NULL,
    start_date DATE,
    end_date DATE,
    description TEXT,
    technologies TEXT[], -- 사용 기술 스택 (배열로 저장)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 성능 최적화를 위한 인덱스 생성
CREATE INDEX idx_careers_profile_id ON careers(profile_id);
CREATE INDEX idx_projects_career_id ON projects(career_id);
CREATE INDEX idx_profiles_email ON profiles(email);

-- updated_at 자동 업데이트를 위한 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- updated_at 트리거 생성
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_careers_updated_at
    BEFORE UPDATE ON careers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) 설정
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE careers ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- RLS 정책 생성 (사용자 인증이 구현된 경우에만 적용)
-- 현재는 주석 처리하고, 필요시 활성화
/*
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
*/

-- 샘플 데이터 (테스트용)
INSERT INTO profiles (name, address, phone, email, bio) VALUES 
('김개발', '서울시 강남구', '010-1234-5678', 'kim@example.com', '5년차 백엔드 개발자입니다. Python과 FastAPI에 능숙하며, 클라우드 환경에서의 개발 경험이 풍부합니다.');

INSERT INTO careers (profile_id, company_name, start_date, end_date, job_description, position) VALUES 
((SELECT id FROM profiles WHERE email = 'kim@example.com'), 
 '테크스타트업', '2022-01-01', NULL, 'FastAPI를 활용한 백엔드 API 개발 및 AWS 클라우드 인프라 구축', '시니어 백엔드 개발자');

INSERT INTO projects (career_id, project_name, start_date, end_date, description, technologies) VALUES 
((SELECT id FROM careers WHERE company_name = '테크스타트업'), 
 'AI 챗봇 시스템', '2023-06-01', '2024-02-01', 
 'LLM을 활용한 고객 서비스 챗봇 시스템 개발', 
 ARRAY['Python', 'FastAPI', 'LangChain', 'PostgreSQL', 'Docker']); 