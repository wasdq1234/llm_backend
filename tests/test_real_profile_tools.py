"""
간단한 Profile 조회 Tool 테스트
profile UUID로 profile 정보를 조회하는 기본 기능
"""
import os
import asyncio
from typing import Dict, Any
from uuid import UUID
from datetime import date

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import Annotated, TypedDict

from app.services.profile_service import ProfileService

# .env 파일에서 환경변수 로드
load_dotenv()


class ChatState(TypedDict):
    """채팅 상태"""
    messages: Annotated[list, add_messages]
    profile_id: str


@tool
async def get_profile_info(profile_id: str) -> str:
    """Profile UUID로 프로필 기본 정보를 조회합니다."""
    try:
        service = ProfileService()
        profile = await service.get_profile_by_id(UUID(profile_id))
        
        if not profile:
            return f"프로필 ID {profile_id}에 해당하는 정보를 찾을 수 없습니다."
        
        result = f"""프로필 정보:
이름: {profile.name}
이메일: {profile.email}
전화번호: {profile.phone or '정보 없음'}
주소: {profile.address or '정보 없음'}
자기소개: {profile.bio or '자기소개 없음'}"""
        
        return result
    
    except Exception as e:
        return f"프로필 조회 중 오류가 발생했습니다: {str(e)}"


@tool
async def get_careers_by_profile(profile_id: str) -> str:
    """Profile UUID로 해당 프로필의 모든 경력사항을 조회합니다."""
    try:
        service = ProfileService()
        careers = await service.get_careers_by_profile_id(UUID(profile_id))
        
        if not careers:
            return f"프로필 ID {profile_id}에 해당하는 경력사항을 찾을 수 없습니다."
        
        result = f"경력사항 ({len(careers)}개):\n\n"
        
        for i, career in enumerate(careers, 1):
            result += f"{i}. {career.company_name}\n"
            result += f"   직책: {career.position or '정보 없음'}\n"
            result += f"   근무기간: {career.start_date}"
            if career.end_date:
                result += f" ~ {career.end_date}\n"
            else:
                result += f" ~ 현재\n"
            if career.job_description:
                result += f"   업무내용: {career.job_description}\n"
            result += "\n"
        
        return result.strip()
    
    except Exception as e:
        return f"경력사항 조회 중 오류가 발생했습니다: {str(e)}"


@tool
async def get_projects_by_profile(profile_id: str) -> str:
    """Profile UUID로 해당 프로필의 모든 프로젝트를 조회합니다."""
    try:
        service = ProfileService()
        # 먼저 경력사항을 조회하고 각 경력의 프로젝트를 가져옴
        careers = await service.get_careers_by_profile_id(UUID(profile_id))
        
        if not careers:
            return f"프로필 ID {profile_id}에 해당하는 경력사항을 찾을 수 없어 프로젝트를 조회할 수 없습니다."
        
        all_projects = []
        for career in careers:
            projects = await service.get_projects_by_career_id(career.id)
            for project in projects:
                # 프로젝트에 회사 정보 추가
                project_info = {
                    "project": project,
                    "company": career.company_name
                }
                all_projects.append(project_info)
        
        if not all_projects:
            return f"프로필 ID {profile_id}에 해당하는 프로젝트를 찾을 수 없습니다."
        
        # 시작일자 기준으로 최신순 정렬
        all_projects.sort(key=lambda x: x["project"].start_date or date(1900, 1, 1), reverse=True)
        
        result = f"프로젝트 ({len(all_projects)}개):\n\n"
        
        for i, project_info in enumerate(all_projects, 1):
            project = project_info["project"]
            company = project_info["company"]
            
            result += f"{i}. {project.project_name}\n"
            result += f"   회사: {company}\n"
            if project.start_date:
                result += f"   기간: {project.start_date}"
                if project.end_date:
                    result += f" ~ {project.end_date}\n"
                else:
                    result += f" ~ 현재\n"
            else:
                result += f"   기간: 정보 없음\n"
            if project.description:
                result += f"   설명: {project.description}\n"
            if project.technologies:
                result += f"   사용기술: {', '.join(project.technologies)}\n"
            result += "\n"
        
        return result.strip()
    
    except Exception as e:
        return f"프로젝트 조회 중 오류가 발생했습니다: {str(e)}"


