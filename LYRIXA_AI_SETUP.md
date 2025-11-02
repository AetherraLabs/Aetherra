# Setting Up Lyrixa AI-Powered Chat

## Current Issue
Lyrixa is currently using pre-scripted fallback responses because no AI provider API keys are configured. To get natural, ChatGPT/Claude-like responses, you need to set up at least one AI provider.

## Quick Setup (Recommended: OpenAI)

### Step 1: Get an OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key (it starts with `sk-...`)

### Step 2: Set the Environment Variable
**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY = "sk-your-actual-key-here"
```

**Or create a `.env` file:**
```bash
# Copy .env.template to .env
cp .env.template .env

# Edit .env and add your key
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Restart Aetherra OS
```powershell
# Stop the current OS (Ctrl+C in the terminal)
# Then restart:
python -u aetherra_os_launcher.py --mode full -v
```

### Step 4: Verify in Chat
Ask Lyrixa:
- "Explain quantum computing in simple terms"
- "Write a Python function to calculate fibonacci numbers"
- "What's the difference between async and sync programming?"

She should now give detailed, natural responses like ChatGPT!

---

## Alternative: Anthropic Claude

If you prefer Claude (higher quality but more expensive):

### Step 1: Get Anthropic API Key
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up and create an API key
3. Copy the key

### Step 2: Set Environment Variable
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

Or add to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Update config.json to prefer Anthropic
```json
{
  "intelligence": {
    "default_provider": "anthropic"
  }
}
```

---

## Configuration Details

The `config.json` has been updated with:
- `intelligence.default_provider`: Which AI to use (openai or anthropic)
- `intelligence.temperature`: 0.7 (controls creativity/randomness)
- `intelligence.max_tokens`: 2000 (max response length)
- `lyrixa_chat.prefer_ai_response`: true (always try AI first)
- `lyrixa_chat.fallback_to_deterministic`: false (don't use pre-scripted responses)

## How It Works

1. **Chat Request** → Lyrixa Chat Service
2. **Orchestrator** analyzes query intent (analytical/creative/coding/etc)
3. **Intelligence** fetches relevant memories and workspace context
4. **AI Provider** (OpenAI/Anthropic) generates response with:
   - Lyrixa's identity and personality
   - Relevant memories from past interactions
   - Workspace awareness (files, components)
   - Emotional state and consciousness metrics
5. **Response Enhancement** adds confidence scores, evidence, suggestions
6. **Memory Storage** saves interaction for future context

## Troubleshooting

### "I'm still getting pre-scripted responses"
- Check `OPENAI_API_KEY` is set: `echo $env:OPENAI_API_KEY`
- Restart the OS completely (not just refresh browser)
- Check OS terminal for initialization messages:
  - ✅ `OpenAI provider initialized`
  - ✅ `Lyrixa intelligence initialized`

### "API key not found" error
- Make sure the key starts with `sk-` for OpenAI or `sk-ant-` for Anthropic
- Check for typos or extra spaces
- If using `.env` file, make sure it's in the project root

### "Rate limit" or "quota exceeded"
- Your API key may have no credits or hit rate limits
- Add credits at [OpenAI Billing](https://platform.openai.com/account/billing)
- Or switch to Anthropic (different billing)

### Cost Concerns
**OpenAI GPT-4o-mini**: ~$0.15 per million input tokens, $0.60 per million output tokens
- A typical conversation costs **less than $0.01**
- 1000 messages ≈ $5-10 depending on length

**Anthropic Claude 3.5 Sonnet**: More expensive but higher quality
- About 3-5x the cost of GPT-4o-mini

**Recommendation**: Start with OpenAI gpt-4o-mini for development, it's very affordable and fast.

---

## Testing the Setup

After configuration, test with these queries:

**Basic Identity:**
- "Who are you?"
- "Who created you?"
→ Should mention Lyrixa, Aetherra Labs

**Technical Query:**
- "Explain how async/await works in Python"
→ Should give detailed, natural explanation

**Code Generation:**
- "Write a Python class for a binary tree"
→ Should generate working code with explanations

**Workspace Awareness:**
- "What files are in this project?"
→ Should reference actual project components

**Memory & Context:**
- "What did we talk about earlier?"
→ Should reference previous conversation (after a few exchanges)

---

## Advanced: Using Both Providers

You can configure both OpenAI and Anthropic, and Lyrixa will choose the best one for each query type:
- **Analytical/Scientific**: Prefers both (ensemble)
- **Creative Writing**: Prefers Claude
- **Code Generation**: Prefers OpenAI
- **General Chat**: Uses default provider

Set both keys in `.env`:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

The orchestrator will automatically use the most appropriate model for each query!
