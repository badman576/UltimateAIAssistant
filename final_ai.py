import os
import sys
import time
import threading
import webbrowser
import subprocess
import pyautogui
import psutil
import speech_recognition as sr
import pyttsx3
import requests
import wikipedia
import pygame
from pygame.locals import *

# Thread-safe speech engine
class SafeSpeaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 180)
        self.lock = threading.Lock()
        self.queue = []
        self.speaking = False
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def speak(self, text):
        with self.lock:
            self.queue.append(text)
    
    def _process_queue(self):
        while True:
            if self.queue and not self.speaking:
                with self.lock:
                    text = self.queue.pop(0)
                    self.speaking = True
                
                self.engine.say(text)
                self.engine.runAndWait()
                
                with self.lock:
                    self.speaking = False
            time.sleep(0.1)

class SuperAssistant:
    def __init__(self):
        # Thread-safe speech
        self.speaker = SafeSpeaker()
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        
        # Visual feedback
        pygame.init()
        self.screen = pygame.display.set_mode((300, 200))
        pygame.display.set_caption("AI Assistant")
        self.font = pygame.font.SysFont('Arial', 20)
        self.status = "Ready"
        self.last_command = ""
        
        # Start visual thread
        self.running = True
        threading.Thread(target=self._visual_feedback, daemon=True).start()
        
        print("SUPER ASSISTANT READY".center(50, "-"))
        self.say("Super assistant at your service")

    def say(self, text):
        """Thread-safe speaking"""
        print(f"AI: {text}")
        self.speaker.speak(text)

    def _visual_feedback(self):
        """Visual display that won't freeze"""
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
            
            self.screen.fill((30, 30, 70))
            status_text = self.font.render(f"Status: {self.status}", True, (255, 255, 255))
            cmd_text = self.font.render(f"Last: {self.last_command[:20]}", True, (200, 200, 255))
            self.screen.blit(status_text, (20, 20))
            self.screen.blit(cmd_text, (20, 50))
            pygame.display.flip()
            clock.tick(30)
        pygame.quit()

    def listen(self):
        """Enhanced listening with visual feedback"""
        self.status = "Listening..."
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                try:
                    text = self.recognizer.recognize_google(audio)
                    self.status = "Processing..."
                    self.last_command = text.lower()
                    return self.last_command
                except sr.UnknownValueError:
                    self.status = "Didn't understand"
                    return None
        except Exception as e:
            self.status = f"Error: {str(e)}"
            return None

    # System Control Features
    def system_control(self, command):
        if "shutdown" in command:
            if "cancel" in command:
                os.system("shutdown /a")
                return "Shutdown cancelled"
            os.system("shutdown /s /t 30")
            return "Computer will shutdown in 30 seconds"
        
        elif "restart" in command:
            os.system("shutdown /r /t 30")
            return "Computer will restart in 30 seconds"
        
        elif "lock" in command:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Locking system"

        elif "screenshot" in command:
            pyautogui.screenshot("screenshot.png")
            return "Screenshot saved"

    # Media Features
    def media_control(self, command):
        if "volume up" in command:
            for _ in range(3 if "three" in command else 1):
                pyautogui.press('volumeup')
            return "Volume increased"
        
        elif "volume down" in command:
            for _ in range(3 if "three" in command else 1):
                pyautogui.press('volumedown')
            return "Volume decreased"
        
        elif "mute" in command:
            pyautogui.press('volumemute')
            return "Sound muted"

        elif "play music" in command:
            os.system("start spotify") if sys.platform == "win32" else os.system("spotify")
            return "Playing music"

    # Web Features
    def web_operations(self, command):
        if "weather" in command:
            webbrowser.open("https://www.accuweather.com")
            return "Showing weather"
        
        elif "news" in command:
            webbrowser.open("https://news.google.com")
            return "Opening news"
        
        elif "youtube" in command:
            query = command.replace("youtube", "").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return f"Searching YouTube for {query}"

    # Knowledge Features
    def knowledge_query(self, command):
        try:
            if "explain" in command:
                query = command.replace("explain", "").strip()
                result = wikipedia.summary(query, sentences=2)
                return result
            
            elif "define" in command:
                query = command.replace("define", "").strip()
                result = wikipedia.summary(query, sentences=1)
                return f"{query} means: {result}"
        except:
            return "I couldn't find information about that"

    def execute(self, command):
        """Master command processor"""
        if not command:
            return "I didn't catch that"
        
        # System commands
        if any(cmd in command for cmd in ["shutdown", "restart", "lock", "screenshot"]):
            return self.system_control(command)
        
        # Media controls
        if any(cmd in command for cmd in ["volume", "mute", "play music"]):
            return self.media_control(command)
        
        # Web operations
        if any(cmd in command for cmd in ["weather", "news", "youtube"]):
            return self.web_operations(command)
        
        # Knowledge queries
        if any(cmd in command for cmd in ["explain", "define"]):
            return self.knowledge_query(command)
        
        # Basic commands
        if "open " in command:
            app = command.split("open ")[1]
            try:
                if sys.platform == "win32":
                    os.startfile(app) if os.path.exists(app) else subprocess.Popen(app)
                else:
                    subprocess.Popen([app])
                return f"Opening {app}"
            except:
                return f"Couldn't open {app}"
        
        if "search " in command:
            query = command.split("search ")[1]
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Searching for {query}"
        
        if any(x in command for x in ["exit", "quit", "goodbye"]):
            self.running = False
            return "Goodbye!"
        
        return "Try: 'open notepad', 'volume up', 'what's the weather', or 'explain AI'"

if __name__ == "__main__":
    assistant = SuperAssistant()
    
    try:
        while assistant.running:
            command = assistant.listen()
            if command:
                print(f"You: {command}")
                response = assistant.execute(command)
                assistant.say(response)
    except KeyboardInterrupt:
        assistant.say("Emergency shutdown")
    finally:
        assistant.running = False
        time.sleep(1)  # Let threads clean up
        print("System shutdown complete")