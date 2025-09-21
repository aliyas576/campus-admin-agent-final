import json
from typing import Dict, List, Any, Generator, AsyncGenerator
from backend.models.database import SessionLocal, ConversationMemory
from backend.tools import get_tools
from backend.config import settings

class CampusAdminAgent:
    def __init__(self):
        self.tools = get_tools()
        self.groq_client = None
        
        # Initialize Groq client with error handling
        try:
            import groq
            
            if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "GROQ_API_KEY":
                # Initialize without any extra parameters and handle proxies issue
                try:
                    # Clear any proxy environment variables that might interfere
                    import os
                    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']
                    for var in proxy_vars:
                        os.environ.pop(var, None)
                    
                    # Initialize Groq client with minimal configuration
                    self.groq_client = groq.AsyncGroq(
                        api_key=settings.GROQ_API_KEY,
                        # Explicitly set to avoid proxy issues
                        http_client=groq.HttpxAsyncClient(proxies=None)
                    )
                    print("✅ Groq client initialized successfully")
                except Exception as e:
                    print(f"⚠️  Groq client configuration error: {e}")
                    self.groq_client = None
            else:
                print("⚠️  GROQ_API_KEY not found or invalid, using rule-based responses")
                self.groq_client = None
            
        except ImportError:
            print("⚠️  Groq package not installed, using rule-based responses")
        except Exception as e:
            print(f"⚠️  Failed to initialize Groq client: {e}, using rule-based responses")
            self.groq_client = None
    
    def save_memory(self, session_id: str, role: str, message: str):
        db = SessionLocal()
        try:
            mem = ConversationMemory(session_id=session_id, role=role, message=message)
            db.add(mem)
            db.commit()
        except Exception as e:
            print(f"Error saving memory: {e}")
        finally:
            db.close()

    def load_memory(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        db = SessionLocal()
        try:
            memories = db.query(ConversationMemory).filter(
                ConversationMemory.session_id == session_id
            ).order_by(ConversationMemory.created_at.desc()).limit(limit).all()
            
            return [{"role": mem.role, "content": mem.message} for mem in memories]
        except Exception as e:
            print(f"Error loading memory: {e}")
            return []
        finally:
            db.close()

    def handle_message(self, session_id: str, user_message: str) -> str:
        self.save_memory(session_id, "user", user_message)
        
        if self.groq_client:
            return self._handle_with_groq(session_id, user_message)
        else:
            return self._handle_rule_based(session_id, user_message)

    def _handle_with_groq(self, session_id: str, user_message: str) -> str:
        try:
            history = self.load_memory(session_id)
            
            messages = [
                {"role": "system", "content": "You are a helpful campus admin assistant. Help with student management, campus information, and analytics."}
            ]
            
            for msg in reversed(history):
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": user_message})
            
            import asyncio
            response = asyncio.run(self.groq_client.chat.completions.create(
                model=settings.AGENT_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1024
            ))
            
            assistant_response = response.choices[0].message.content
            self.save_memory(session_id, "assistant", assistant_response)
            return assistant_response
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._handle_rule_based(session_id, user_message)

    def _handle_rule_based(self, session_id: str, user_message: str) -> str:
        text = user_message.lower()
        
        if "add student" in text:
            return "Please use the /students endpoint to add students with JSON data"
        elif "how many students" in text:
            total = self.tools["get_total_students"]()
            response = f"There are {total} students in the system."
            self.save_memory(session_id, "assistant", response)
            return response
        elif "list students" in text:
            result = self.tools["list_students"]()
            if "error" in result:
                return f"Error: {result['error']}"
            students = result["students"]
            response = "Students:\n" + "\n".join([f"- {s['name']} ({s['student_id']}) - {s['department']}" for s in students])
            self.save_memory(session_id, "assistant", response)
            return response
        elif "department" in text and "students" in text:
            dept_data = self.tools["get_students_by_department"]()
            response = "Students by department:\n" + "\n".join([f"- {dept}: {count} students" for dept, count in dept_data.items()])
            self.save_memory(session_id, "assistant", response)
            return response
        
        response = f"I received: '{user_message}'. I can help with student management, analytics, and campus information."
        self.save_memory(session_id, "assistant", response)
        return response

    def stream_handle_message(self, session_id: str, user_message: str) -> Generator[str, None, None]:
        full_response = self.handle_message(session_id, user_message)
        words = full_response.split()
        for word in words:
            yield word + " "
        yield "__END__"

    async def async_stream_handle_message(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        if not self.groq_client:
            for chunk in self.stream_handle_message(session_id, user_message):
                yield chunk
            return
        
        try:
            history = self.load_memory(session_id)
            messages = [
                {"role": "system", "content": "You are a helpful campus admin assistant. Help with student management, campus information, and analytics."}
            ]
            
            for msg in reversed(history):
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": user_message})
            self.save_memory(session_id, "user", user_message)
            
            full_response = ""
            stream = await self.groq_client.chat.completions.create(
                model=settings.AGENT_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            self.save_memory(session_id, "assistant", full_response)
            yield "__END__"
            
        except Exception as e:
            print(f"Groq streaming error: {e}")
            fallback_response = self._handle_rule_based(session_id, user_message)
            words = fallback_response.split()
            for word in words:
                yield word + " "
            yield "__END__"