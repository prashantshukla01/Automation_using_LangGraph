from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from ..utils.logging import logger
from ..config import settings
from .strategies import StrategyFactory

MOCK_LLM_RESPONSE = {
    "error_category": "Rate Limit Exceeded",
    "recovery_action": "RETRY",
    "wait_seconds": 2,
    "rationale": "We hit a 429 error. Standard protocol is to wait and retry."
}

class AutomatedWatchdog:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.llm = None
        self.chain = None
        
        if self.api_key:
            try:
                # Initialize Gemini via LangChain
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    google_api_key=self.api_key,
                    temperature=0
                )
                
                # Define Parser
                self.parser = JsonOutputParser()
                
                # Define Prompt
                template = """
                Act as a Site Reliability Engineer. 
                Analyze the following error in a Python requests pipeline:
                Error: {error_msg}
                Context: {context}
                
                Return ONLY a valid JSON object with the following schema:
                {{
                    "error_category": "string", 
                    "recovery_action": "RETRY | FAILOVER | ESCALATE | UPDATE_URL", 
                    "wait_seconds": "int", 
                    "rationale": "string"
                }}
                
                {format_instructions}
                """
                
                prompt = PromptTemplate(
                    template=template,
                    input_variables=["error_msg", "context"],
                    partial_variables={"format_instructions": self.parser.get_format_instructions()}
                )
                
                # Create Chain
                self.chain = prompt | self.llm | self.parser
                logger.info("Watchdog initialized with LangChain Gemini.")
                
            except Exception as e:
                logger.error(f"Failed to configure LangChain Gemini: {e}")
        else:
            logger.info("Watchdog starting in MOCK MODE (No API Key provided)")

    def analyze_error(self, error: Exception, context: dict) -> dict:
        error_msg = str(error)
        logger.info(f"Watchdog activated. Analyzing error: {error_msg}")
        
        if self.chain:
            try:
                # Invoke Chain
                plan_json = self.chain.invoke({"error_msg": error_msg, "context": context})
                logger.info(f"Gemini Watchdog Plan: {plan_json}")
                return plan_json
                
            except OutputParserException as e:
                logger.error(f"Output Parsing Failed: {e}")
            except Exception as e:
                logger.error(f"LangChain Call Failed: {e}. Falling back to MOCK.")
        
        # Fallback
        plan_json = MOCK_LLM_RESPONSE
        logger.info(f"Using Mock Plan: {plan_json}")
        return plan_json

