import pygame
import pygame.gfxdraw
import sys
import threading
import time
import json
import webbrowser
from datetime import datetime
from tkinter import messagebox, simpledialog
import requests
import socketio
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("enhanced_user.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize pygame
pygame.init()
pygame.font.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 120, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_RED = (180, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Tourist Safety App")

# Fonts
title_font = pygame.font.SysFont('Arial', 28, bold=True)
large_font = pygame.font.SysFont('Arial', 22)
medium_font = pygame.font.SysFont('Arial', 18)
small_font = pygame.font.SysFont('Arial', 14)

# Language support
LANGUAGES = {
    'en': {
        'title': 'Tourist Safety App',
        'connect': 'Connect',
        'disconnect': 'Disconnect',
        'sos': 'EMERGENCY SOS',
        'efir': 'File E-FIR',
        'location': 'Update Location',
        'rating': 'Rate Place',
        'feedback': 'Give Feedback',
        'tracking': 'Real-time Tracking',
        'emergency_contacts': 'Emergency Contacts',
        'help_eta': 'Help ETA',
        'language': 'Language',
        'connected': 'Connected',
        'disconnected': 'Disconnected',
        'enter_aadhaar': 'Enter 12-digit Aadhaar ID',
        'enter_location': 'Enter your location',
        'current_location': 'Current',
        'welcome': 'Welcome',
        'activity_log': 'Activity Log',
        'geofence_alert': 'Geo-fence Alert!',
        'danger_zone': 'Danger Zone Detected!',
        'red_zone': 'Red Zone Alert!',
        'help_coming': 'Help is coming!',
        'eta_update': 'ETA Update'
    },
    'hi': {
        'title': 'पर्यटक सुरक्षा ऐप',
        'connect': 'कनेक्ट करें',
        'disconnect': 'डिस्कनेक्ट करें',
        'sos': 'आपातकालीन SOS',
        'efir': 'ई-एफआईआर दर्ज करें',
        'location': 'स्थान अपडेट करें',
        'rating': 'स्थान रेट करें',
        'feedback': 'फीडबैक दें',
        'tracking': 'रियल-टाइम ट्रैकिंग',
        'emergency_contacts': 'आपातकालीन संपर्क',
        'help_eta': 'सहायता ETA',
        'language': 'भाषा',
        'connected': 'जुड़ा हुआ',
        'disconnected': 'डिस्कनेक्ट हो गया',
        'enter_aadhaar': '12-अंकीय आधार आईडी दर्ज करें',
        'enter_location': 'अपना स्थान दर्ज करें',
        'current_location': 'वर्तमान',
        'welcome': 'स्वागत',
        'activity_log': 'गतिविधि लॉग',
        'geofence_alert': 'जियो-फेंस अलर्ट!',
        'danger_zone': 'खतरे का क्षेत्र मिला!',
        'red_zone': 'रेड जोन अलर्ट!',
        'help_coming': 'मदद आ रही है!',
        'eta_update': 'ETA अपडेट'
    },
    'es': {
        'title': 'App de Seguridad Turística',
        'connect': 'Conectar',
        'disconnect': 'Desconectar',
        'sos': 'SOS DE EMERGENCIA',
        'efir': 'Presentar E-FIR',
        'location': 'Actualizar Ubicación',
        'rating': 'Calificar Lugar',
        'feedback': 'Dar Comentario',
        'tracking': 'Seguimiento en Tiempo Real',
        'emergency_contacts': 'Contactos de Emergencia',
        'help_eta': 'ETA de Ayuda',
        'language': 'Idioma',
        'connected': 'Conectado',
        'disconnected': 'Desconectado',
        'enter_aadhaar': 'Ingrese ID Aadhaar de 12 dígitos',
        'enter_location': 'Ingrese su ubicación',
        'current_location': 'Actual',
        'welcome': 'Bienvenido',
        'activity_log': 'Registro de Actividad',
        'geofence_alert': '¡Alerta de Geo-cerca!',
        'danger_zone': '¡Zona Peligrosa Detectada!',
        'red_zone': '¡Alerta de Zona Roja!',
        'help_coming': '¡La ayuda viene!',
        'eta_update': 'Actualización ETA'
    }
}

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False
        self.text_color = text_color
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=8)
        
        text_surf = medium_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.action:
                self.action()
                return True
        return False

class InputBox:
    def __init__(self, x, y, width, height, text='', placeholder=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.text = text
        self.placeholder = placeholder
        self.active = False
        self.txt_surface = medium_font.render(text, True, BLACK)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = BLUE if self.active else GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = medium_font.render(self.text, True, BLACK)
        return None
        
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, 0, border_radius=5)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=5)
        
        if self.text:
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        elif not self.active and self.placeholder:
            placeholder_surf = medium_font.render(self.placeholder, True, DARK_GRAY)
            screen.blit(placeholder_surf, (self.rect.x + 5, self.rect.y + 5))

