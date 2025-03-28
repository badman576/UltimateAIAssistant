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
import pygame
import math
import re
import wikipedia
import requests
from pygame.locals import *
from datetime import datetime
from packaging import version

class UltimateAssistant:
    def __init__(self):
        # Initialize speech systems
        self.speaker = self._init_speech_engine()
        
        # Audio recognition setup
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        
        # Command processing
        self.command_history = []
        self.known_commands = {
            'media': ['play', 'music', 'song', 'volume', 'mute'],
            'system': ['shutdown', 'restart', 'lock', 'screenshot'],
            'info': ['history', 'last command', 'what did i say'],
            'app': ['open', 'launch', 'start'],
            'search': ['search', 'look up', 'find'],
            'knowledge': ['what is', 'who is', 'tell me about', 'explain'],
            'update': ['update', 'upgrade', 'check for updates'],
            'weather': ['weather', 'forecast', 'temperature'],
            'exit': ['exit', 'quit', 'goodbye', 'shut down', 'terminate']
        }
        
        # Visual interface
        self._init_visual_interface()
        
        # System monitoring
        self.system_stats = {
            'cpu': 0,
            'memory': 0,
            'disk': 0,
            'last_update': time.time()
        }
        
        # Current version
        self.current_version = "1.1.0"
        
        # Weather API (using OpenWeatherMap)
        self.weather_api_key = "d70de62adec8ebd18f3725f26386c3d7" 
        self.weather_location = "New York"  # Default location
        
        # Start service threads
        self.running = True
        threading.Thread(target=self._monitor_system, daemon=True).start()
        threading.Thread(target=self._run_visual_interface, daemon=True).start()
        
        print("✧ ULTIMATE AI ASSISTANT ✧".center(50, "★"))
        self.speak(f"Ultimate assistant v{self.current_version} at your service")

    def _init_speech_engine(self):
        """Initialize text-to-speech engine"""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # Voice selection priority
            voice_preference = ['zira', 'david', 'hazel', 'eva']
            for voice_name in voice_preference:
                for voice in voices:
                    if voice_name.lower() in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            engine.setProperty('rate', 165)
            engine.setProperty('volume', 0.9)
            return engine
        except Exception as e:
            print(f"Error initializing speech engine: {e}")
            # Return a dummy engine that won't crash
            class DummyEngine:
                def say(self, text): print(f"DUMMY SPEAK: {text}")
                def runAndWait(self): pass
                def setProperty(self, *args): pass
            return DummyEngine()

    def _init_visual_interface(self):
        """Initialize visual display"""
        pygame.init()
        self.screen_width = 800
        self.screen_height = 500
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.RESIZABLE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("★ ULTIMATE AI ASSISTANT ★")
        self.font_large = pygame.font.SysFont('Segoe UI', 26, bold=True)
        self.font_medium = pygame.font.SysFont('Segoe UI', 20)
        self.font_small = pygame.font.SysFont('Segoe UI', 16)
        
        # Visual elements
        self.visualizer_data = [0] * 60
        self.animation_offset = 0
        self.status = "Ready"
        self.last_command = ""

    def _monitor_system(self):
        """System monitoring with smoothing"""
        samples = []
        while self.running:
            samples.append({
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent
            })
            
            if len(samples) > 5:
                samples.pop(0)
            
            self.system_stats = {
                'cpu': sum(s['cpu'] for s in samples) / len(samples),
                'memory': sum(s['memory'] for s in samples) / len(samples),
                'disk': sum(s['disk'] for s in samples) / len(samples),
                'last_update': time.time()
            }
            time.sleep(1)

    def _run_visual_interface(self):
        """Visual interface main loop"""
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
            
            self._draw_interface()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

    def _draw_interface(self):
        """Render the visual interface"""
        # Animated background
        self.screen.fill((20, 20, 40))
        for y in range(self.screen_height):
            r = int(20 + 10 * abs(math.sin(y/50 + self.animation_offset)))
            g = int(20 + 15 * abs(math.sin(y/40 + self.animation_offset/2)))
            b = int(40 + 20 * abs(math.cos(y/60 + self.animation_offset/3)))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # System stats
        stats = [
            f"CPU: {self.system_stats['cpu']:.1f}%",
            f"MEM: {self.system_stats['memory']:.1f}%",
            f"DSK: {self.system_stats['disk']:.1f}%",
            datetime.now().strftime("%H:%M:%S")
        ]
        
        for i, stat in enumerate(stats):
            text = self.font_medium.render(stat, True, (220, 240, 255))
            self.screen.blit(text, (20, 20 + i * 25))
        
        # Status and command
        status = self.font_large.render(self.status, True, (255, 255, 200))
        self.screen.blit(status, (20, self.screen_height - 80))
        
        cmd = self.font_small.render(f"Last: {self.last_command[:40]}", True, (200, 220, 255))
        self.screen.blit(cmd, (20, self.screen_height - 40))
        
        # Visualizer
        self.visualizer_data.append(min(100, (self.system_stats['cpu'] + self.system_stats['memory'])/2))
        if len(self.visualizer_data) > 60:
            self.visualizer_data.pop(0)
        
        for i, val in enumerate(self.visualizer_data):
            x = self.screen_width - 40 - i * 6
            h = val * (self.screen_height - 120) / 100
            c = (
                int(100 + 155 * (val/100)),
                int(50 + 100 * abs(math.sin(i/10 + self.animation_offset))),
                200
            )
            pygame.draw.rect(self.screen, c, (x, self.screen_height - 60 - h, 5, h))

    def speak(self, text):
        """Speak with visual feedback"""
        print(f"AI: {text}")
        self.status = "Speaking..."
        try:
            self.speaker.say(text)
            self.speaker.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            self.status = "Ready"

    def listen(self):
        """Listen for commands"""
        self.status = "Listening..."
        with self.mic as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("\n[LISTENING] Speak now...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                text = self.recognizer.recognize_google(audio)
                print(f"You: {text}")
                self.last_command = text
                self._add_to_history(text)
                return text.lower()
            except sr.UnknownValueError:
                return None
            except Exception as e:
                print(f"Listening error: {e}")
                return None
            finally:
                self.status = "Processing..."

    def _add_to_history(self, command):
        """Maintain command history"""
        self.command_history.append(command)
        if len(self.command_history) > 10:
            self.command_history.pop(0)

    def _handle_media(self, command):
        """Handle all media commands"""
        # Volume control
        if "volume" in command:
            if "up" in command:
                try:
                    words = command.split()
                    idx = words.index("up")
                    steps = int(words[idx-1]) if idx > 0 and words[idx-1].isdigit() else 3
                    steps = max(1, min(10, steps))
                except:
                    steps = 3
                
                for _ in range(steps):
                    pyautogui.press('volumeup')
                    time.sleep(0.1)
                return f"Volume increased by {steps} levels"
            
            elif "down" in command:
                try:
                    words = command.split()
                    idx = words.index("down")
                    steps = int(words[idx-1]) if idx > 0 and words[idx-1].isdigit() else 3
                    steps = max(1, min(10, steps))
                except:
                    steps = 3
                
                for _ in range(steps):
                    pyautogui.press('volumedown')
                    time.sleep(0.1)
                return f"Volume decreased by {steps} levels"
            
            elif "mute" in command:
                pyautogui.press('volumemute')
                return "Toggled mute"
        
        # Music playback
        elif any(word in command for word in ["play", "music", "song"]):
            query = re.sub(r'play|music|song|on youtube', '', command, flags=re.IGNORECASE).strip()
            if query:
                webbrowser.open(f"https://music.youtube.com/search?q={query}")
                return f"Searching YouTube Music for {query}"
            else:
                webbrowser.open("https://music.youtube.com")
                return "Opening YouTube Music"
        
        return None

    def _handle_system(self, command):
        """Handle system commands"""
        if "shutdown" in command or "shut down" in command:
            try:
                words = command.split()
                idx = words.index("shutdown") if "shutdown" in words else words.index("shut")
                minutes = float(words[idx-1]) if idx > 0 and words[idx-1].replace('.', '').isdigit() else 0.5
                seconds = max(30, min(3600, int(minutes * 60)))
                os.system(f"shutdown /s /t {seconds}")
                return f"System will shutdown in {seconds} seconds"
            except:
                os.system("shutdown /s /t 30")
                return "System will shutdown in 30 seconds"
        
        elif "restart" in command:
            try:
                words = command.split()
                idx = words.index("restart")
                minutes = float(words[idx-1]) if idx > 0 and words[idx-1].replace('.', '').isdigit() else 0.5
                seconds = max(30, min(3600, int(minutes * 60)))
                os.system(f"shutdown /r /t {seconds}")
                return f"System will restart in {seconds} seconds"
            except:
                os.system("shutdown /r /t 30")
                return "System will restart in 30 seconds"
        
        elif "lock" in command:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Workstation locked"
        
        elif "screenshot" in command:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            pyautogui.screenshot(filename)
            return f"Screenshot saved as {filename}"
        
        return None

    def _handle_info(self, command):
        """Handle information requests"""
        if any(word in command for word in ["history", "last command", "what did i say"]):
            if self.command_history:
                last_cmd = self.command_history[-1]
                return f"Your last command was: {last_cmd}"
            return "No command history available"
        return None

    def _handle_knowledge(self, command):
        """Handle knowledge queries"""
        try:
            query = re.sub(r'what is|who is|tell me about|explain', '', command, flags=re.IGNORECASE).strip()
            if not query:
                return "Please specify what you want to know about"
            
            # Try Wikipedia first
            try:
                wikipedia.set_lang("en")
                summary = wikipedia.summary(query, sentences=2)
                return summary
            except wikipedia.exceptions.DisambiguationError as e:
                options = '\n'.join(e.options[:3])
                return f"There are multiple meanings. Did you mean:\n{options}"
            except:
                # Fallback to web search
                webbrowser.open(f"https://www.google.com/search?q={query}")
                return f"Showing web results for {query}"
        except Exception as e:
            print(f"Knowledge error: {e}")
            return "I couldn't retrieve that information"

    def _handle_update(self, command):
        """Handle update commands"""
        try:
            if "check" in command:
                # In a real app, this would call your update server
                mock_latest_version = "1.2.0"
                
                if version.parse(mock_latest_version) > version.parse(self.current_version):
                    return f"Update available (v{mock_latest_version}). Say 'update now' to install"
                return f"You're running v{self.current_version} (latest)"
            
            elif "now" in command:
                # This would actually download updates in a real implementation
                return "Update system will be implemented in future versions"
                
        except Exception as e:
            print(f"Update error: {e}")
            return "Update check failed"

    def _handle_weather(self, command):
        """Handle weather queries"""
        try:
            # Extract location if specified
            location = self.weather_location
            if "in " in command:
                location = command.split("in ")[1].strip()
            
            # Get weather data
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            complete_url = f"{base_url}q={location}&appid={self.weather_api_key}&units=metric"
            
            response = requests.get(complete_url)
            data = response.json()
            
            if data["cod"] != "404":
                main = data["main"]
                weather = data["weather"][0]
                temp = main["temp"]
                feels_like = main["feels_like"]
                description = weather["description"]
                
                return (f"Weather in {location}: {description}, "
                       f"{temp}°C (feels like {feels_like}°C)")
            else:
                return f"Weather data not found for {location}"
        except Exception as e:
            print(f"Weather error: {e}")
            return "Couldn't retrieve weather information"

    def execute(self, command):
        """Execute commands with improved understanding"""
        if not command:
            return "I didn't catch that"

        # Check exit commands first
        if any(word in command for word in self.known_commands['exit']):
            self.running = False
            return "Shutting down ultimate assistant"

        # Check other command types
        for category, keywords in self.known_commands.items():
            if category == 'exit':
                continue  # Already handled
            if any(keyword in command for keyword in keywords):
                handler = getattr(self, f"_handle_{category}", None)
                if handler:
                    result = handler(command)
                    if result:
                        return result
        
        # Special cases
        if "open " in command:
            app = command.split("open ")[1].strip()
            try:
                if sys.platform == "win32":
                    os.startfile(app) if os.path.exists(app) else subprocess.Popen(app)
                else:
                    subprocess.Popen([app])
                return f"Opening {app}"
            except:
                return f"Couldn't open {app}"
        
        elif "search " in command:
            query = command.split("search ")[1].strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Searching for {query}"
        
        elif any(word in command for word in ["beautiful", "marvelous", "awesome", "great"]):
            return "Thank you! I appreciate your kind words."
        
        # Enhanced unknown command response
        suggestions = [
            "• Media: 'play jazz music' or 'volume up 5'",
            "• System: 'shutdown in 10 minutes' or 'take screenshot'",
            "• Knowledge: 'what is quantum computing?'",
            "• Weather: 'weather in London'",
            "• Updates: 'check for updates'"
        ]
        return "I can help with:\n" + "\n".join(suggestions)

if __name__ == "__main__":
    assistant = UltimateAssistant()
    
    try:
        while assistant.running:
            command = assistant.listen()
            if command:
                response = assistant.execute(command)
                assistant.speak(response)
    except KeyboardInterrupt:
        assistant.speak("Emergency shutdown initiated")
    finally:
        assistant.running = False
        time.sleep(1)
        print("Ultimate services terminated")