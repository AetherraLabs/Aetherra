# Multi-AI Fallback System Setup Guide

Lyrixa now supports multiple AI models with intelligent fallback when one fails! This guide shows you how to configure API keys for different AI providers.

## 🎯 How It Works

When you chat with Lyrixa, she tries AI models in this priority order:

1. **OpenAI GPT-4o-mini** (Primary - fastest and most efficient)
2. **OpenAI GPT-3.5-turbo** (Backup for OpenAI)
3. **Anthropic Claude** (Alternative provider)
4. **Google Gemini** (Google's AI)
5. **Cohere Command** (Enterprise-focused AI)
6. **Hugging Face** (Open-source models)
7. **Local Fallback** (Intelligent personality-driven responses)

## 🔑 API Key Configuration

### 1. OpenAI (Recommended)
**Free Tier:** $5 credit for new users
**Pricing:** ~$0.001 per 1K tokens

1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Create account and get API key
3. Add to `.env` file:
```
OPENAI_API_KEY=sk-proj-your-key-here
```

### 2. Anthropic Claude
**Free Tier:** Limited free credits
**Pricing:** ~$0.003 per 1K tokens

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create account and get API key
3. Add to `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Install library:
```bash
pip install anthropic
```

### 3. Google Gemini
**Free Tier:** Generous free tier
**Pricing:** Free up to 1 million tokens/month

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create API key
3. Add to `.env` file:
```
GOOGLE_API_KEY=your-google-api-key-here
```

Install library:
```bash
pip install google-generativeai
```

### 4. Cohere
**Free Tier:** Limited free usage
**Pricing:** Usage-based

1. Go to [Cohere Dashboard](https://dashboard.cohere.ai/api-keys)
2. Create account and get API key
3. Add to `.env` file:
```
COHERE_API_KEY=your-cohere-key-here
```

Install library:
```bash
pip install cohere
```

### 5. Hugging Face
**Free Tier:** Free inference API
**Pricing:** Free for most models

1. Go to [Hugging Face Tokens](https://huggingface.co/settings/tokens)
2. Create account and get token
3. Add to `.env` file:
```
HUGGINGFACE_API_KEY=hf_your-token-here
```

No additional library needed (uses requests)

## 📄 Complete .env File Example

Create or update your `.env` file in the project root:

```env
# Primary AI Provider
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Backup AI Providers
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-api-key-here
COHERE_API_KEY=your-cohere-key-here
HUGGINGFACE_API_KEY=hf_your-huggingface-token-here

# Optional: Other configurations
# LYRIXA_DEBUG=true
# LYRIXA_LOG_LEVEL=DEBUG
```

## 🚀 Quick Start (Minimum Setup)

For the best experience with minimal cost:

1. **OpenAI** (Primary): $5 free credit, excellent quality
2. **Google Gemini** (Backup): 1 million free tokens/month
3. **Hugging Face** (Final backup): Completely free

This gives you excellent coverage with minimal/no cost!

## 💡 Features

### Smart Error Detection
- Detects quota/billing issues specifically
- Automatically tries next provider
- Logs which provider succeeded

### Personality Integration
- All AI responses maintain Lyrixa's personality
- Emotional state affects response creativity
- Consistent character across all providers

### Intelligent Local Fallback
- Context-aware responses when all APIs fail
- Personality-driven conversation
- Emotional state integration
- Pattern recognition for common queries

## 🔧 Testing Your Setup

1. Add at least one API key to `.env`
2. Restart Lyrixa
3. Open chat interface
4. Send a message
5. Check logs to see which AI model responded

Look for logs like:
```
[PHASE6] Successfully generated response using OpenAI GPT-4o-mini
```

## 🛠️ Troubleshooting

### "All AI models failed"
- Check your `.env` file exists in project root
- Verify API keys are correct
- Check internet connection
- Try with just one provider first

### Rate Limiting
- The system automatically tries next provider
- Consider upgrading API plans for higher limits
- Spread usage across multiple providers

### Quality Issues
- Primary providers (OpenAI, Anthropic) have best quality
- Adjust model priority in code if needed
- Local fallback is always available

## 🎮 Advanced Configuration

You can modify the AI model priority in `phase6_personality.py` by changing the `priority` values in the `ai_models` list.

## 📊 Cost Optimization

1. **Free Setup**: Google Gemini + Hugging Face
2. **Low Cost**: OpenAI GPT-4o-mini (~$1/month for casual use)
3. **High Quality**: OpenAI + Anthropic
4. **Enterprise**: All providers for maximum reliability

The system automatically uses the most cost-effective available option while maintaining quality!

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
