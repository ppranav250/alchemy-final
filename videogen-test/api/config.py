# Centralized configuration for the application

import os

class Config:
    # AI Model Configuration
    # Using Claude 3.5 Sonnet for its balance of intelligence, speed, and cost-effectiveness.
    CLAUDE_MODEL = "claude-3-5-sonnet-20240620"
    MAX_TOKENS = 4096

    # API Keys - fetched from environment variables for security
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    LMNT_API_KEY = os.getenv("LMNT_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Voice Generation Configuration
    # Using 'lily' as a default voice. A list of available voices can be fetched from the LMNT API.
    LMNT_VOICE = 'lily'

    # File Paths
    MEDIA_DIR = 'media'
    AUDIO_DIR = os.path.join(MEDIA_DIR, 'audio')
