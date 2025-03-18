'''from kivy.config import Config
Config.set('graphics','width', '375')
Config.set('graphics','height', '665')'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
import requests
import json
import time
import os

# OpenRouter API details
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"  # OpenRouter API endpoint
API_KEY = "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"  # Replace with your actual OpenRouter API key
MODEL_NAME = "mistralai/mistral-7b-instruct"  # Change model if needed

print(os.path.exists('loading.gif'))  # Should print True if the file exists

class AIAgentApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Scrollable response area
        self.scroll_view = ScrollView(size_hint=(1, 0.6))
        self.chat_display = Label(text="Welcome to AI Agent", size_hint_y=None, text_size=(self.layout.width, None), valign='top')
        self.chat_display.bind(size=self.update_text_size)
        self.scroll_view.add_widget(self.chat_display)
        self.layout.add_widget(self.scroll_view)
        
        self.input_text = TextInput(hint_text="Ask something...", size_hint_y=0.1, multiline=False)
        self.layout.add_widget(self.input_text)
        
        # Replace the loading GIF with a text-based loading indicator
        self.loading_label = Label(text="Loading...", size_hint_y=0.1, halign="center", valign="middle")
        self.layout.add_widget(self.loading_label)
        
        self.send_button = Button(text="Send", size_hint_y=0.1)
        self.send_button.bind(on_press=self.get_ai_response)
        self.layout.add_widget(self.send_button)
        
        return self.layout
    
    def update_text_size(self, instance, value):
        self.chat_display.text_size = (self.scroll_view.width - 20, None)
        self.chat_display.size_hint_y = None
        self.chat_display.height = self.chat_display.texture_size[1]
       
    
    def get_ai_response(self, instance):
        user_input = self.input_text.text.strip()
        if user_input:
            self.loading_label.text = "Loading..."  # Show loading text
            self.chat_display.texture_update()
            self.scroll_view.scroll_y = 0  # Auto-scroll to the bottom
            self.input_text.text = ""
            
            response = self.ask_openrouter_api(user_input)
            self.chat_display.text = f"You: {user_input}\nAI: {response}"
            self.chat_display.texture_update()
           
    
    def ask_openrouter_api(self, prompt, retries=3, delay=5):
        """ Calls OpenRouter API with retry logic """
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        })
        
        for attempt in range(retries):
            try:
                response = requests.post(OPENROUTER_API_URL, headers=headers, data=data, timeout=30)
                print(response.status_code, response.text)  # Debugging output
                
                if response.status_code == 200:
                    json_response = response.json()
                    if "choices" in json_response and json_response["choices"]:
                        return json_response["choices"][0]["message"]["content"]
                    else:
                        return "No response from AI"
                elif response.status_code == 500:
                    print(f"Model too busy, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    return f"Error: {response.status_code} - {response.text}"
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}, retrying in {delay} seconds...")
                time.sleep(delay)
        
        return "Failed to get a response from the model after multiple attempts."

if __name__ == '__main__':
    AIAgentApp().run()
