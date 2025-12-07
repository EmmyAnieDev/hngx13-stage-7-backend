import httpx
import json
import logging
from typing import Dict, Any
from app.database import settings

logger = logging.getLogger(__name__)


class LLMService:
    @staticmethod
    async def analyze_document(text: str) -> Dict[str, Any]:
        """Send document text to LLM for analysis."""

        prompt = f"""You are a document analysis assistant. Analyze the following document and extract information.

IMPORTANT: You MUST respond with ONLY a JSON object in EXACTLY this structure (no other text):

{{
  "summary": "A 2-3 sentence summary of the document",
  "document_type": "one of: invoice, cv, resume, report, letter, contract, prd, readme, guide, or other",
  "metadata": {{
    "key1": "value1",
    "key2": "value2"
  }}
}}

Guidelines for metadata extraction by document type:
- Invoice: date, invoice_number, total_amount, vendor, client
- CV/Resume: name, email, phone, skills (as comma-separated string), experience_years
- Report: title, date, author, department, summary
- Letter: date, sender, recipient, subject
- Contract: parties, date, contract_type, value
- PRD: product_name, version, author, date
- Guide/README: title, topic, version

Document text:
{text[:4000]}

Remember: Respond with ONLY the JSON object, no markdown, no explanations, no extra text."""

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    settings.openrouter_uri,
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
                logger.debug(f"LLM API response: {json.dumps(result, indent=2)}")
                
                if "choices" not in result or len(result["choices"]) == 0:
                    logger.error(f"No choices in LLM response: {result}")
                    raise ValueError("Received invalid response from analysis service")
                
                message = result["choices"][0].get("message", {})
                content = message.get("content", "")
                
                if not content:
                    logger.error(f"Empty content in LLM response: {result}")
                    raise ValueError("Received empty response from analysis service")
                
                logger.debug(f"Raw LLM content: {content}")

                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start != -1 and json_end != -1:
                    content = content[json_start:json_end + 1]

                logger.debug(f"Cleaned content: {content}")

                try:
                    analysis = json.loads(content)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {str(e)}. Attempting fallback...")
                    analysis = {}

                if not isinstance(analysis, dict):
                    logger.error(f"LLM returned non-dict: {type(analysis)}")
                    analysis = {}

                if not all(key in analysis for key in ["summary", "document_type", "metadata"]):
                    logger.warning(f"LLM response missing required fields. Got keys: {analysis.keys()}")

                    if "summary" not in analysis and "document_type" not in analysis:
                        logger.error("Response appears to be raw metadata instead of full analysis structure")
                        raise ValueError("LLM did not follow the required response format")

                return {
                    "summary": analysis.get("summary", "No summary available"),
                    "document_type": analysis.get("document_type", "unknown"),
                    "metadata": analysis.get("metadata", {})
                }

            except httpx.HTTPError as e:
                logger.error(f"LLM API request failed: {str(e)}")
                raise ValueError("Failed to connect to analysis service")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response. Content was: '{content}'. Error: {str(e)}")
                raise ValueError("Failed to process analysis results")
            except KeyError as e:
                logger.error(f"Unexpected LLM response format: {str(e)}, Response: {result}")
                raise ValueError("Received invalid response from analysis service")
            except Exception as e:
                logger.error(f"Unexpected error in LLM analysis: {str(e)}", exc_info=True)
                raise ValueError("Document analysis failed")