from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from ..utils.logging import logger
from ..config import settings
from .strategies import StrategyFactory
import json

MOCK_LLM_RESPONSE = {
    "error_category": "Rate Limit Exceeded",
    "recovery_action": "RETRY",
    "wait_seconds": 2,
    "rationale": "We hit a 429 error. Standard protocol is to wait and retry."
}

class AutomatedWatchdog:
    def __init__(self):
        self.llm = None
        self.chain = None
        self.using_ollama = False
        
        try:
            # Initialize Ollama LLM
            ollama_base_url = settings.OLLAMA_BASE_URL
            ollama_model = settings.OLLAMA_MODEL
            
            self.llm = OllamaLLM(
                base_url=ollama_base_url,
                model=ollama_model,
                temperature=0
            )
            
            # Define Parser
            self.parser = JsonOutputParser()
            
            # Define Prompt
            template = """Act as a Site Reliability Engineer. Analyze the following error in a Python requests pipeline:
Error: {error_msg}
Context: {context}

Return ONLY a valid JSON object with this exact schema:
{{"error_category": "string", "recovery_action": "RETRY | FAILOVER | ESCALATE", "wait_seconds": 2, "rationale": "string"}}

Respond with ONLY the JSON, no other text."""
            
            prompt = PromptTemplate(
                template=template,
                input_variables=["error_msg", "context"]
            )
            
            # Create Chain
            self.chain = prompt | self.llm
            self.using_ollama = True
            logger.info(f"✓ Watchdog initialized with Ollama ({ollama_model})")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama: {e}. Will use MOCK mode.")
            self.using_ollama = False

    def analyze_error(self, error: Exception, context: dict) -> dict:
        error_msg = str(error)
        logger.info(f"Watchdog activated. Analyzing error: {error_msg}")
        
        if self.chain and self.using_ollama:
            try:
                # Invoke Chain and get response
                response = self.chain.invoke({"error_msg": error_msg, "context": context})
                
                # Parse JSON from response
                try:
                    # Handle markdown-wrapped JSON (```json ... ```)
                    json_str = response
                    if "```" in response:
                        # Extract JSON between markdown code blocks
                        json_str = response.split("```")[1]
                        if json_str.startswith("json"):
                            json_str = json_str[4:]  # Remove "json" prefix
                        json_str = json_str.strip()
                    
                    plan_json = json.loads(json_str)
                    logger.info(f"✓ Ollama Watchdog Plan: {plan_json}")
                    return plan_json
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse JSON response: {response[:100]}")
                    # Extract recovery_action from response if possible
                    if "RETRY" in response.upper():
                        return {"error_category": "API Error", "recovery_action": "RETRY", "wait_seconds": 2, "rationale": error_msg}
                    elif "FAILOVER" in response.upper():
                        return {"error_category": "API Error", "recovery_action": "FAILOVER", "wait_seconds": 0, "rationale": error_msg}
                    
            except Exception as e:
                logger.warning(f"Ollama call failed: {e}. Falling back to MOCK.")
        
        # Fallback to mock
        plan_json = MOCK_LLM_RESPONSE
        logger.info(f"Using MOCK Plan: {plan_json}")
        return plan_json

