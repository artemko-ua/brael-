#Bot X4.2.1.1
#!pip install deep_translator
import requests
import os
from typing import List, Dict
import json
import nest_asyncio
from enum import Enum
import time
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import re
from deep_translator import GoogleTranslator
GROQ_API_KEY = input("Enter your GROQ API key: (type '? to get tutorial for getting api) ")
if GROQ_API_KEY == "?":
    print("To get your GROQ API key, you need to register on the official website of the service: https://console.groq.com/keys and get the key for the API.")
    GROQ_API_KEY = input("And now enter your GROQ API key: ")
else:
    GROQ_API_KEY = GROQ_API_KEY
nest_asyncio.apply()
name = "OpiuMN"

class SearchEngine:
    def __init__(self):
        self.session = None
        self.translator = GoogleTranslator(source='auto', target='en')

    async def _create_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def search(self, query: str, original_lang: str = 'uk') -> dict:
        """
        Performs search with translation to English and back
        """
        try:
            # Translate query to English if needed
            try:
                english_query = self.translator.translate(query)
                print(f"\n🔍 Шукаю: '{query}' (EN: '{english_query}')")
            except:
                english_query = query
                print(f"\n🔍 Шукаю: '{query}'")

            await self._create_session()
            search_url = f"https://duckduckgo.com/html/?q={english_query}&t=h_"

            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    results = []
                    # Create translator once for all results
                    translator = GoogleTranslator(source='en', target=original_lang)

                    # Batch process results
                    batch_texts = []
                    result_items = []

                    for result in soup.find_all('div', {'class': 'result'})[:5]:
                        title = result.find('a', {'class': 'result__a'})
                        snippet = result.find('a', {'class': 'result__snippet'})

                        if title and snippet:
                            title_text = title.text.strip()
                            snippet_text = snippet.text.strip()

                            if original_lang != 'en':
                                batch_texts.extend([title_text, snippet_text])

                            result_items.append({
                                'title': title_text,
                                'snippet': snippet_text,
                                'url': title['href']
                            })

                    # Batch translate if needed
                    if original_lang != 'en' and batch_texts:
                        try:
                            translated_texts = translator.translate_batch(batch_texts)

                            for i, item in enumerate(result_items):
                                item['title'] = translated_texts[i*2]
                                item['snippet'] = translated_texts[i*2 + 1]
                        except:
                            # If translation fails, use original texts
                            pass

                    results.extend(result_items)

                    print("✅ Пошук завершено!")
                    return {
                        'query': query,
                        'status': 'success',
                        'results': results,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    print("❌ Помилка пошуку")
                    return {
                        'query': query,
                        'status': 'error',
                        'message': f'HTTP Error: {response.status}'
                    }
        except Exception as e:
            print(f"❌ Помилка: {str(e)}")
            return {
                'query': query,
                'status': 'error',
                'message': str(e)
            }
        finally:
            await self.close()

class PreprocessorAgent:
    def __init__(self):
        self.model_id = "mixtral-8x7b-32768"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.search_engine = SearchEngine()
        self.translator = GoogleTranslator(source='auto', target='en')

    def _make_api_call(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_id,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 5001
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {str(e)}"

    async def analyze_query(self, user_query: str) -> List[str]:
        try:
            english_query = self.translator.translate(user_query)
        except:
            english_query = user_query

        messages = [
            {
                "role": "system",
                "content": """YQuery Analyzer v5.0.0


1. QUERY CLASSIFICATION:
   IF input contains request for:
   -Search if the user has asked you directly
   - Current events/news
   - Real-time data
   - Location-specific information
   - Price/availability checks
   - Weather/traffic conditions
   - Recent updates
   THEN output-> SEARCH: [specific_search_terms]

   IF input requests:
   - Basic facts
   - Definitions
   - Historical info
   - Theoretical concepts
   - Standard procedures
   THEN output-> NO_SEARCH: [direct_response]

2. RESPONSE STRUCTURE:
   FOR DYNAMIC QUERIES:
   SEARCH: [core_search_terms]
   Parameters:
   - Time sensitivity: [real-time/daily/none]
   - Geographic scope: [local/global/none]
   - Update frequency: [continuous/periodic/once]
   - Priority: [1-5]

   FOR STATIC QUERIES:
   NO_SEARCH: [concise_explanation]
   Type: [concept/fact/definition/procedure]
   Context: [relevant_domain]

3. PROCESSING RULES:
   - Extract key search terms
   - Remove unnecessary words
   - Identify temporal context
   - Determine geographic scope
   - Set information freshness requirements
   - Evaluate search priority

4. VALIDITY CHECKS:
   - Confirm query completeness
   - Verify temporal relevance
   - Check geographic applicability
   - Validate data requirements
   - Ensure response format compliance

OUTPUT FORMAT:
For dynamic content:
SEARCH: [precise_search_query]

For static content:
NO_SEARCH: [direct_answer]"""
            },
            {
                "role": "user",
                "content": english_query
            }
        ]

        response = self._make_api_call(messages)
        if response.startswith("Error:") or response == "NO_SEARCH":
            return []

        search_queries = []
        for line in response.split('\n'):
            if line.startswith('SEARCH:'):
                search_queries.append(line.replace('SEARCH:', '').strip())

        return search_queries

    async def preprocess_query(self, user_query: str) -> str:
        try:
            original_lang = GoogleTranslator().detect(user_query)
        except:
            original_lang = 'uk'

        search_queries = await self.analyze_query(user_query)

        if not search_queries:
            return user_query

        search_results = []
        for query in search_queries:
            result = await self.search_engine.search(query, original_lang)
            if result['status'] == 'success':
                search_results.append(result)

        if search_results:
            context = f"""Current search results as of {time.strftime('%Y-%m-%d %H:%M:%S')}:

"""
            for result in search_results:
                context += f"Search query: {result['query']}\n"
                for item in result['results']:
                    context += f"• {item['title']}\n{item['snippet']}\n\n"

            enriched_query = f"""Original question: {user_query}

{context}

Please provide a comprehensive response based on the CURRENT search results above.
Important: Use ONLY the information from these search results, and use the correct ."""

            return enriched_query

        return user_query

class ModelAgent:
    def __init__(self, model_id: str, name: str):
        self.model_id = model_id
        self.name = name
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.conversation_history = []
        self.translator = GoogleTranslator(source='auto', target='uk')

    def generate_response(self, prompt: str) -> str:
        try:
            original_lang = GoogleTranslator().detect(prompt)
            self.translator = GoogleTranslator(source='en', target=original_lang)
        except:
            pass

        system_message = """"
Bot X4.2.1 Identification:
- Name: OpiuMN
- Creator: Be_Alex (Ukraine)
Main functions:
- Match user's language
- Provide direct answers
- Focus on current data
- Talk to the user in his language (in the language in which he asks the question)
- Processing of information in real time
Structure of the answer:
- Concise and accurate presentation of information
- Only key points (but not headlines)
- Relevant facts first
- Regional relevance
- Clear formatting

"""

        response = self._make_api_call(prompt, system_message)
        return response

    def _make_api_call(self, prompt: str, system_message: str) -> str:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": system_message}
        ]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model_id,
            "messages": messages,
            "max_tokens": 5005
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            response_content = response.json()["choices"][0]["message"]["content"]

            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": response_content})

            return response_content
        except Exception as e:
            return f"Error: {str(e)}"

    def clear_history(self):
        self.conversation_history = []

class CouncilBot:
    def __init__(self):
        self.preprocessor = PreprocessorAgent()
        self.agents = [
            ModelAgent("llama-3.2-90b-vision-preview", "Strategic Advisor"),
            ModelAgent("mixtral-8x7b-32768", "Knowledge Expert"),
            ModelAgent("llama3-groq-70b-8192-tool-use-preview", "Concise Summarizer")
        ]

    async def get_council_response(self, user_query: str) -> str:
        print("\n🤖 Препроцесор аналізує запит...")
        enriched_query = await self.preprocessor.preprocess_query(user_query)

        responses = []
        for agent in self.agents:
            try:
                response = agent.generate_response(enriched_query)
                if not response.startswith("Error:"):
                    responses.append(response)
            except Exception as e:
                continue

        if not responses:
            return "Сервіс тимчасово недоступний. Будь ласка, спробуйте пізніше."

        return max(responses, key=len) if responses else "Немає доступної відповіді."

    def clear_all_histories(self):
        for agent in self.agents:
            agent.clear_history()

async def run_chatbot():
    bot = CouncilBot()
    print("Welcome to the AI Council Chat Bot!")
    print("Type 'exit' to end the conversation")
    print("Type 'clear' to clear conversation history")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'clear':
            bot.clear_all_histories()
            print("\nConversation history cleared!")
            continue

        response = await bot.get_council_response(user_input)
        print("\nAI:", response)

if __name__ == "__main__":
    asyncio.run(run_chatbot())
