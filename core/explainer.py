# core/explainer.py
from openai import OpenAI
from config.settings import Settings
from typing import Optional

class OpenRouterExplainer:
    def __init__(self):
        self.client = OpenAI(
            api_key=Settings.OPENROUTER_API_KEY,
            base_url=Settings.OPENROUTER_BASE_URL
        )
        self.model = Settings.OPENROUTER_MODEL
    
    def explain_code(self, code: str, context: str = "", question: str = "") -> str:
        """Explain code using OpenRouter"""
        
        prompt = f"""You are a helpful code assistant. Explain the following code:

CONTEXT: {context}
QUESTION: {question}

CODE:
```python
{code}
```

Provide a clear explanation focusing on:
1. What this code does
2. Key functions and their purposes
3. Important variables or data structures
4. Any patterns or best practices used
5. Potential issues or improvements

Be concise but comprehensive."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior software engineer explaining code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=Settings.TEMPERATURE,
                max_tokens=Settings.MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting explanation: {str(e)}"
    
    def explain_impact(self, component: str, dependencies: list, callers: list) -> str:
        """Explain impact of changing a component"""
        
        prompt = f"""Analyze the impact of changing this component:

COMPONENT TO CHANGE: {component}

DEPENDENCIES (things this component uses):
{dependencies[:10]}

CALLERS (things that call this component):
{callers[:10]}

What would break if we change this component?
Provide:
1. Direct impact on callers
2. Indirect impact through dependencies
3. Testing considerations
4. Migration strategy
5. Risk assessment (Low/Medium/High)"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a software architect analyzing change impact."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more deterministic analysis
                max_tokens=5000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing impact: {str(e)}"

def explain_code(self, code: str, context: str = "", question: str = "") -> str:
    """Explain code using OpenRouter"""
    
    prompt = f"""You are a helpful code assistant. Explain the following code:

CONTEXT: {context}
QUESTION: {question}

CODE:
```python
{code}
```

Provide a clear explanation focusing on:
1. What this code does
2. Key functions and their purposes
3. Important variables or data structures
4. Any patterns or best practices used
5. Potential issues or improvements

Be concise but comprehensive."""
    
    try:
        print(f"DEBUG: Using model {self.model}")  # Debug line
        print(f"DEBUG: API Key present: {bool(Settings.OPENROUTER_API_KEY)}")  # Debug line
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a senior software engineer explaining code."},
                {"role": "user", "content": prompt}
            ],
            temperature=Settings.TEMPERATURE,
            max_tokens=Settings.MAX_TOKENS
        )
        return response.choices[0].message.content
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error getting explanation: {str(e)}\n\nDetails:\n{error_details}"
