from decimal import Decimal
from capital_table import CapitalTable
from datetime import datetime

class TradeStateMachine:
    def __init__(self):
        self.capital_table = CapitalTable()
        self.reset()
        self.rest_time_seconds = 30
        self.max_consecutive_losses = 3
    
    def reset(self):
        self.main_trade_index = 1
        self.loss_depth = 0
        self.consecutive_losses = 0
        self.history = []
        self.is_resting = False
        self.rest_end_time = None
        self.cycle_complete = False
    
    def get_current_amount(self):
        if self.cycle_complete:
            return Decimal('0')
        return self.capital_table.get_amount(self.main_trade_index, self.loss_depth)
    
    def get_current_state(self):
        return {
            'main_trade_index': self.main_trade_index,
            'loss_depth': self.loss_depth,
            'consecutive_losses': self.consecutive_losses,
            'amount': str(self.get_current_amount()),
            'special_name': self.capital_table.get_special_name(self.main_trade_index),
            'is_resting': self.is_resting,
            'cycle_complete': self.cycle_complete,
            'history': self.history[-10:]
        }
    
    def record_result(self, result):
        if self.is_resting:
            return False
        if self.cycle_complete:
            return False
        
        current_amount = self.get_current_amount()
        
        history_entry = {
            'trade_number': self.main_trade_index,
            'loss_depth': self.loss_depth,
            'amount': str(current_amount),
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        self.history.append(history_entry)
        
        if result == 'win':
            self._handle_win()
        elif result == 'loss':
            self._handle_loss()
        
        return True
    
    def _handle_win(self):
        self.consecutive_losses = 0
        
        if self.loss_depth == 0:
            if self.main_trade_index < 21:
                self.main_trade_index += 1
            else:
                self.cycle_complete = True
        else:
            if self.loss_depth > 1:
                self.loss_depth -= 1
            elif self.loss_depth == 1:
                if self.main_trade_index > 1:
                    self.main_trade_index -= 1
                    self.loss_depth = 0
                else:
                    self.reset()
                    return
                self._start_rest("کوتاه")
    
    def _handle_loss(self):
        self.consecutive_losses += 1
        
        if self.loss_depth < 4:
            self.loss_depth += 1
        else:
            self._start_rest("کامل")
            return
        
        if self.consecutive_losses >= self.max_consecutive_losses:
            self._start_rest("کامل")
    
    def _start_rest(self, rest_type="کامل"):
        self.is_resting = True
        self.rest_end_time = datetime.now().timestamp() + self.rest_time_seconds
        self.rest_type = rest_type
    
    def check_rest(self):
        if self.is_resting and self.rest_end_time:
            current_time = datetime.now().timestamp()
            if current_time >= self.rest_end_time:
                self.is_resting = False
                self.rest_end_time = None
                self.rest_type = None
                return False
        return self.is_resting
    
    def get_rest_remaining(self):
        if not self.is_resting or not self.rest_end_time:
            return 0
        remaining = self.rest_end_time - datetime.now().timestamp()
        return max(0, int(remaining))
    
    def to_dict(self):
        return {
            'main_trade_index': self.main_trade_index,
            'loss_depth': self.loss_depth,
            'consecutive_losses': self.consecutive_losses,
            'history': self.history,
            'is_resting': self.is_resting,
            'rest_end_time': self.rest_end_time,
            'rest_type': self.rest_type,
            'cycle_complete': self.cycle_complete
        }
    
    def from_dict(self, data):
        self.main_trade_index = data.get('main_trade_index', 1)
        self.loss_depth = data.get('loss_depth', 0)
        self.consecutive_losses = data.get('consecutive_losses', 0)
        self.history = data.get('history', [])
        self.is_resting = data.get('is_resting', False)
        self.rest_end_time = data.get('rest_end_time', None)
        self.rest_type = data.get('rest_type', None)
        self.cycle_complete = data.get('cycle_complete', False)
