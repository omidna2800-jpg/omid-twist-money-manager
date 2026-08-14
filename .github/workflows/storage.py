import json
import os
from datetime import datetime

class Storage:
    def __init__(self):
        self.storage_dir = self._get_storage_dir()
        self.state_file = os.path.join(self.storage_dir, 'state.json')
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _get_storage_dir(self):
        try:
            from android.storage import app_storage_path
            return app_storage_path()
        except ImportError:
            return os.path.dirname(os.path.abspath(__file__))
    
    def save_state(self, state_dict):
        try:
            state_dict['saved_at'] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"خطا در ذخیره‌سازی: {e}")
            return False
    
    def load_state(self):
        try:
            if not os.path.exists(self.state_file):
                return None
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"خطا در بازیابی: {e}")
            return None
    
    def clear_state(self):
        try:
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
            return True
        except Exception as e:
            print(f"خطا در پاک کردن: {e}")
            return False
