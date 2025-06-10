"""
프로필 도구를 활용한 채팅 서비스
Profile tools를 사용하여 사용자 질문에 대답하는 AI 서비스
"""

import uuid
from typing import AsyncGenerator, Optional, List, Dict, Any


from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import Annotated, TypedDict

from app.core.config import settings
from app.models.chat import StreamChunk, ChatMessage, MessageRole

from app.services.tools import get_profile_info, get_careers_by_profile, get_projects_by_profile, get_profile_with_full_details


class ChatToolState(TypedDict):
    """채팅 도구 상태"""
    messages: Annotated[list, add_messages]
    conversation_id: str
    profile_id: str
    model_name: str


class ChatToolService:
    """프로필 도구를 활용한 채팅 서비스"""
    
    def __init__(self):
        self.memory = MemorySaver()
        self.tools = [
            get_profile_info, 
            get_careers_by_profile, 
            get_projects_by_profile, 
            get_profile_with_full_details
        ]
        self.graph = self._create_chat_tool_graph()
        
    def _get_llm(self, model_name: str = None):
        """Get LLM instance based on model name"""
        model = model_name or settings.default_model
        
        if model.startswith("gpt"):
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return ChatOpenAI(
                model=model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                openai_api_key=settings.openai_api_key,
                streaming=True
            )
        elif model.startswith("claude"):
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            return ChatAnthropic(
                model=model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                anthropic_api_key=settings.anthropic_api_key,
                streaming=True
            )
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    def _create_chat_tool_graph(self) -> StateGraph:
        """프로필 도구를 사용하는 채팅 그래프 생성"""
        
        async def agent_node(state: ChatToolState):
            """에이전트 노드 - LLM이 도구를 사용할지 결정"""
            llm = self._get_llm(state.get("model_name"))
            llm_with_tools = llm.bind_tools(self.tools)
            
            # 시스템 프롬프트 설정
            system_prompt = f"""당신은 전문 프로필 관리 AI 어시스턴트입니다.
현재 프로필 ID: {state.get('profile_id')}

사용 가능한 도구:
1. get_profile_info: 기본 프로필 정보 조회 (이름, 이메일, 연락처, 자기소개)
2. get_careers_by_profile: 경력사항 조회 (회사, 직책, 근무기간, 업무내용)
3. get_projects_by_profile: 프로젝트 조회 (프로젝트명, 기간, 설명, 기술스택)
4. get_profile_with_full_details: 모든 정보를 한번에 조회 (기본정보 + 경력 + 프로젝트)

응답 가이드라인:
- 사용자가 "프로필 정보", "기본 정보"를 물으면 → get_profile_info 사용
- 사용자가 "경력", "회사", "직장", "커리어"를 물으면 → get_careers_by_profile 사용  
- 사용자가 "프로젝트", "포트폴리오", "작업"을 물으면 → get_projects_by_profile 사용
- 사용자가 "전체", "모든", "상세", "다 보여줘"를 물으면 → get_profile_with_full_details 사용
- 조회된 정보를 정리하여 사용자에게 친근하게 전달
- 정보가 없거나 오류가 발생하면 명확하게 안내
- 항상 정중하고 도움이 되는 톤으로 응답
- 사용자는 해당 프로필에 궁금한게 있어 질문을 하는거라 친절하게 응답"""

            # 메시지 준비
            messages = state["messages"]
            if not any(isinstance(msg, SystemMessage) for msg in messages):
                system_msg = SystemMessage(content=system_prompt)
                messages = [system_msg] + messages
            
            # LLM 호출
            response = await llm_with_tools.ainvoke(messages)
            
            return {
                "messages": [response],
                "conversation_id": state["conversation_id"],
                "profile_id": state["profile_id"],
                "model_name": state["model_name"]
            }
        
        def should_continue(state: ChatToolState) -> str:
            """다음 노드 결정"""
            messages = state["messages"]
            last_message = messages[-1]
            
            # AI 메시지에 tool_calls가 있으면 tools 노드로
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            return END
        
        # Tool 노드
        tool_node = ToolNode(self.tools)
        
        # StateGraph 생성
        workflow = StateGraph(ChatToolState)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        
        # 엣지 설정
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")
        
        return workflow.compile(checkpointer=self.memory)
    
    def _convert_messages_to_langchain(self, messages: List[ChatMessage]) -> List:
        """Convert ChatMessage list to LangChain message format"""
        langchain_messages = []
        
        for msg in messages:
            if msg.role == MessageRole.USER:
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.ASSISTANT:
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == MessageRole.SYSTEM:
                langchain_messages.append(SystemMessage(content=msg.content))
        
        return langchain_messages


    
    async def stream_chat_with_profile_tools(
        self,
        message: str,
        profile_id: str,
        messages: Optional[List[ChatMessage]] = None,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """프로필 도구를 사용한 스트리밍 채팅"""
        
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        try:
            # Create thread config
            config = {"configurable": {"thread_id": conversation_id}}
            
            # Prepare messages
            if messages:
                input_messages = self._convert_messages_to_langchain(messages)
                input_messages.append(HumanMessage(content=message))
            else:
                input_messages = [HumanMessage(content=message)]

            # Prepare input
            input_data = {
                "messages": input_messages,
                "conversation_id": conversation_id,
                "profile_id": profile_id,
                "model_name": model or settings.default_model
            }
            
            # Stream through graph
            async for chunk in self.graph.astream(input_data, config=config, stream_mode="updates"):
                for node_name, node_output in chunk.items():
                    
                    if node_name == "agent":
                        # 에이전트 노드에서 나온 메시지 처리
                        if "messages" in node_output:
                            for msg in node_output["messages"]:
                                if isinstance(msg, AIMessage):
                                    # 도구 호출이 있는 경우
                                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                        for tool_call in msg.tool_calls:
                                            yield StreamChunk(
                                                content=f"도구 호출 중: {tool_call['name']}",
                                                conversation_id=conversation_id,
                                                is_final=False,
                                                chunk_type="tool_calling"
                                            )
                                    
                                    # AI 응답 내용이 있는 경우 (최종 응답)
                                    elif hasattr(msg, 'content') and msg.content and msg.content.strip():
                                        yield StreamChunk(
                                            content=f"AI 응답:\n{msg.content}",
                                            conversation_id=conversation_id,
                                            is_final=False,
                                            chunk_type="ai_response"
                                        )
                    
                    elif node_name == "tools":
                        # 도구 노드에서 나온 결과 처리
                        if "messages" in node_output:
                            for msg in node_output["messages"]:
                                if isinstance(msg, ToolMessage):
                                    yield StreamChunk(
                                        content=f"도구 실행 결과:\n{msg.content}",
                                        conversation_id=conversation_id,
                                        is_final=False,
                                        chunk_type="tool_result"
                                    )
            
            # Send final chunk
            yield StreamChunk(
                content="",
                conversation_id=conversation_id,
                is_final=True
            )
            
        except Exception as e:
            # Yield error message as stream
            error_msg = f"죄송합니다. 프로필 정보 조회 중 오류가 발생했습니다: {str(e)}"
            yield StreamChunk(
                content=error_msg,
                conversation_id=conversation_id,
                is_final=True,
                chunk_type="error"
            )
