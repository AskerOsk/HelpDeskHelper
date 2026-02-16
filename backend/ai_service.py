"""
AI Service - Ollama Integration for Sulpak HelpDesk
Handles intelligent customer support responses
"""

import os
import logging
from typing import Dict, List, Tuple, Optional
import httpx
from dotenv import load_dotenv
from constants import (
    AI_MODEL_DEFAULT,
    AI_CONFIDENCE_THRESHOLD,
    AI_MAX_CONTEXT_MESSAGES,
    SENDER_USER,
    SENDER_AI,
    AI_RESPONSE_TIMEOUT
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AIService:
    """AI-powered customer support assistant using Ollama"""

    def __init__(self):
        """Initialize AI service with Ollama client"""
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.model = os.getenv('AI_MODEL', 'llama3.2:latest')
        self.use_ollama = os.getenv('USE_OLLAMA', 'true').lower() == 'true'

        # For future Anthropic support
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')

        if self.use_ollama:
            logger.info(f"AI Service initialized with Ollama | URL: {self.ollama_url} | Model: {self.model}")
        else:
            if not self.anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            logger.info(f"AI Service initialized with Anthropic | Model: {self.model}")

    def _build_system_prompt(self) -> str:
        """Build system prompt for AI assistant"""
        return """Ты — AI-ассистент службы поддержки Sulpak (крупнейшая сеть электроники и бытовой техники в Казахстане).

ТВОЯ РОЛЬ:
- Помогай клиентам с вопросами о заказах, доставке, оплате, возврате товаров
- Отвечай дружелюбно, профессионально и по существу на русском языке
- Используй эмодзи умеренно для теплоты общения
- Если не уверен в ответе или вопрос сложный — честно признай это

ПОЛИТИКИ SULPAK:
- Доставка: По Алматы 1-2 дня, по Казахстану 3-7 дней
- Возврат: 14 дней с момента покупки, товар должен быть в оригинальной упаковке
- Гарантия: Согласно производителю (обычно 12-24 месяца)
- Оплата: Наличные, карта, Kaspi Red, рассрочка

КОГДА НУЖЕН МЕНЕДЖЕР:
- Клиент очень недоволен/расстроен/агрессивен (негативная тональность)
- Вопрос требует доступа к внутренним системам (проверка статуса конкретного заказа по номеру)
- Запрос на возврат денег или компенсацию
- Клиент требует компенсацию за моральный ущерб или испорченные продукты
- Технически сложный вопрос о продукте
- Клиент явно просит живого менеджера

КРИТИЧЕСКИ ВАЖНО - ПРАВИЛА ЭСКАЛАЦИИ:

🚫 ЗАПРЕЩЕНО:
- НЕ давай клиенту email или номер телефона для самостоятельного обращения
- НЕ говори "напишите на почту support@..."
- НЕ говори "позвоните по номеру..."
- НЕ говори "я уже отправил ваш запрос"
- НЕ делай вид что уже что-то сделал

✅ ПРАВИЛЬНЫЙ СПОСОБ:
1. Если ситуация требует менеджера, спроси:
   "Хотите, чтобы я передал ваш вопрос нашему специалисту? Менеджер получит уведомление и свяжется с вами."

2. Дождись ответа клиента (Да/Нет)

3. Если клиент согласен (Да), скажи:
   "Передаю ваш запрос специалисту. Менеджер получит уведомление и свяжется с вами в ближайшее время."

4. Если клиент отказался (Нет), продолжай помогать сам

ПРИМЕР ПРАВИЛЬНОГО ДИАЛОГА:
Клиент: "Холодильник сломался! Требую возврат денег!"
Ты: "Понимаю ваше разочарование. Это серьезная ситуация, которая требует детального рассмотрения. Хотите, чтобы я передал ваш вопрос нашему специалисту? Менеджер получит уведомление и свяжется с вами."
Клиент: "Да"
Ты: "Передаю ваш запрос специалисту. Менеджер получит уведомление и свяжется с вами в ближайшее время."

СТИЛЬ ОБЩЕНИЯ:
- Краткие ответы (2-4 предложения)
- Конкретные решения, не общие фразы
- Если нужна информация от клиента — задай уточняющий вопрос
- Закрывай обращение предложением "Есть ещё вопросы?" когда проблема решена

Помни: твоя цель — помочь клиенту быстро и эффективно! 🚀"""

    def _build_conversation_context(self, messages: List[Dict], for_ollama: bool = True) -> List[Dict]:
        """
        Build conversation context for AI API

        Args:
            messages: List of message dicts with 'sender_type' and 'content'
            for_ollama: If True, format for Ollama, else for Anthropic

        Returns:
            List of messages in API format
        """
        # Limit context to recent messages
        recent_messages = messages[-AI_MAX_CONTEXT_MESSAGES:]

        formatted_messages = []
        for msg in recent_messages:
            role = "user" if msg['sender_type'] == SENDER_USER else "assistant"
            content = msg['content']

            # Add media context if present
            if msg.get('media_type'):
                media_type = msg['media_type']
                content = f"[{media_type.upper()}] {content if content else 'Фото/видео от пользователя'}"

            formatted_messages.append({
                "role": role,
                "content": content
            })

        return formatted_messages

    def _calculate_confidence(self, response: str) -> float:
        """
        Calculate AI confidence score based on response content

        Args:
            response: AI-generated response text

        Returns:
            Confidence score between 0 and 1
        """
        # Simple heuristic-based confidence scoring
        confidence = 1.0

        # Lower confidence indicators
        uncertainty_phrases = [
            'не уверен',
            'не знаю',
            'возможно',
            'может быть',
            'скорее всего',
            'попробуйте',
            'свяжитесь с',
            'обратитесь к менеджеру'
        ]

        response_lower = response.lower()
        for phrase in uncertainty_phrases:
            if phrase in response_lower:
                confidence -= 0.15

        # Very short responses might indicate uncertainty
        if len(response) < 50:
            confidence -= 0.1

        # Question-heavy responses indicate need for more info
        question_count = response.count('?')
        if question_count > 2:
            confidence -= 0.1

        return max(0.1, min(1.0, confidence))

    def _should_escalate(self, response: str, confidence: float) -> bool:
        """
        Determine if conversation should be escalated to human manager

        Args:
            response: AI-generated response
            confidence: AI confidence score

        Returns:
            True if escalation needed
        """
        # Only escalate when user CONFIRMS they want a manager
        # and AI says it's transferring to specialist

        # Explicit escalation confirmations (AI says this AFTER user confirms)
        escalation_triggers = [
            'передаю ваш запрос специалисту',
            'передам ваш запрос специалисту',
            'передаю специалисту',
            'передам специалисту',
            'передано специалисту',
            'передаю менеджеру',
            'передам менеджеру',
            'передано менеджеру',
            'специалист получил',
            'менеджер получил'
        ]

        response_lower = response.lower()
        for trigger in escalation_triggers:
            if trigger in response_lower:
                logger.info(f"Escalating due to user confirmation: {trigger}")
                return True

        return False

    async def _call_ollama(
        self,
        system_prompt: str,
        messages: List[Dict]
    ) -> str:
        """
        Call Ollama API

        Args:
            system_prompt: System prompt
            messages: Conversation messages

        Returns:
            AI response text
        """
        # Build full conversation with system prompt
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        async with httpx.AsyncClient(timeout=AI_RESPONSE_TIMEOUT) as client:
            response = await client.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": full_messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1024
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data['message']['content']

    async def _call_anthropic(
        self,
        system_prompt: str,
        messages: List[Dict]
    ) -> str:
        """
        Call Anthropic API (for future use)

        Args:
            system_prompt: System prompt
            messages: Conversation messages

        Returns:
            AI response text
        """
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=self.anthropic_key)

        response = await client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
            temperature=0.7
        )

        return response.content[0].text

    async def get_ai_response(
        self,
        ticket_id: int,
        conversation_history: List[Dict],
        user_info: Dict
    ) -> Tuple[str, float, bool]:
        """
        Generate AI response for user message

        Args:
            ticket_id: Ticket ID for logging
            conversation_history: Full conversation history
            user_info: User information (username, user_id)

        Returns:
            Tuple of (response_text, confidence_score, should_escalate)
        """
        try:
            logger.info(f"Generating AI response for ticket #{ticket_id} | History: {len(conversation_history)} messages")

            # Debug: log conversation
            for i, msg in enumerate(conversation_history):
                logger.debug(f"  Msg {i+1}: {msg['sender_type']} - {msg['content'][:50]}...")

            # Build context
            system_prompt = self._build_system_prompt()
            messages = self._build_conversation_context(conversation_history)

            # Call appropriate AI service
            if self.use_ollama:
                response_text = await self._call_ollama(system_prompt, messages)
            else:
                response_text = await self._call_anthropic(system_prompt, messages)

            # Calculate confidence and escalation
            confidence = self._calculate_confidence(response_text)
            should_escalate = self._should_escalate(response_text, confidence)

            logger.info(
                f"AI response generated for ticket #{ticket_id} | "
                f"Confidence: {confidence:.2f} | "
                f"Escalate: {should_escalate}"
            )

            return response_text, confidence, should_escalate

        except Exception as e:
            logger.error(f"Error generating AI response for ticket #{ticket_id}: {e}", exc_info=True)
            # Fallback response on error
            fallback_response = (
                "Извините, возникла техническая проблема. "
                "Я передам ваш вопрос менеджеру, который свяжется с вами в ближайшее время. 🙏"
            )
            return fallback_response, 0.0, True  # Always escalate on error

    async def generate_conversation_summary(
        self,
        conversation_history: List[Dict]
    ) -> str:
        """
        Generate concise summary of conversation for email notification

        Args:
            conversation_history: Full conversation history

        Returns:
            Summary text in Russian
        """
        try:
            # Build conversation text
            conversation_text = "\n\n".join([
                f"{'Клиент' if msg['sender_type'] == SENDER_USER else 'AI'}: {msg['content']}"
                for msg in conversation_history
            ])

            # Create summarization prompt
            summary_prompt = f"""Создай краткое резюме (2-3 предложения) этой беседы службы поддержки на русском языке:

{conversation_text}

Укажи:
1. Суть проблемы/вопроса клиента
2. Что было предложено AI
3. Почему требуется эскалация

Формат: только текст резюме, без заголовков."""

            messages = [{"role": "user", "content": summary_prompt}]

            # Call appropriate AI service
            if self.use_ollama:
                async with httpx.AsyncClient(timeout=AI_RESPONSE_TIMEOUT) as client:
                    response = await client.post(
                        f"{self.ollama_url}/api/chat",
                        json={
                            "model": self.model,
                            "messages": messages,
                            "stream": False,
                            "options": {
                                "temperature": 0.5,
                                "num_predict": 512
                            }
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    summary = data['message']['content'].strip()
            else:
                from anthropic import AsyncAnthropic
                client = AsyncAnthropic(api_key=self.anthropic_key)
                response = await client.messages.create(
                    model=self.model,
                    max_tokens=512,
                    messages=messages,
                    temperature=0.5
                )
                summary = response.content[0].text.strip()

            logger.info(f"Generated conversation summary: {summary[:100]}...")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            return "Не удалось сгенерировать резюме беседы."


# Global AI service instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
