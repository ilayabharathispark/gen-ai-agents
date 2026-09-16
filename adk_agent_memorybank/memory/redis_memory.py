"""
Redis Short-Term Memory Manager
--------------------------------
Stores the recent conversation history for the current session in Redis.
Think of it like a notepad that the agent reads before each reply.
"""

import json
import os

import redis
from dotenv import load_dotenv

load_dotenv()


class RedisMemoryManager:

    def __init__(self):
        # Step 1: Connect to Redis Cloud using the URL from your .env file
        # The URL format is: redis://default:<password>@<host>:<port>
        self.client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

        # Step 2: Set how long (in seconds) to keep a session alive
        # 7200 seconds = 2 hours. If the user is idle for 2 hours, Redis
        # automatically deletes the session history.
        self.ttl = int(os.getenv("REDIS_SESSION_TTL", "7200"))

        # Step 3: How many recent turns to show the agent
        # We only need the last 10 messages — no need to feed the entire history
        self.context_window = int(os.getenv("REDIS_CONTEXT_WINDOW", "10"))

    def add_turn(self, session_id: str, role: str, content: str = "", text: str = None):
        """
        Save one message turn to Redis.

        session_id : unique ID of the current conversation
        role       : "user" or "agent"
        content    : the actual message text (can also be passed as 'text')
        """
        message_text = text if text is not None else content

        # The Redis key looks like: session:abc123:history
        key = f"session:{session_id}:history"

        # Convert the turn dict to a JSON string so Redis can store it
        turn = json.dumps({"role": role, "content": message_text})


        # rpush → append to the end of the list
        # expire → reset the 2-hour TTL countdown on every new message
        self.client.rpush(key, turn)
        self.client.expire(key, self.ttl)

    def get_history(self, session_id: str) -> list[dict]:
        """
        Retrieve the last N turns from Redis for this session.
        Returns a list of dicts like: [{"role": "user", "content": "..."}]
        Returns an empty list if there is no history (new session).
        """
        key = f"session:{session_id}:history"

        # lrange(key, -10, -1) means: get the last 10 items from the list
        raw_turns = self.client.lrange(key, -self.context_window, -1)

        return [json.loads(turn) for turn in raw_turns]

    def build_context_string(self, session_id: str) -> str:
        """
        Format the conversation history as a readable text block.
        This text is injected into the agent's instruction so it
        'remembers' what was said earlier in the session.

        Returns an empty string if no history exists yet.
        """
        turns = self.get_history(session_id)

        if not turns:
            return ""  # New session — nothing to inject

        lines = ["### Recent Conversation (short-term memory)"]
        for turn in turns:
            label = "User" if turn["role"] == "user" else "Assistant"
            lines.append(f"{label}: {turn['content']}")
        lines.append("---")

        return "\n".join(lines)
