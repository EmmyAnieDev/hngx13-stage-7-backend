import httpx
import json
from typing import Dict, Any
from app.database import settings


class LLMService:
    @staticmethod
    async def analyze_document(text: str) -> Dict[str, Any]:
        """Send document text to LLM for analysis."""

        prompt = f"""Analyze this document and provide:
1. A concise summary (2-3 sentences)
2. Document type (invoice, CV, report, letter, contract, etc.)
3. Extracted metadata as JSON

For metadata, extract relevant fields based on document type:
- Invoice: date, invoice_number, total_amount, vendor, client
- CV/Resume: name, email, phone, skills, experience_years
- Report: title, date, author, department
- Letter: date, sender, recipient, subject
- Contract: parties, date, contract_type, value

Document text:
{text[:3000]}

Respond ONLY with valid JSON in this format:
{{
  "summary": "your summary here",
  "document_type": "type here",
  "metadata": {{
    "field1": "value1",
    "field2": "value2"
  }}
}}"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.openrouter_model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                )
                response.raise_for_status()

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON response
                # Clean markdown code blocks if present
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                analysis = json.loads(content)

                return {
                    "summary": analysis.get("summary", ""),
                    "document_type": analysis.get("document_type", "unknown"),
                    "metadata": analysis.get("metadata", {})
                }

            except httpx.HTTPError as e:
                raise ValueError(f"LLM API request failed: {str(e)}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse LLM response: {str(e)}")
            except Exception as e:
                raise ValueError(f"LLM analysis failed: {str(e)}")