@tool
async def get_profile_with_full_details(profile_id: str) -> str:
    """Profile UUID로 프로필의 모든 정보(기본정보, 경력, 프로젝트)를 한번에 조회합니다."""
    try:
        service = ProfileService()
        profile_details = await service.get_profile_with_details(UUID(profile_id))
        
        if not profile_details:
            return f"프로필 ID {profile_id}에 해당하는 정보를 찾을 수 없습니다."
        
        result = f"""=== {profile_details.name}님의 상세 프로필 ===

📋 기본 정보:
이름: {profile_details.name}
이메일: {profile_details.email}
전화번호: {profile_details.phone or '정보 없음'}
주소: {profile_details.address or '정보 없음'}
자기소개: {profile_details.bio or '자기소개 없음'}

"""
        
        if profile_details.careers:
            result += f"💼 경력사항 ({len(profile_details.careers)}개):\n"
            for i, career in enumerate(profile_details.careers, 1):
                result += f"\n{i}. {career.company_name} - {career.position or '정보 없음'}\n"
                result += f"   기간: {career.start_date}"
                if career.end_date:
                    result += f" ~ {career.end_date}\n"
                else:
                    result += f" ~ 현재\n"
                if career.job_description:
                    result += f"   업무: {career.job_description}\n"
                
                # 해당 경력의 프로젝트들
                if hasattr(career, 'projects') and career.projects:
                    result += f"   📁 프로젝트 ({len(career.projects)}개):\n"
                    for j, project in enumerate(career.projects, 1):
                        result += f"   {i}-{j}. {project.project_name}\n"
                        if project.start_date:
                            result += f"        기간: {project.start_date}"
                            if project.end_date:
                                result += f" ~ {project.end_date}\n"
                            else:
                                result += f" ~ 현재\n"
                        else:
                            result += f"        기간: 정보 없음\n"
                        if project.description:
                            result += f"        설명: {project.description}\n"
                        if project.technologies:
                            result += f"        기술: {', '.join(project.technologies)}\n"
        else:
            result += "💼 등록된 경력사항이 없습니다.\n"
        
        return result
    
    except Exception as e:
        return f"상세 프로필 조회 중 오류가 발생했습니다: {str(e)}"


