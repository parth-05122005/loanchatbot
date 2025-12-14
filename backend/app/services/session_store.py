class SessionStore:
    def __init__(self):
        self.sessions = {}

    def get(self, session_id: str):
        return self.sessions.get(session_id, {})

    def save(self, session_id: str, state: dict):
        self.sessions[session_id] = state
