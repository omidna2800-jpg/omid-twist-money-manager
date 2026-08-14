from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock

from state_machine import TradeStateMachine
from storage import Storage
from decimal import Decimal

class TradeApp(App):
    def __init__(self):
        super().__init__()
        self.state_machine = TradeStateMachine()
        self.storage = Storage()
        self.load_saved_state()
    
    def build(self):
        Window.size = (400, 700)
        
        self.main_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=10
        )
        
        title_label = Label(
            text='مدیریت سرمایه پیچشی',
            font_size=24,
            bold=True,
            size_hint=(1, 0.15),
            color=(0.2, 0.4, 0.8, 1)
        )
        self.main_layout.add_widget(title_label)
        
        self.status_label = Label(
            text='',
            font_size=18,
            size_hint=(1, 0.3),
            halign='center',
            valign='middle'
        )
        self.main_layout.add_widget(self.status_label)
        
        self.amount_label = Label(
            text='',
            font_size=32,
            bold=True,
            size_hint=(1, 0.2),
            halign='center',
            color=(0.1, 0.6, 0.1, 1)
        )
        self.main_layout.add_widget(self.amount_label)
        
        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.15),
            spacing=20,
            padding=[40, 0]
        )
        
        self.win_button = Button(
            text='سود شد',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=20,
            bold=True
        )
        self.win_button.bind(on_press=self.on_win)
        
        self.loss_button = Button(
            text='ضرر شد',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=20,
            bold=True
        )
        self.loss_button.bind(on_press=self.on_loss)
        
        buttons_layout.add_widget(self.win_button)
        buttons_layout.add_widget(self.loss_button)
        self.main_layout.add_widget(buttons_layout)
        
        self.stage_label = Label(
            text='',
            font_size=14,
            size_hint=(1, 0.1),
            halign='center',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.main_layout.add_widget(self.stage_label)
        
        control_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=10
        )
        
        self.reset_button = Button(
            text='ریست',
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=14
        )
        self.reset_button.bind(on_press=self.on_reset)
        
        self.history_button = Button(
            text='تاریخچه',
            background_color=(0.4, 0.4, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=14
        )
        self.history_button.bind(on_press=self.show_history)
        
        control_layout.add_widget(self.reset_button)
        control_layout.add_widget(self.history_button)
        self.main_layout.add_widget(control_layout)
        
        self.update_display()
        Clock.schedule_interval(self.check_rest_timer, 1)
        
        return self.main_layout
    
    def load_saved_state(self):
        saved_state = self.storage.load_state()
        if saved_state:
            self.state_machine.from_dict(saved_state)
    
    def save_current_state(self):
        state_dict = self.state_machine.to_dict()
        self.storage.save_state(state_dict)
    
    def update_display(self):
        state = self.state_machine.get_current_state()
        
        if state['cycle_complete']:
            self.status_label.text = 'چرخه کامل شد!'
            self.amount_label.text = '🎉'
            self.stage_label.text = 'شروع چرخه جدید؟'
            self.win_button.disabled = True
            self.loss_button.disabled = True
            self.reset_button.text = 'شروع چرخه جدید'
            
        elif state['is_resting']:
            rest_type = self.state_machine.rest_type
            remaining = self.state_machine.get_rest_remaining()
            self.status_label.text = f'استراحت{(" " + rest_type) if rest_type else ""}'
            self.amount_label.text = f'⏳ {remaining} ثانیه'
            self.stage_label.text = 'لطفاً صبر کنید...'
            self.win_button.disabled = True
            self.loss_button.disabled = True
            
        else:
            if state['loss_depth'] == 0:
                status_text = f'ترید شماره {state["main_trade_index"]}'
                if state['special_name']:
                    status_text += f'\n{state["special_name"]}'
            else:
                depth_names = {1: 'ضرر 1', 2: 'ضرر 2', 3: 'ضرر 3', 4: 'ضرر 4'}
                status_text = f'ترید {state["main_trade_index"]} - {depth_names[state["loss_depth"]]}'
            
            self.status_label.text = status_text
            amount = Decimal(state['amount'])
            self.amount_label.text = f'${amount:.6f}'.rstrip('0').rstrip('.')
            self.stage_label.text = f'مرحله: {state["main_trade_index"]} / 21'
            self.win_button.disabled = False
            self.loss_button.disabled = False
            self.reset_button.text = 'ریست'
    
    def on_win(self, instance):
        success = self.state_machine.record_result('win')
        if success:
            self.save_current_state()
            self.update_display()
    
    def on_loss(self, instance):
        success = self.state_machine.record_result('loss')
        if success:
            self.save_current_state()
            self.update_display()
    
    def on_reset(self, instance):
        if self.state_machine.cycle_complete:
            self.state_machine.reset()
            self.save_current_state()
            self.update_display()
        else:
            self.show_reset_confirmation()
    
    def show_reset_confirmation(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        label = Label(text='مطمئنی می‌خواهی از ترید اول شروع کنی؟', font_size=16, halign='center')
        content.add_widget(label)
        
        buttons = BoxLayout(orientation='horizontal', spacing=10)
        yes_button = Button(text='بله', background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        no_button = Button(text='خیر', background_color=(0.5, 0.5, 0.5, 1), color=(1, 1, 1, 1))
        buttons.add_widget(yes_button)
        buttons.add_widget(no_button)
        content.add_widget(buttons)
        
        popup = Popup(title='تأیید ریست', content=content, size_hint=(0.8, 0.4))
        
        def confirm_reset(instance):
            self.state_machine.reset()
            self.save_current_state()
            self.update_display()
            popup.dismiss()
        
        yes_button.bind(on_press=confirm_reset)
        no_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_history(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        title = Label(text='تاریخچه معاملات', font_size=18, bold=True, size_hint=(1, 0.1))
        content.add_widget(title)
        
        scroll = ScrollView(size_hint=(1, 0.8))
        history_text = ''
        
        for i, entry in enumerate(self.state_machine.history[-20:]):
            trade_num = entry['trade_number']
            depth = entry['loss_depth']
            amount = entry['amount']
            result = 'سود' if entry['result'] == 'win' else 'ضرر'
            
            if depth == 0:
                trade_desc = f'ترید {trade_num}'
            else:
                trade_desc = f'ترید {trade_num}/ضرر {depth}'
            
            history_text += f'#{i+1}\n{trade_desc}: ${amount} - {result}\n\n'
        
        history_label = Label(
            text=history_text if history_text else 'تاریخچه خالی است',
            font_size=14,
            size_hint=(1, None),
            height=500
        )
        scroll.add_widget(history_label)
        content.add_widget(scroll)
        
        close_button = Button(
            text='بستن',
            size_hint=(1, 0.1),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        content.add_widget(close_button)
        
        popup = Popup(title='تاریخچه', content=content, size_hint=(0.9, 0.8))
        close_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def check_rest_timer(self, dt):
        if self.state_machine.check_rest() == False:
            self.update_display()
    
    def on_stop(self):
        self.save_current_state()

if __name__ == '__main__':
    TradeApp().run()
