from abc import ABC, abstractmethod
from typing import Dict, Any
import json
import httpx
from app.utils.logger import logger
from app.utils.exceptions import LLMError

class LLMProvider(ABC):
    """Abstract base for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate response from LLM"""
        pass

class GeminiProvider(LLMProvider):
    """Google Gemini 2.0 Flash provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "gemini-2.0-flash"
        logger.info(f"GeminiProvider initialized with model {self.model_name}")
        self._client = None
    
    @property
    def client(self):
        """Lazy load Gemini client"""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model_name)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                raise LLMError(f"Gemini initialization failed: {str(e)}")
        return self._client
    
    async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate response from Gemini"""
        try:
            # Build full prompt with context
            full_prompt = f"{prompt}\n\nContext: {json.dumps(context)}"
            
            logger.info("Calling Gemini API")
            response = self.client.generate_content(full_prompt)
            
            result = response.text
            logger.info("Gemini response received")
            return result
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise LLMError(f"Gemini generation failed: {str(e)}")

class DeepSeekProvider(LLMProvider):
    """DeepSeek V3 provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.model_name = "deepseek-chat"
        logger.info(f"DeepSeekProvider initialized with model {self.model_name}")
    
    async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate response from DeepSeek"""
        try:
            full_prompt = f"{prompt}\n\nContext: {json.dumps(context)}"
            
            async with httpx.AsyncClient() as client:
                logger.info("Calling DeepSeek API")
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": full_prompt}],
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code != 200:
                    raise LLMError(f"DeepSeek API error: {response.status_code}")
                
                result = response.json()["choices"][0]["message"]["content"]
                logger.info("DeepSeek response received")
                return result
        except Exception as e:
            logger.error(f"DeepSeek generation failed: {e}")
            raise LLMError(f"DeepSeek generation failed: {str(e)}")

class LLMService:
    """Service for LLM operations with provider fallback"""
    
    def __init__(self, gemini_key: str, deepseek_key: str):
        self.providers = [
            GeminiProvider(gemini_key),
            DeepSeekProvider(deepseek_key)
        ]
        self.current_idx = 0
        logger.info(f"LLMService initialized with {len(self.providers)} providers")
    
    async def generate_with_fallback(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate with provider fallback"""
        last_error = None
        
        for i, provider in enumerate(self.providers):
            try:
                logger.info(f"Attempting generation with provider {i+1}/{len(self.providers)}")
                result = await provider.generate(prompt, context)
                self.current_idx = i  # Set as current successful provider
                return result
            except Exception as e:
                logger.warning(f"Provider {i+1} failed: {e}")
                last_error = e
                continue
        
        # All providers failed
        logger.error(f"All LLM providers exhausted. Last error: {last_error}")
        raise LLMError(f"All LLM providers failed. Last error: {str(last_error)}")
    
    async def segment_user(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """Classify user segment based on events"""
        prompt = """Analyze these user behavior events and classify the visitor into ONE segment:

SEGMENTS:
1. ML_ENGINEER: Heavy AI/ML project focus
2. FULLSTACK_DEV: Balanced frontend/backend interest
3. RECRUITER: Quick scan, contact-focused
4. STUDENT: Exploratory, long session time
5. CASUAL: Brief visit, no clear pattern

Respond ONLY with JSON (no markdown):
{"segment": "SEGMENT_NAME", "confidence": 0.0-1.0, "reasoning": "brief explanation"}"""
        
        try:
            result_str = await self.generate_with_fallback(prompt, events)
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', result_str, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(result_str)
            
            return result
        except Exception as e:
            logger.error(f"Segmentation failed: {e}")
            # Return default segment on failure
            return {"segment": "CASUAL", "confidence": 0.5, "reasoning": "Default due to error"}
    
    async def generate_rules(self, events: Dict[str, Any], segment: str) -> Dict[str, Any]:
        """Generate personalization rules for segment"""
        prompt = f"""Based on segment {segment} and behavior patterns, generate personalization rules.

Respond ONLY with JSON (no markdown):
{{"priority_sections": ["section1", "section2"], "featured_projects": ["proj1", "proj2"], "highlight_skills": ["skill1"], "reasoning": "brief explanation"}}"""
        
        try:
            result_str = await self.generate_with_fallback(prompt, events)
            
            import re
            json_match = re.search(r'\{.*\}', result_str, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(result_str)
            
            return result
        except Exception as e:
            logger.error(f"Rule generation failed: {e}")
            return {
                "priority_sections": ["projects", "skills"],
                "featured_projects": [],
                "highlight_skills": [],
                "reasoning": "Default rules due to error"
            }