class EnhancedTouristApp:
    def __init__(self, server_url="http://localhost:3000"):
        self.server_url = server_url
        self.aadhaar_id = None
        self.name = None
        self.connected = False
        self.language = 'en'
        self.current_location = "Unknown"
        self.coordinates = None
        self.real_time_tracking = False
        self.emergency_contacts = []
        self.emergency_services = {}
        self.active_sos = None
        self.eta_info = None
        
        # Socket.IO client
        self.sio = socketio.Client(
            reconnection=True, 
            reconnection_attempts=10, 
            reconnection_delay=1000,
            reconnection_delay_max=5000
        )
        self.heartbeat_interval = None
        self.session = requests.Session()
        
        # UI state
        self.status_message = "Disconnected"
        self.status_color = RED
        self.messages = []
        self.current_screen = "login"  # login, main, efir, rating, contacts
        
        # Setup event handlers
        self.setup_socket_handlers()
        
    def setup_socket_handlers(self):
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('connect_error', self.on_connect_error)
        self.sio.on('connection_ack', self.on_connection_ack)
        self.sio.on('sos_ack', self.on_sos_ack)
        self.sio.on('geofence_alert', self.on_geofence_alert)
        self.sio.on('red_zone_alert', self.on_red_zone_alert)
        self.sio.on('eta_update', self.on_eta_update)
        self.sio.on('help_arrived', self.on_help_arrived)
        self.sio.on('efir_ack', self.on_efir_ack)
        self.sio.on('rating_ack', self.on_rating_ack)
        self.sio.on('feedback_ack', self.on_feedback_ack)
        
    def get_text(self, key):
        return LANGUAGES.get(self.language, LANGUAGES['en']).get(key, key)
        
    def add_message(self, message, is_alert=False):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append((f"[{timestamp}] {message}", is_alert))
        if len(self.messages) > 15:
            self.messages.pop(0)
        logger.info(message)
        
    def on_connect(self):
        logger.info("Connected to server")
        self.connected = True
        self.status_message = self.get_text('connected')
        self.status_color = GREEN
        self.add_message("Connected to server")
        self.start_heartbeat()
        
    def on_disconnect(self):
        logger.warning("Disconnected from server")
        self.connected = False
        self.status_message = self.get_text('disconnected')
        self.status_color = RED
        self.add_message("Disconnected from server", True)
        self.stop_heartbeat()
        
    def on_connect_error(self, data):
        logger.error(f"Connection error: {data}")
        self.connected = False
        self.status_message = "Connection Error"
        self.status_color = RED
        self.add_message(f"Connection error: {data}", True)
        
    def on_connection_ack(self, data):
        self.name = data.get('name', 'Unknown')
        self.emergency_services = data.get('emergency_services', {})
        user_data = data.get('user_data', {})
        if user_data:
            self.emergency_contacts = user_data.get('emergency_contacts', [])
            self.real_time_tracking = user_data.get('real_time_tracking', False)
        logger.info(f"Connection acknowledged: {self.name}")
        self.add_message(f"Connected as {self.name}")
        
    def on_sos_ack(self, data):
        sos_id = data.get('sos_id', 'Unknown')
        message = data.get('message', 'SOS acknowledged')
        eta = data.get('eta_minutes', 0)
        self.active_sos = sos_id
        self.eta_info = {'eta_minutes': eta, 'help_type': data.get('help_type', 'general')}
        logger.info(f"SOS acknowledged: {sos_id} - ETA: {eta} minutes")
        self.add_message(f"SOS sent! Help arriving in {eta} minutes")
        
    def on_geofence_alert(self, data):
        zone = data.get('zone', {})
        message = data.get('message', 'Geofence alert')
        self.add_message(f"⚠️ {message}: {zone.get('name', 'Unknown zone')}", True)
        # Show popup alert
        threading.Thread(target=lambda: messagebox.showwarning(
            self.get_text('geofence_alert'), 
            f"{message}\nZone: {zone.get('name', 'Unknown')}"
        ), daemon=True).start()
        
    def on_red_zone_alert(self, data):
        zone = data.get('zone', {})
        message = data.get('message', 'Red zone alert')
        self.add_message(f"🚨 {message}: {zone.get('name', 'Unknown zone')}", True)
        threading.Thread(target=lambda: messagebox.showerror(
            self.get_text('red_zone'), 
            f"{message}\nZone: {zone.get('name', 'Unknown')}"
        ), daemon=True).start()
        
    def on_eta_update(self, data):
        eta = data.get('eta_minutes', 0)
        if self.eta_info:
            self.eta_info['eta_minutes'] = eta
        self.add_message(f"ETA Update: Help arriving in {eta} minutes")
        
    def on_help_arrived(self, data):
        self.active_sos = None
        self.eta_info = None
        self.add_message("✅ Help has arrived at your location!")
        threading.Thread(target=lambda: messagebox.showinfo(
            "Help Arrived", "Emergency help has arrived at your location!"
        ), daemon=True).start()
        
    def on_efir_ack(self, data):
        ref_number = data.get('reference_number', 'Unknown')
        self.add_message(f"E-FIR filed successfully. Ref: {ref_number}")
        
    def on_rating_ack(self, data):
        self.add_message(f"Rating submitted for {data.get('place', 'location')}")
        
    def on_feedback_ack(self, data):
        self.add_message("Feedback submitted successfully")
        
    def start_heartbeat(self):
        def send_heartbeat():
            while self.connected:
                try:
                    self.sio.emit('heartbeat', {
                        'type': 'user',
                        'aadhaar_id': self.aadhaar_id,
                        'timestamp': datetime.now().isoformat()
                    })
                    time.sleep(10)
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
                    break
                    
        self.heartbeat_interval = threading.Thread(target=send_heartbeat, daemon=True)
        self.heartbeat_interval.start()
        
    def stop_heartbeat(self):
        self.connected = False
        if self.heartbeat_interval and self.heartbeat_interval.is_alive():
            time.sleep(1.1)
            
    def connect(self, aadhaar_id):
        self.aadhaar_id = aadhaar_id
        
        try:
            # HTTP connection first
            response = self.session.post(
                f"{self.server_url}/connect", 
                json={"aadhaar_id": aadhaar_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.name = data.get('name', 'Unknown')
                self.current_location = data.get('location', 'Unknown')
                self.emergency_services = data.get('emergency_services', {})
                
                # WebSocket connection
                self.sio.connect(self.server_url)
                self.sio.emit('user_connect', {
                    'aadhaar_id': aadhaar_id,
                    'client_type': 'user',
                    'name': self.name,
                    'version': '3.0',
                    'language': self.language
                })
                
                self.current_screen = "main"
                return True
            else:
                error_msg = response.json().get('error', 'Connection failed')
                self.add_message(f"Connection failed: {error_msg}", True)
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.add_message(f"Connection error: {e}", True)
            return False
            
    def send_sos(self, help_type='general'):
        if not self.connected:
            self.add_message("Not connected to server", True)
            return False
            
        try:
            sos_data = {
                'aadhaar_id': self.aadhaar_id,
                'location': self.current_location,
                'message': 'Emergency assistance needed!',
                'coordinates': self.coordinates,
                'help_type': help_type
            }
            
            self.sio.emit('sos_signal', sos_data)
            logger.info("SOS signal sent successfully!")
            self.add_message("🚨 SOS signal sent! Help is on the way.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SOS: {e}")
            self.add_message(f"Failed to send SOS: {e}", True)
            return False
            
    def update_location(self, location, coordinates=None):
        if self.connected:
            self.current_location = location
            self.coordinates = coordinates
            self.sio.emit('location_update', {
                'location': location,
                'coordinates': coordinates
            })
            self.add_message(f"Location updated to: {location}")
        else:
            self.add_message("Not connected to server", True)
            
    def file_efir(self, incident_type, description, location=None):
        if not self.connected:
            self.add_message("Not connected to server", True)
            return False
            
        try:
            efir_data = {
                'incident_type': incident_type,
                'description': description,
                'location': location or self.current_location,
                'coordinates': self.coordinates
            }
            
            self.sio.emit('file_efir', efir_data)
            self.add_message("E-FIR filed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to file E-FIR: {e}")
            self.add_message(f"Failed to file E-FIR: {e}", True)
            return False
            
    def submit_rating(self, place_name, rating):
        if not self.connected:
            self.add_message("Not connected to server", True)
            return False
            
        try:
            rating_data = {
                'place_name': place_name,
                'place_id': place_name.lower().replace(' ', '_'),
                'rating': rating,
                'location': self.current_location
            }
            
            self.sio.emit('submit_rating', rating_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit rating: {e}")
            self.add_message(f"Failed to submit rating: {e}", True)
            return False
            
    def submit_feedback(self, place_name, feedback):
        if not self.connected:
            self.add_message("Not connected to server", True)
            return False
            
        try:
            feedback_data = {
                'place_name': place_name,
                'place_id': place_name.lower().replace(' ', '_'),
                'feedback': feedback,
                'location': self.current_location
            }
            
            self.sio.emit('submit_feedback', feedback_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit feedback: {e}")
            self.add_message(f"Failed to submit feedback: {e}", True)
            return False
            
    def toggle_real_time_tracking(self):
        if not self.connected:
            self.add_message("Not connected to server", True)
            return
            
        self.real_time_tracking = not self.real_time_tracking
        self.sio.emit('toggle_tracking', {'enabled': self.real_time_tracking})
        status = "enabled" if self.real_time_tracking else "disabled"
        self.add_message(f"Real-time tracking {status}")
        
    def show_efir_dialog(self):
        def submit_efir():
            incident_type = incident_var.get()
            description = desc_text.get("1.0", tk.END).strip()
            if incident_type and description:
                self.file_efir(incident_type, description)
                dialog.destroy()
            
        dialog = tk.Toplevel()
        dialog.title("File E-FIR")
        dialog.geometry("400x300")
        
        tk.Label(dialog, text="Incident Type:").pack(pady=5)
        incident_var = tk.StringVar()
        incident_combo = ttk.Combobox(dialog, textvariable=incident_var, values=[
            "Theft", "Fraud", "Harassment", "Accident", "Lost Property", "Other"
        ])
        incident_combo.pack(pady=5)
        
        tk.Label(dialog, text="Description:").pack(pady=5)
        desc_text = scrolledtext.ScrolledText(dialog, height=8, width=40)
        desc_text.pack(pady=5)
        
        tk.Button(dialog, text="Submit E-FIR", command=submit_efir).pack(pady=10)
        
    def show_rating_dialog(self):
        def submit_rating():
            place = place_entry.get().strip()
            rating = rating_var.get()
            if place and rating > 0:
                self.submit_rating(place, rating)
                dialog.destroy()
            
        dialog = tk.Toplevel()
        dialog.title("Rate Place")
        dialog.geometry("300x200")
        
        tk.Label(dialog, text="Place Name:").pack(pady=5)
        place_entry = tk.Entry(dialog, width=30)
        place_entry.pack(pady=5)
        
        tk.Label(dialog, text="Rating (1-5 stars):").pack(pady=5)
        rating_var = tk.IntVar()
        for i in range(1, 6):
            tk.Radiobutton(dialog, text=f"{i} Star{'s' if i > 1 else ''}", 
                          variable=rating_var, value=i).pack()
        
        tk.Button(dialog, text="Submit Rating", command=submit_rating).pack(pady=10)
        
    def show_feedback_dialog(self):
        def submit_feedback():
            place = place_entry.get().strip()
            feedback = feedback_text.get("1.0", tk.END).strip()
            if place and feedback:
                self.submit_feedback(place, feedback)
                dialog.destroy()
            
        dialog = tk.Toplevel()
        dialog.title("Give Feedback")
        dialog.geometry("400x300")
        
        tk.Label(dialog, text="Place Name:").pack(pady=5)
        place_entry = tk.Entry(dialog, width=30)
        place_entry.pack(pady=5)
        
        tk.Label(dialog, text="Feedback:").pack(pady=5)
        feedback_text = scrolledtext.ScrolledText(dialog, height=8, width=40)
        feedback_text.pack(pady=5)
        
        tk.Button(dialog, text="Submit Feedback", command=submit_feedback).pack(pady=10)
        
    def change_language(self):
        languages = list(LANGUAGES.keys())
        current_index = languages.index(self.language)
        next_index = (current_index + 1) % len(languages)
        self.language = languages[next_index]
        self.add_message(f"Language changed to: {self.language.upper()}")
        
    def disconnect(self):
        self.connected = False
        self.status_message = self.get_text('disconnected')
        self.status_color = RED
        self.stop_heartbeat()
        self.sio.disconnect()
        self.current_screen = "login"
        self.add_message("Disconnected from server")

def main():
    app = EnhancedTouristApp()
    clock = pygame.time.Clock()
    
    # UI elements for login screen
    aadhaar_input = InputBox(400, 300, 400, 50, '', 'Enter 12-digit Aadhaar ID')
    connect_button = Button(400, 370, 400, 60, "Connect", GREEN, LIGHT_BLUE, 
                           lambda: app.connect(aadhaar_input.text) if len(aadhaar_input.text) == 12 else None)
    
    # UI elements for main screen
    location_input = InputBox(50, 150, 300, 40, '', 'Enter your location')
    
    # Create buttons for main screen
    buttons = {
        'update_location': Button(50, 200, 150, 40, "Update Location", BLUE, LIGHT_BLUE,
                                 lambda: app.update_location(location_input.text)),
        'sos_general': Button(50, 250, 150, 50, "SOS General", RED, (255, 100, 100),
                             lambda: app.send_sos('general')),
        'sos_police': Button(220, 250, 150, 50, "SOS Police", RED, (255, 100, 100),
                            lambda: app.send_sos('police')),
        'sos_medical': Button(390, 250, 150, 50, "SOS Medical", RED, (255, 100, 100),
                             lambda: app.send_sos('ambulance')),
        'efir': Button(50, 320, 150, 40, "File E-FIR", ORANGE, (255, 200, 100),
                      lambda: threading.Thread(target=app.show_efir_dialog, daemon=True).start()),
        'rating': Button(220, 320, 150, 40, "Rate Place", YELLOW, (255, 255, 150),
                        lambda: threading.Thread(target=app.show_rating_dialog, daemon=True).start()),
        'feedback': Button(390, 320, 150, 40, "Give Feedback", PURPLE, (200, 100, 200),
                          lambda: threading.Thread(target=app.show_feedback_dialog, daemon=True).start()),
        'tracking': Button(50, 370, 150, 40, "Toggle Tracking", BLUE, LIGHT_BLUE,
                          lambda: app.toggle_real_time_tracking()),
        'language': Button(220, 370, 150, 40, "Language", GRAY, LIGHT_GRAY,
                          lambda: app.change_language()),
        'disconnect': Button(390, 370, 150, 40, "Disconnect", DARK_RED, (255, 100, 100),
                            lambda: app.disconnect())
    }
    
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if app.current_screen == "login":
                aadhaar_input.handle_event(event)
                connect_button.check_hover(mouse_pos)
                connect_button.handle_event(event)
            elif app.current_screen == "main":
                location_input.handle_event(event)
                for button in buttons.values():
                    button.check_hover(mouse_pos)
                    button.handle_event(event)
                
        # Draw UI
        screen.fill(LIGHT_GRAY)
        
        if app.current_screen == "login":
            # Draw login screen
            title_text = title_font.render(app.get_text('title'), True, BLACK)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 200))
            
            instruction = large_font.render(app.get_text('enter_aadhaar'), True, BLACK)
            screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 250))
            
            aadhaar_input.draw(screen)
            connect_button.draw(screen)
            
            # Test IDs hint
            test_text = small_font.render("Test IDs: 123456789012, 987654321098, 456789012345", True, DARK_GRAY)
            screen.blit(test_text, (WIDTH // 2 - test_text.get_width() // 2, 450))
            
        elif app.current_screen == "main":
            # Draw header
            pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, 80))
            title_text = title_font.render(app.get_text('title'), True, WHITE)
            screen.blit(title_text, (20, 25))
            
            # Status indicator
            status_bg = pygame.Rect(WIDTH - 200, 20, 180, 40)
            pygame.draw.rect(screen, WHITE, status_bg, border_radius=5)
            pygame.draw.rect(screen, app.status_color, status_bg, 2, border_radius=5)
            status_text = medium_font.render(app.status_message, True, BLACK)
            screen.blit(status_text, (status_bg.centerx - status_text.get_width() // 2, 
                                     status_bg.centery - status_text.get_height() // 2))
            
            # Welcome message
            welcome_text = large_font.render(f"{app.get_text('welcome')}, {app.name}!", True, BLACK)
            screen.blit(welcome_text, (50, 100))
            
            # Location section
            location_label = medium_font.render("Location:", True, BLACK)
            screen.blit(location_label, (50, 120))
            location_input.draw(screen)
            
            # Current location display
            curr_loc_text = small_font.render(f"{app.get_text('current_location')}: {app.current_location}", True, BLACK)
            screen.blit(curr_loc_text, (50, 420))
            
            # Language display
            lang_text = small_font.render(f"{app.get_text('language')}: {app.language.upper()}", True, BLACK)
            screen.blit(lang_text, (50, 440))
            
            # Tracking status
            tracking_status = "ON" if app.real_time_tracking else "OFF"
            tracking_text = small_font.render(f"{app.get_text('tracking')}: {tracking_status}", True, BLACK)
            screen.blit(tracking_text, (50, 460))
            
            # Draw all buttons
            for button in buttons.values():
                button.draw(screen)
            
            # ETA display if active
            if app.eta_info:
                eta_bg = pygame.Rect(600, 150, 300, 100)
                pygame.draw.rect(screen, YELLOW, eta_bg, border_radius=10)
                pygame.draw.rect(screen, BLACK, eta_bg, 2, border_radius=10)
                
                eta_title = medium_font.render(app.get_text('help_eta'), True, BLACK)
                screen.blit(eta_title, (620, 170))
                
                eta_text = large_font.render(f"{app.eta_info['eta_minutes']} minutes", True, RED)
                screen.blit(eta_text, (620, 200))
                
                help_type_text = small_font.render(f"Type: {app.eta_info['help_type']}", True, BLACK)
                screen.blit(help_type_text, (620, 230))
            
            # Emergency contacts section
            contacts_bg = pygame.Rect(600, 270, 300, 200)
            pygame.draw.rect(screen, WHITE, contacts_bg, border_radius=5)
            pygame.draw.rect(screen, DARK_GRAY, contacts_bg, 2, border_radius=5)
            
            contacts_title = medium_font.render(app.get_text('emergency_contacts'), True, BLACK)
            screen.blit(contacts_title, (620, 280))
            
            y_offset = 310
            # Show emergency services
            for service, info in app.emergency_services.items():
                service_text = small_font.render(f"{info['name']}: {info['phone']}", True, BLACK)
                screen.blit(service_text, (620, y_offset))
                y_offset += 20
                if y_offset > 450:
                    break
            
            # Activity log
            log_bg = pygame.Rect(950, 100, 230, 500)
            pygame.draw.rect(screen, WHITE, log_bg, border_radius=5)
            pygame.draw.rect(screen, DARK_GRAY, log_bg, 2, border_radius=5)
            
            log_title = medium_font.render(app.get_text('activity_log'), True, BLACK)
            screen.blit(log_title, (1065 - log_title.get_width() // 2, 110))
            
            # Draw messages
            for i, (message, is_alert) in enumerate(app.messages[-20:]):
                msg_color = RED if is_alert else BLACK
                # Wrap long messages
                if len(message) > 30:
                    message = message[:27] + "..."
                msg_surface = small_font.render(message, True, msg_color)
                screen.blit(msg_surface, (960, 140 + i * 22))
        
        pygame.display.flip()
        clock.tick(30)
        
    app.disconnect()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()