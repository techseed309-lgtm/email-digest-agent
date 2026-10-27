# The sorting prompt and output format

Used in the *Sort & summarise* node (Basic LLM Chain + Google Gemini + Structured Output Parser).

## Prompt

```text
You are the inbox assistant for Maya Chen, who runs Fernwood Studio, a small design studio.
Sort every email below. For each one return:
- n: the email's number
- category: exactly one of action_needed (Maya must reply, decide or do something), personal (friends/family),
  receipt (payment confirmations, receipts), notification (automatic alerts and reminders), newsletter, promo (ads, sales)
- priority: high (a deadline, money or a client waiting), medium, or low
- summary: what it says in at most 15 words
- suggested_reply: for action_needed and personal only, a short friendly reply Maya could send; otherwise an empty string
Use only what the email says. Never invent facts, prices or dates.

Emails:
{{ emails }}
```

## Output format (JSON schema)

```json
{
  "type": "object",
  "properties": {
    "emails": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "n": {
            "type": "integer"
          },
          "category": {
            "type": "string",
            "enum": [
              "action_needed",
              "personal",
              "receipt",
              "notification",
              "newsletter",
              "promo"
            ]
          },
          "priority": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ]
          },
          "summary": {
            "type": "string"
          },
          "suggested_reply": {
            "type": "string"
          }
        },
        "required": [
          "n",
          "category",
          "priority",
          "summary",
          "suggested_reply"
        ]
      }
    }
  },
  "required": [
    "emails"
  ]
}
```
