# AI Response Summarization Feature

## Overview

The AI Companion now includes automatic response summarization to provide users with more concise, focused responses while preserving all essential information and actionable advice.

## How It Works

1. **Original Response Generation**: The AI generates a full response to the user's query
2. **Intelligent Summarization**: If enabled, the response is automatically summarized using a secondary AI call
3. **Quality Preservation**: The summarization process preserves:
   - All essential information and advice
   - Supportive and encouraging tone
   - Important warnings or disclaimers
   - Actionable recommendations

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Enable/disable response summarization (default: True)
AI_COMPANION_ENABLE_SUMMARIZATION=true

# Maximum words for summarized responses (default: 150)
AI_COMPANION_MAX_SUMMARY_WORDS=150
```

### Django Settings

The following settings are automatically configured in `settings.py`:

```python
# AI Companion Settings
AI_COMPANION_ENABLE_SUMMARIZATION = env.bool('AI_COMPANION_ENABLE_SUMMARIZATION', default=True)
AI_COMPANION_MAX_SUMMARY_WORDS = env.int('AI_COMPANION_MAX_SUMMARY_WORDS', default=150)
```

## Database Tracking

The system tracks summarization metadata in the `Message` model:

- `original_word_count`: Word count before summarization
- `was_summarized`: Boolean indicating if response was summarized
- `token_count`: Updated to reflect final response length

## Testing

### Manual Testing

Test the summarization feature using the management command:

```bash
# Basic test
python manage.py test_summarization

# Custom test message
python manage.py test_summarization --message "Tell me about nutrition and healthy eating"

# Custom word limit
python manage.py test_summarization --max-words 100
```

### API Testing

Use the regular chat API - summarization happens automatically:

```bash
curl -X POST http://localhost:8080/api/ai-companion/chat/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "your-thread-id",
    "message": "How can I improve my sleep quality?"
  }'
```

## Benefits

1. **Improved User Experience**: Shorter, more digestible responses
2. **Faster Reading**: Users can quickly understand key points
3. **Preserved Quality**: Important information is retained
4. **Configurable**: Can be disabled or adjusted per deployment
5. **Tracked**: Full analytics on summarization effectiveness

## Fallback Behavior

If summarization fails:
- Falls back to intelligent truncation at sentence boundaries
- Preserves original response if truncation isn't beneficial
- Logs errors for monitoring
- Never crashes the chat functionality

## Performance Considerations

- Summarization adds ~1-2 seconds to response time
- Uses additional API tokens (typically 20-30% more)
- Can be disabled for faster responses if needed
- Caches are not implemented yet (future enhancement)

## Monitoring

Check logs for summarization metrics:
- Word count reductions
- Summarization success/failure rates
- Performance impact

Example log output:
```
INFO Response summarized: 247 -> 134 words
```

## Future Enhancements

- Response caching to avoid re-summarizing similar content
- User preference for summary length
- A/B testing framework for summarization effectiveness
- Advanced summarization techniques (extractive + abstractive) 