def create_chat_agent(profile_id: str):
    """채팅 에이전트 생성"""
    # OpenAI 모델 설정
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # System prompt 설정 (현재 프로필 ID 포함)
    system_prompt = f"""당신은 전문 프로필 관리 AI 어시스턴트입니다.
현재 프로필 ID: {profile_id}

사용 가능한 도구:
1. get_profile_info: 기본 프로필 정보 조회 (이름, 이메일, 연락처, 자기소개)
2. get_careers_by_profile: 경력사항 조회 (회사, 직책, 근무기간, 업무내용, 기술스택)
3. get_projects_by_profile: 프로젝트 조회 (프로젝트명, 기간, 설명, 역할, 기술스택)
4. get_profile_with_full_details: 모든 정보를 한번에 조회 (기본정보 + 경력 + 프로젝트)

응답 가이드라인:
- 사용자가 "프로필 정보", "기본 정보"를 물으면 → get_profile_info 사용
- 사용자가 "경력", "회사", "직장", "커리어"를 물으면 → get_careers_by_profile 사용  
- 사용자가 "프로젝트", "포트폴리오", "작업"을 물으면 → get_projects_by_profile 사용
- 사용자가 "전체", "모든", "상세", "다 보여줘"를 물으면 → get_profile_with_full_details 사용
- 사용자가 사용법을 물어보면 호출할 수 있는 도구들을 기반으로 사용법을 친절히 응답
- 조회된 정보를 정리하여 사용자에게 친근하게 전달
- 정보가 없거나 오류가 발생하면 명확하게 안내
- 항상 정중하고 도움이 되는 톤으로 응답
- 사용자는 해당 프로필의 본인이 아니고 프로필에 궁금한게 있어 질문을 하는거라 친절하게 응답
- 사용자의 질문에 정보가 없으면 해당 정보가 없다고 간결하게 응답

자동 프로필 조회 키워드:
프로필 정보, 내 정보, 정보 보여줘, 프로필 조회, 정보 알려줘, 안녕, 안녕하세요, 경력, 프로젝트, 전체 정보"""

    # Tool 설정
    tools = [get_profile_info, get_careers_by_profile, get_projects_by_profile, get_profile_with_full_details]
    llm_with_tools = llm.bind_tools(tools)
    tool_node = ToolNode(tools)
    
    # Prompt template 생성
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}")
    ])
    
    def should_continue(state: ChatState) -> str:
        """다음 노드 결정"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # AI 메시지에 tool_calls가 있으면 tools 노드로
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return END
    
    def call_model(state: ChatState) -> Dict[str, Any]:
        """LLM 호출"""
        # Prompt template을 통해 system prompt가 포함된 메시지 생성
        formatted_prompt = prompt.invoke(state)
        response = llm_with_tools.invoke(formatted_prompt.messages)
        return {"messages": [response]}
    
    # StateGraph 생성
    workflow = StateGraph(ChatState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    # 엣지 설정
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    # 그래프 컴파일
    return workflow.compile()


async def interactive_chat(profile_id: str):
    """대화형 채팅 테스트"""
    print("=" * 60)
    print("🤖 Profile AI 어시스턴트 (스트리밍 모드)")
    print("=" * 60)
    print(f"📋 관리 중인 프로필 ID: {profile_id}")
    print("💬 'quit' 또는 'exit' 입력 시 종료")
    print()
    
    # 에이전트 생성
    app = create_chat_agent(profile_id)
    
    while True:
        try:
            # 사용자 입력
            user_input = input("\n🙋 사용자: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("👋 채팅을 종료합니다!")
                break
                
            if not user_input:
                continue
                
            print("\n" + "─" * 50)
            
            # 스트리밍 방식으로 응답 생성
            async for chunk in app.astream(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "profile_id": profile_id
                },
                config={"recursion_limit": 5},
                stream_mode="updates"  # updates 모드로 변경
            ):
                # 각 노드의 업데이트 처리
                for node_name, node_output in chunk.items():
                    print(f"🔄 노드: {node_name}")
                    
                    if "messages" in node_output:
                        for message in node_output["messages"]:
                            # AI 메시지 처리
                            if isinstance(message, AIMessage):
                                # 도구 호출이 있는 경우
                                if hasattr(message, 'tool_calls') and message.tool_calls:
                                    print("🔧 도구 호출:")
                                    for tool_call in message.tool_calls:
                                        print(f"   📍 {tool_call['name']}({tool_call['args']})")
                                
                                # AI 응답 내용이 있는 경우
                                if hasattr(message, 'content') and message.content and message.content.strip():
                                    print("🤖 AI 응답:")
                                    print(f"   {message.content}")
                            
                            # 도구 메시지 처리
                            elif isinstance(message, ToolMessage):
                                print("📋 도구 실행 결과:")
                                print(f"   {message.content}")
                    
                    print()  # 각 노드 처리 후 줄바꿈
            
            print("─" * 50)
                
        except KeyboardInterrupt:
            print("\n👋 Ctrl+C로 종료됩니다!")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            print("계속 채팅하려면 다른 메시지를 입력하세요.")


async def main():
    """메인 함수"""
    profile_uuid = "f2cc2311-97e2-445c-8bec-1192b9042c46"
    
    # 1. 대화형 채팅 시작 (profile_uuid를 전달)
    await interactive_chat(profile_uuid)


if __name__ == "__main__":
    asyncio.run(main()) 