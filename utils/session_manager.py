import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class SessionManager:
    """Manages user sessions and maintains RFP history"""
    
    def __init__(self):
        self.sessions_dir = 'sessions'
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.max_sessions = 5  # Maximum sessions per user
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user"""
        session_file = os.path.join(self.sessions_dir, f'{user_id}.json')
        
        if not os.path.exists(session_file):
            return []
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sessions', [])
        except Exception:
            return []
    
    def get_current_session(self, user_id: str) -> Optional[Dict]:
        """Get the most recent session for a user"""
        sessions = self.get_user_sessions(user_id)
        return sessions[0] if sessions else None
    
    def update_rfp_data(self, user_id: str, filename: str, requirements: str, content: str) -> Dict:
        """Update session with RFP data"""
        sessions = self.get_user_sessions(user_id)
        
        # Check if file already exists and update it
        existing_session = None
        for session in sessions:
            if session.get('rfp_filename') == filename:
                existing_session = session
                break
        
        if existing_session:
            existing_session.update({
                'rfp_requirements': requirements,
                'rfp_content': content,
                'updated_at': datetime.now().isoformat()
            })
            session_data = existing_session
        else:
            # Create new session
            session_data = {
                'id': len(sessions) + 1,
                'rfp_filename': filename,
                'rfp_requirements': requirements,
                'rfp_content': content,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Add to beginning of list
            sessions.insert(0, session_data)
            
            # Limit to max sessions
            if len(sessions) > self.max_sessions:
                sessions = sessions[:self.max_sessions]
        
        self._save_user_sessions(user_id, sessions)
        return session_data
    
    def update_org_data(self, user_id: str, filename: str, analysis: str, 
                       matching_table: List[Dict], response_prompt: str) -> Dict:
        """Update current session with organization data"""
        sessions = self.get_user_sessions(user_id)
        
        if not sessions:
            raise Exception("No RFP session found. Please upload RFP first.")
        
        current_session = sessions[0]
        current_session.update({
            'org_filename': filename,
            'org_analysis': analysis,
            'matching_table': matching_table,
            'response_prompt': response_prompt,
            'updated_at': datetime.now().isoformat()
        })
        
        self._save_user_sessions(user_id, sessions)
        return current_session
    
    def update_output_file(self, user_id: str, output_filename: str) -> Dict:
        """Update current session with output file info"""
        sessions = self.get_user_sessions(user_id)
        
        if not sessions:
            raise Exception("No active session found.")
        
        current_session = sessions[0]
        current_session.update({
            'output_filename': output_filename,
            'completed_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })
        
        self._save_user_sessions(user_id, sessions)
        return current_session
    
    def _save_user_sessions(self, user_id: str, sessions: List[Dict]):
        """Save sessions to file"""
        session_file = os.path.join(self.sessions_dir, f'{user_id}.json')
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump({'sessions': sessions}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Error saving sessions: {str(e)}")
    
    def get_session_summary(self, session: Dict) -> str:
        """Generate a summary for display in sidebar"""
        rfp_name = session.get('rfp_filename', 'Unknown RFP')
        created_date = session.get('created_at', '')
        
        if created_date:
            try:
                date_obj = datetime.fromisoformat(created_date)
                date_str = date_obj.strftime('%m/%d %H:%M')
            except:
                date_str = 'Unknown date'
        else:
            date_str = 'Unknown date'
        
        status = 'Complete' if session.get('output_filename') else 'In Progress'
        
        return f"{rfp_name} - {date_str} ({status})"
