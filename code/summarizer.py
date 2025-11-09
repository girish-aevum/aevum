from transformers import pipeline

# Load smaller summarizer model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

text = """
Hugging Face Transformers library provides thousands of pre-trained models
for tasks such as classification, information extraction, question answering,
summarization, translation, and text generation.
These models help developers quickly build state-of-the-art NLP applications.
"""

summary = summarizer(text, max_length=80, min_length=20, do_sample=False)
print("Summary:", summary[0]['summary_text'])

