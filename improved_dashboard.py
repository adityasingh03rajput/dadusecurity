import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import json
import webbrowser
from datetime import datetime, timezone
import socketio
import logging
import sys
import os
from typing import Dict, List, Any, Optional
import requests

# Set up logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("improved_dashboard.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ImprovedDashboardUI:
    def __init__(self, root, server_url="http://localhost:3000"):
        self.root = root
        self.root.title("🚨 Enhanced Tourist Safety Dashboard - Real-time Monitoring")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#f0f8ff')
        
        # Apply modern theme
        style = ttk.Style()
        style.theme_use('clam')
        
        self.server_url = server_url
        self.sio = socketio.Client(
            reconnection=True, 
            reconnection_attempts=5, 
            reconnection_delay=2,
            reconnection_delay_max=10,
            logger=False,
            engineio_logger=False
        )
        
        # Data storage
        self.connected_users = []
        self.sos_signals = []
        self.efir_reports = []
        self.connection_stats = {}
        self.places_data = {}
        
        # Connection state
        self.connected = False
        self.heartbeat_interval = None
        self.last_update = None
        self.auto_refresh = True
        
        # Setup Socket.IO event handlers
        self.setup_socket_handlers()
        
        self.create_widgets()
        self.update_status("🔴 Not Connected", "red")
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Auto-refresh timer
        self.start_auto_refresh()
        
    def setup_socket_handlers(self):
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('connect_error', self.on_connect_error)
        self.sio.on('users_update', self.on_users_update)
        self.sio.on('sos_update', self.on_sos_update)
        self.sio.on('stats_update', self.on_stats_update)
        self.sio.on('new_sos_alert', self.on_new_sos_alert)
        self.sio.on('new_efir', self.on_new_efir)
        self.sio.on('heartbeat_ack', self.on_heartbeat_ack)
        
    def create_widgets(self):
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)
        
        # Header section
        self.create_header(main_container)
        
        # Status and controls section
        self.create_status_controls(main_container)
        
        # Main content area with tabs
        self.create_main_content(main_container)
        
    def create_header(self, parent):
        # Header frame with gradient-like appearance
        header_frame = tk.Frame(parent, bg='#1e3a8a', height=80)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.grid_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="🚨 ENHANCED TOURIST SAFETY DASHBOARD", 
            font=("Arial", 20, "bold"), 
            fg="white", 
            bg='#1e3a8a'
        )
        title_label.pack(pady=20)
        
    def create_status_controls(self, parent):
        # Status and controls frame
        status_frame = ttk.LabelFrame(parent, text="System Status & Controls", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status indicators row
        status_row = ttk.Frame(status_frame)
        status_row.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Connection status
        ttk.Label(status_row, text="Connection:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=(0, 5))
        self.status_label = ttk.Label(status_row, text="🔴 Not Connected", font=("Arial", 10, "bold"))
        self.status_label.grid(row=0, column=1, padx=(0, 20))
        
        # Last update
        ttk.Label(status_row, text="Last Update:", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=(0, 5))
        self.update_label = ttk.Label(status_row, text="Never", font=("Arial", 10))
        self.update_label.grid(row=0, column=3, padx=(0, 20))
        
        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(status_row, text="Auto Refresh", variable=self.auto_refresh_var, 
                       command=self.toggle_auto_refresh).grid(row=0, column=4, padx=(0, 20))
        
        # Statistics row
        stats_row = ttk.Frame(status_frame)
        stats_row.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Stats labels with better styling
        self.active_conn_label = ttk.Label(stats_row, text="🟢 Active: 0", font=("Arial", 10, "bold"))
        self.active_conn_label.grid(row=0, column=0, padx=(0, 15))
        
        self.total_conn_label = ttk.Label(stats_row, text="📊 Total: 0", font=("Arial", 10))
        self.total_conn_label.grid(row=0, column=1, padx=(0, 15))
        
        self.sos_count_label = ttk.Label(stats_row, text="🚨 SOS: 0", font=("Arial", 10, "bold"), foreground="red")
        self.sos_count_label.grid(row=0, column=2, padx=(0, 15))
        
        self.efir_count_label = ttk.Label(stats_row, text="📋 E-FIR: 0", font=("Arial", 10), foreground="orange")
        self.efir_count_label.grid(row=0, column=3, padx=(0, 15))
        
        # Control buttons row
        controls_row = ttk.Frame(status_frame)
        controls_row.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Styled buttons
        self.connect_button = ttk.Button(controls_row, text="🔌 Connect", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(controls_row, text="🔄 Refresh", command=self.manual_refresh).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(controls_row, text="📤 Export Data", command=self.export_data).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(controls_row, text="🗺️ Show Map", command=self.show_map).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(controls_row, text="📈 Analytics", command=self.show_analytics).grid(row=0, column=4, padx=(0, 10))
        ttk.Button(controls_row, text="⚙️ Settings", command=self.show_settings).grid(row=0, column=5, padx=(0, 10))
        
    def create_main_content(self, parent):
        # Notebook for tabs with better styling
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs with improved layouts
        self.create_sos_tab()
        self.create_users_tab()
        self.create_efir_tab()
        self.create_tracking_tab()
        self.create_analytics_tab()
        
    def create_sos_tab(self):
        sos_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(sos_frame, text="🚨 SOS Emergency Signals")
        
        # SOS header with summary
        sos_header = ttk.LabelFrame(sos_frame, text="Emergency Overview", padding="5")
        sos_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.sos_summary_label = ttk.Label(sos_header, text="No active SOS signals", font=("Arial", 12, "bold"))
        self.sos_summary_label.grid(row=0, column=0)
        
        # SOS list with enhanced columns
        sos_list_frame = ttk.LabelFrame(sos_frame, text="Active SOS Signals", padding="5")
        sos_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Enhanced SOS tree
        sos_columns = ('priority', 'name', 'location', 'help_type', 'time', 'eta', 'status', 'phone')
        self.sos_tree = ttk.Treeview(sos_list_frame, columns=sos_columns, show='headings', height=12)
        
        # Define headings with better names
        headings = {
            'priority': '🔥 Priority',
            'name': '👤 Name', 
            'location': '📍 Location',
            'help_type': '🚑 Help Type',
            'time': '⏰ Time',
            'eta': '⏱️ ETA',
            'status': '📊 Status',
            'phone': '📞 Phone'
        }
        
        for col, heading in headings.items():
            self.sos_tree.heading(col, text=heading)
            self.sos_tree.column(col, width=120)
        
        # Scrollbar
        sos_scrollbar = ttk.Scrollbar(sos_list_frame, orient=tk.VERTICAL, command=self.sos_tree.yview)
        self.sos_tree.configure(yscrollcommand=sos_scrollbar.set)
        
        self.sos_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sos_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # SOS action buttons
        sos_actions = ttk.Frame(sos_frame)
        sos_actions.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(sos_actions, text="✅ Resolve Selected", command=self.resolve_sos).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(sos_actions, text="🚑 Dispatch Help", command=self.dispatch_help).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(sos_actions, text="⏱️ Update ETA", command=self.update_eta).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(sos_actions, text="📞 Contact User", command=self.contact_user).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(sos_actions, text="🗑️ Clear All", command=self.clear_sos).grid(row=0, column=4)
        
        # Configure grid weights
        sos_frame.columnconfigure(0, weight=1)
        sos_frame.rowconfigure(1, weight=1)
        sos_list_frame.columnconfigure(0, weight=1)
        sos_list_frame.rowconfigure(0, weight=1)
        
    def create_users_tab(self):
        users_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(users_frame, text="👥 Connected Users")
        
        # Users summary
        users_header = ttk.LabelFrame(users_frame, text="Users Overview", padding="5")
        users_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.users_summary_label = ttk.Label(users_header, text="No users connected", font=("Arial", 12, "bold"))
        self.users_summary_label.grid(row=0, column=0)
        
        # Users list
        users_list_frame = ttk.LabelFrame(users_frame, text="Active Users", padding="5")
        users_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        user_columns = ('status_icon', 'name', 'type', 'location', 'language', 'connected_time', 'tracking', 'sos_status')
        self.users_tree = ttk.Treeview(users_list_frame, columns=user_columns, show='headings', height=15)
        
        user_headings = {
            'status_icon': '🔵 Status',
            'name': '👤 Name',
            'type': '🏷️ Type', 
            'location': '📍 Location',
            'language': '🌐 Language',
            'connected_time': '⏰ Connected',
            'tracking': '📍 Tracking',
            'sos_status': '🚨 SOS Status'
        }
        
        for col, heading in user_headings.items():
            self.users_tree.heading(col, text=heading)
            self.users_tree.column(col, width=120)
        
        users_scrollbar = ttk.Scrollbar(users_list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        users_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        users_frame.columnconfigure(0, weight=1)
        users_frame.rowconfigure(1, weight=1)
        users_list_frame.columnconfigure(0, weight=1)
        users_list_frame.rowconfigure(0, weight=1)
        
    def create_efir_tab(self):
        efir_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(efir_frame, text="📋 E-FIR Reports")
        
        # E-FIR summary
        efir_header = ttk.LabelFrame(efir_frame, text="E-FIR Overview", padding="5")
        efir_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.efir_summary_label = ttk.Label(efir_header, text="No E-FIR reports", font=("Arial", 12, "bold"))
        self.efir_summary_label.grid(row=0, column=0)
        
        # E-FIR list
        efir_list_frame = ttk.LabelFrame(efir_frame, text="Filed Reports", padding="5")
        efir_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        efir_columns = ('priority', 'user_name', 'incident_type', 'location', 'time', 'status', 'reference')
        self.efir_tree = ttk.Treeview(efir_list_frame, columns=efir_columns, show='headings', height=10)
        
        efir_headings = {
            'priority': '🔥 Priority',
            'user_name': '👤 User Name',
            'incident_type': '📋 Incident Type',
            'location': '📍 Location',
            'time': '⏰ Filed Time',
            'status': '📊 Status',
            'reference': '🔢 Reference'
        }
        
        for col, heading in efir_headings.items():
            self.efir_tree.heading(col, text=heading)
            self.efir_tree.column(col, width=130)
        
        efir_scrollbar = ttk.Scrollbar(efir_list_frame, orient=tk.VERTICAL, command=self.efir_tree.yview)
        self.efir_tree.configure(yscrollcommand=efir_scrollbar.set)
        
        self.efir_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        efir_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # E-FIR details
        details_frame = ttk.LabelFrame(efir_frame, text="Report Details", padding="5")
        details_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.efir_details = scrolledtext.ScrolledText(details_frame, height=8, width=100, font=("Consolas", 10))
        self.efir_details.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Bind selection event
        self.efir_tree.bind('<<TreeviewSelect>>', self.on_efir_select)
        
        # Configure grid weights
        efir_frame.columnconfigure(0, weight=1)
        efir_frame.rowconfigure(1, weight=1)
        efir_list_frame.columnconfigure(0, weight=1)
        efir_list_frame.rowconfigure(0, weight=1)
        
    def create_tracking_tab(self):
        tracking_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tracking_frame, text="📍 Real-time Tracking")
        
        # Tracking controls
        tracking_header = ttk.LabelFrame(tracking_frame, text="Tracking Controls", padding="5")
        tracking_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(tracking_header, text="Real-time Location Tracking", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=(0, 20))
        ttk.Button(tracking_header, text="🔄 Refresh Locations", command=self.refresh_tracking).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(tracking_header, text="🗺️ Show on Map", command=self.show_tracking_map).grid(row=0, column=2)
        
        # Tracking list
        tracking_list_frame = ttk.LabelFrame(tracking_frame, text="User Locations", padding="5")
        tracking_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        tracking_columns = ('status', 'name', 'location', 'coordinates', 'last_update', 'tracking_enabled', 'movement')
        self.tracking_tree = ttk.Treeview(tracking_list_frame, columns=tracking_columns, show='headings', height=18)
        
        tracking_headings = {
            'status': '🔵 Status',
            'name': '👤 User Name',
            'location': '📍 Location',
            'coordinates': '🗺️ Coordinates',
            'last_update': '⏰ Last Update',
            'tracking_enabled': '📍 Tracking',
            'movement': '🚶 Movement'
        }
        
        for col, heading in tracking_headings.items():
            self.tracking_tree.heading(col, text=heading)
            self.tracking_tree.column(col, width=140)
        
        tracking_scrollbar = ttk.Scrollbar(tracking_list_frame, orient=tk.VERTICAL, command=self.tracking_tree.yview)
        self.tracking_tree.configure(yscrollcommand=tracking_scrollbar.set)
        
        self.tracking_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tracking_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        tracking_frame.columnconfigure(0, weight=1)
        tracking_frame.rowconfigure(1, weight=1)
        tracking_list_frame.columnconfigure(0, weight=1)
        tracking_list_frame.rowconfigure(0, weight=1)
        
    def create_analytics_tab(self):
        analytics_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(analytics_frame, text="📈 Analytics & Reports")
        
        # Analytics header
        analytics_header = ttk.LabelFrame(analytics_frame, text="System Analytics", padding="5")
        analytics_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(analytics_header, text="Dashboard Analytics & Reporting", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=(0, 20))
        ttk.Button(analytics_header, text="📊 Generate Report", command=self.generate_report).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(analytics_header, text="📈 Show Charts", command=self.show_charts).grid(row=0, column=2)
        
        # Analytics content
        analytics_content = ttk.LabelFrame(analytics_frame, text="System Statistics", padding="10")
        analytics_content.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Statistics display
        self.analytics_text = scrolledtext.ScrolledText(analytics_content, height=25, width=120, font=("Consolas", 10))
        self.analytics_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        analytics_frame.columnconfigure(0, weight=1)
        analytics_frame.rowconfigure(1, weight=1)
        analytics_content.columnconfigure(0, weight=1)
        analytics_content.rowconfigure(0, weight=1)
        
    # Event handlers
    def on_connect(self):
        logger.info("Dashboard connected to server")
        self.root.after(0, lambda: self.update_status("🟢 Connected", "green"))
        self.sio.emit('user_connect', {
            'aadhaar_id': 'improved_dashboard',
            'client_type': 'dashboard',
            'name': 'Improved Monitoring Dashboard',
            'version': '3.0'
        })
        self.start_heartbeat()
        self.root.after(0, self.update_display)
    
    def on_disconnect(self, reason=None):
        logger.warning(f"Dashboard disconnected: {reason}")
        self.root.after(0, lambda: self.update_status("🔴 Disconnected", "red"))
        self.stop_heartbeat()
        self.root.after(0, self.update_display)
    
    def on_connect_error(self, data):
        logger.error(f"Connection error: {data}")
        self.root.after(0, lambda: self.update_status("🔴 Connection Error", "red"))
    
    def on_users_update(self, data):
        logger.info(f"Received users update: {len(data)} users")
        self.connected_users = data
        self.last_update = datetime.now()
        self.root.after(0, self.update_display)
    
    def on_sos_update(self, data):
        logger.info(f"Received SOS update: {len(data)} signals")
        self.sos_signals = data
        self.last_update = datetime.now()
        self.root.after(0, self.update_display)
    
    def on_stats_update(self, data):
        logger.info(f"Received stats update: {data}")
        self.connection_stats = data
        self.last_update = datetime.now()
        self.root.after(0, self.update_display)
    
    def on_new_sos_alert(self, data):
        logger.warning(f"🚨 NEW SOS ALERT: {data.get('name', 'Unknown')} at {data.get('location', 'Unknown')}")
        def show_alert():
            messagebox.showwarning(
                "🚨 EMERGENCY SOS ALERT", 
                f"New SOS Emergency!\n\n"
                f"👤 User: {data.get('name', 'Unknown')}\n"
                f"📍 Location: {data.get('location', 'Unknown')}\n"
                f"🚑 Help Type: {data.get('help_type', 'General')}\n"
                f"⏱️ ETA: {data.get('eta', 'Unknown')} minutes\n"
                f"📞 Phone: {data.get('phone', 'N/A')}\n\n"
                f"⚠️ Immediate action required!"
            )
        self.root.after(0, show_alert)
        
        # Play alert sound
        if sys.platform == "win32":
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                pass
    
    def on_new_efir(self, data):
        logger.info(f"New E-FIR: {data.get('incident_type', 'Unknown')} by {data.get('user_name', 'Unknown')}")
        self.efir_reports.append(data)
        self.root.after(0, self.update_display)
    
    def on_heartbeat_ack(self, data):
        pass  # Heartbeat acknowledged
    
    # Connection management
    def toggle_connection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        try:
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            logger.error(f"Cannot connect to server: {e}")
            messagebox.showerror("Connection Error", f"Cannot connect to server:\n{e}")
            return False
    
    def disconnect(self):
        self.stop_heartbeat()
        try:
            if self.sio.connected:
                self.sio.disconnect()
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    def start_heartbeat(self):
        def send_heartbeat():
            while self.connected:
                try:
                    self.sio.emit('heartbeat', {'type': 'dashboard', 'timestamp': datetime.now().isoformat()})
                    time.sleep(10)
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
                    break
        self.heartbeat_interval = threading.Thread(target=send_heartbeat, daemon=True)
        self.heartbeat_interval.start()
        
    def stop_heartbeat(self):
        self.connected = False
    
    # Auto-refresh functionality
    def start_auto_refresh(self):
        def auto_refresh_loop():
            while True:
                if self.auto_refresh and self.connected:
                    self.root.after(0, self.update_display)
                time.sleep(5)  # Refresh every 5 seconds
        threading.Thread(target=auto_refresh_loop, daemon=True).start()
    
    def toggle_auto_refresh(self):
        self.auto_refresh = self.auto_refresh_var.get()
        logger.info(f"Auto-refresh {'enabled' if self.auto_refresh else 'disabled'}")
    
    # Display update methods
    def update_status(self, status, color="black"):
        self.status_label.config(text=status, foreground=color)
        self.connected = "Connected" in status
        if self.connected:
            self.connect_button.config(text="🔌 Disconnect")
        else:
            self.connect_button.config(text="🔌 Connect")
    
    def update_display(self):
        try:
            # Update timestamp
            if self.last_update:
                self.update_label.config(text=self.last_update.strftime('%H:%M:%S'))
            
            # Update statistics
            if self.connection_stats:
                active = self.connection_stats.get('activeConnections', 0)
                total = self.connection_stats.get('totalConnections', 0)
                sos_count = self.connection_stats.get('totalSOS', 0)
                
                self.active_conn_label.config(text=f"🟢 Active: {active}")
                self.total_conn_label.config(text=f"📊 Total: {total}")
                self.sos_count_label.config(text=f"🚨 SOS: {sos_count}")
                self.efir_count_label.config(text=f"📋 E-FIR: {len(self.efir_reports)}")
            
            # Update SOS display
            self.update_sos_display()
            
            # Update users display
            self.update_users_display()
            
            # Update E-FIR display
            self.update_efir_display()
            
            # Update tracking display
            self.update_tracking_display()
            
            # Update analytics
            self.update_analytics_display()
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    def update_sos_display(self):
        # Clear existing items
        for item in self.sos_tree.get_children():
            self.sos_tree.delete(item)
        
        # Update summary
        sos_count = len(self.sos_signals)
        if sos_count == 0:
            self.sos_summary_label.config(text="✅ No active SOS signals", foreground="green")
        else:
            self.sos_summary_label.config(text=f"🚨 {sos_count} ACTIVE SOS SIGNALS - IMMEDIATE ATTENTION REQUIRED!", foreground="red")
        
        # Add SOS signals
        for i, signal in enumerate(self.sos_signals):
            # Determine priority
            help_type = signal.get('help_type', 'general')
            if help_type in ['ambulance', 'fire']:
                priority = "🔴 CRITICAL"
            elif help_type == 'police':
                priority = "🟠 HIGH"
            else:
                priority = "🟡 MEDIUM"
            
            # Format time
            sos_time = self.parse_datetime(signal.get('sos_time'))
            time_ago = self.format_timedelta(sos_time)
            
            # Format ETA
            eta = signal.get('eta', 'N/A')
            eta_text = f"{eta} min" if eta != 'N/A' else 'N/A'
            
            # Insert row
            item = self.sos_tree.insert('', 'end', values=(
                priority,
                signal.get('name', 'Unknown'),
                signal.get('location', 'Unknown'),
                signal.get('help_type', 'General').title(),
                time_ago,
                eta_text,
                signal.get('status', 'Active').upper(),
                signal.get('phone', 'N/A')
            ))
            
            # Color coding
            if help_type in ['ambulance', 'fire']:
                self.sos_tree.set(item, 'priority', '🔴 CRITICAL')
            elif help_type == 'police':
                self.sos_tree.set(item, 'priority', '🟠 HIGH')
    
    def update_users_display(self):
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Update summary
        user_count = len([u for u in self.connected_users if u.get('client_type') != 'dashboard'])
        dashboard_count = len([u for u in self.connected_users if u.get('client_type') == 'dashboard'])
        
        self.users_summary_label.config(
            text=f"👥 {user_count} Users Connected | 🖥️ {dashboard_count} Dashboards Online"
        )
        
        # Add users
        for user in self.connected_users:
            # Status icon
            if user.get('client_type') == 'dashboard':
                status_icon = "🖥️"
            else:
                has_sos = any(s.get('aadhaar_id') == user.get('aadhaar_id') for s in self.sos_signals)
                status_icon = "🚨" if has_sos else "🟢"
            
            # Connected time
            connected_time = self.parse_datetime(user.get('connected_at'))
            uptime = self.format_timedelta(connected_time)
            
            # SOS status
            has_sos = any(s.get('aadhaar_id') == user.get('aadhaar_id') for s in self.sos_signals)
            sos_status = "🚨 ACTIVE SOS" if has_sos else "✅ Normal"
            
            # Tracking status
            tracking = user.get('real_time_tracking', False)
            tracking_text = "🟢 Enabled" if tracking else "🔴 Disabled"
            
            self.users_tree.insert('', 'end', values=(
                status_icon,
                user.get('name', 'Unknown'),
                user.get('client_type', 'user').title(),
                user.get('location', 'Unknown'),
                user.get('language', 'en').upper(),
                uptime,
                tracking_text,
                sos_status
            ))
    
    def update_efir_display(self):
        # Clear existing items
        for item in self.efir_tree.get_children():
            self.efir_tree.delete(item)
        
        # Update summary
        efir_count = len(self.efir_reports)
        if efir_count == 0:
            self.efir_summary_label.config(text="📋 No E-FIR reports filed")
        else:
            self.efir_summary_label.config(text=f"📋 {efir_count} E-FIR Reports Filed")
        
        # Add E-FIR reports
        for efir in self.efir_reports:
            # Priority based on incident type
            incident_type = efir.get('incident_type', 'Unknown')
            if incident_type.lower() in ['theft', 'robbery', 'assault']:
                priority = "🔴 HIGH"
            elif incident_type.lower() in ['fraud', 'harassment']:
                priority = "🟠 MEDIUM"
            else:
                priority = "🟡 LOW"
            
            # Format time
            efir_time = self.parse_datetime(efir.get('timestamp'))
            time_ago = self.format_timedelta(efir_time)
            
            self.efir_tree.insert('', 'end', values=(
                priority,
                efir.get('user_name', 'Unknown'),
                incident_type,
                efir.get('location', 'Unknown'),
                time_ago,
                efir.get('status', 'Filed').upper(),
                efir.get('efir_id', 'N/A')[:8] + "..."  # Shortened ID
            ))
    
    def update_tracking_display(self):
        # Clear existing items
        for item in self.tracking_tree.get_children():
            self.tracking_tree.delete(item)
        
        # Add tracking data for users with real-time tracking
        for user in self.connected_users:
            if user.get('client_type') != 'dashboard':
                # Status
                has_sos = any(s.get('aadhaar_id') == user.get('aadhaar_id') for s in self.sos_signals)
                status = "🚨" if has_sos else "🟢"
                
                # Coordinates
                coords = user.get('coordinates', {})
                coord_text = f"{coords.get('lat', 'N/A')}, {coords.get('lng', 'N/A')}" if coords else "N/A"
                
                # Last update
                last_seen = self.parse_datetime(user.get('last_seen', user.get('connected_at')))
                last_update = self.format_timedelta(last_seen)
                
                # Tracking enabled
                tracking = user.get('real_time_tracking', False)
                tracking_text = "🟢 ON" if tracking else "🔴 OFF"
                
                # Movement (simulated)
                movement = "🚶 Moving" if tracking else "⏸️ Static"
                
                self.tracking_tree.insert('', 'end', values=(
                    status,
                    user.get('name', 'Unknown'),
                    user.get('location', 'Unknown'),
                    coord_text,
                    last_update,
                    tracking_text,
                    movement
                ))
    
    def update_analytics_display(self):
        # Generate analytics text
        analytics_text = f"""
🚨 ENHANCED TOURIST SAFETY DASHBOARD - SYSTEM ANALYTICS
{'='*80}

📊 SYSTEM OVERVIEW
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Server Status: {'🟢 Online' if self.connected else '🔴 Offline'}
Auto Refresh: {'🟢 Enabled' if self.auto_refresh else '🔴 Disabled'}

📈 CONNECTION STATISTICS
Total Connections: {self.connection_stats.get('totalConnections', 0)}
Active Connections: {self.connection_stats.get('activeConnections', 0)}
Total SOS Signals: {self.connection_stats.get('totalSOS', 0)}
Total E-FIR Reports: {len(self.efir_reports)}

👥 USER BREAKDOWN
Connected Users: {len([u for u in self.connected_users if u.get('client_type') != 'dashboard'])}
Active Dashboards: {len([u for u in self.connected_users if u.get('client_type') == 'dashboard'])}
Users with Tracking: {len([u for u in self.connected_users if u.get('real_time_tracking')])}

🚨 EMERGENCY OVERVIEW
Active SOS Signals: {len(self.sos_signals)}
"""
        
        # Add SOS breakdown
        if self.sos_signals:
            analytics_text += "\n🚑 SOS BREAKDOWN BY TYPE:\n"
            sos_types = {}
            for sos in self.sos_signals:
                help_type = sos.get('help_type', 'general')
                sos_types[help_type] = sos_types.get(help_type, 0) + 1
            
            for help_type, count in sos_types.items():
                analytics_text += f"  {help_type.title()}: {count}\n"
        
        # Add E-FIR breakdown
        if self.efir_reports:
            analytics_text += "\n📋 E-FIR BREAKDOWN BY TYPE:\n"
            efir_types = {}
            for efir in self.efir_reports:
                incident_type = efir.get('incident_type', 'Unknown')
                efir_types[incident_type] = efir_types.get(incident_type, 0) + 1
            
            for incident_type, count in efir_types.items():
                analytics_text += f"  {incident_type}: {count}\n"
        
        # Add language breakdown
        if self.connected_users:
            analytics_text += "\n🌐 LANGUAGE DISTRIBUTION:\n"
            languages = {}
            for user in self.connected_users:
                if user.get('client_type') != 'dashboard':
                    lang = user.get('language', 'en')
                    languages[lang] = languages.get(lang, 0) + 1
            
            for lang, count in languages.items():
                analytics_text += f"  {lang.upper()}: {count}\n"
        
        analytics_text += f"\n{'='*80}\n"
        
        # Update analytics display
        self.analytics_text.delete(1.0, tk.END)
        self.analytics_text.insert(1.0, analytics_text)
    
    # Utility methods
    def parse_datetime(self, dt_string):
        try:
            if isinstance(dt_string, str):
                if 'Z' in dt_string:
                    return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
                else:
                    return datetime.fromisoformat(dt_string)
            return dt_string
        except (ValueError, TypeError):
            return datetime.now()
    
    def format_timedelta(self, dt):
        if not isinstance(dt, datetime):
            return "Unknown"
            
        now = datetime.now(timezone.utc) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        if diff.total_seconds() < 60:
            return f"{int(diff.total_seconds())}s ago"
        elif diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() / 60)}m ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            minutes = int((diff.total_seconds() % 3600) / 60)
            return f"{hours}h {minutes}m ago"
        else:
            days = int(diff.total_seconds() / 86400)
            hours = int((diff.total_seconds() % 86400) / 3600)
            return f"{days}d {hours}h ago"
    
    # Action methods
    def manual_refresh(self):
        logger.info("Manual refresh triggered")
        self.update_display()
        messagebox.showinfo("Refresh", "Dashboard data refreshed successfully!")
    
    def resolve_sos(self):
        selection = self.sos_tree.selection()
        if selection:
            messagebox.showinfo("SOS Resolved", "✅ Selected SOS has been marked as resolved")
        else:
            messagebox.showwarning("No Selection", "Please select an SOS signal to resolve")
    
    def dispatch_help(self):
        selection = self.sos_tree.selection()
        if selection:
            messagebox.showinfo("Help Dispatched", "🚑 Emergency help has been dispatched to the location")
        else:
            messagebox.showwarning("No Selection", "Please select an SOS signal to dispatch help")
    
    def update_eta(self):
        selection = self.sos_tree.selection()
        if selection:
            new_eta = tk.simpledialog.askinteger("Update ETA", "Enter new ETA in minutes:", minvalue=1, maxvalue=120)
            if new_eta:
                messagebox.showinfo("ETA Updated", f"⏱️ ETA updated to {new_eta} minutes")
    
    def contact_user(self):
        selection = self.sos_tree.selection()
        if selection:
            messagebox.showinfo("Contact User", "📞 Contacting user via emergency services")
        else:
            messagebox.showwarning("No Selection", "Please select a user to contact")
    
    def clear_sos(self):
        if messagebox.askyesno("Clear SOS", "Are you sure you want to clear all SOS signals?"):
            for item in self.sos_tree.get_children():
                self.sos_tree.delete(item)
            messagebox.showinfo("Cleared", "🗑️ All SOS signals cleared from display")
    
    def export_data(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                data = {
                    'export_timestamp': datetime.now().isoformat(),
                    'sos_signals': self.sos_signals,
                    'efir_reports': self.efir_reports,
                    'connected_users': self.connected_users,
                    'connection_stats': self.connection_stats
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Export Complete", f"📤 Data exported successfully to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data:\n{e}")
    
    def show_map(self):
        messagebox.showinfo("Map View", "🗺️ Interactive map would open here showing user locations and SOS signals")
    
    def show_analytics(self):
        messagebox.showinfo("Analytics", "📈 Advanced analytics charts would be displayed here")
    
    def show_settings(self):
        messagebox.showinfo("Settings", "⚙️ Dashboard settings and configuration panel would open here")
    
    def refresh_tracking(self):
        self.update_display()
        messagebox.showinfo("Tracking Refreshed", "📍 Location tracking data has been refreshed")
    
    def show_tracking_map(self):
        messagebox.showinfo("Tracking Map", "🗺️ Real-time tracking map would open here")
    
    def generate_report(self):
        messagebox.showinfo("Report Generated", "📊 Comprehensive system report has been generated")
    
    def show_charts(self):
        messagebox.showinfo("Charts", "📈 Statistical charts and graphs would be displayed here")
    
    def on_efir_select(self, event):
        selection = self.efir_tree.selection()
        if selection:
            item = self.efir_tree.item(selection[0])
            values = item['values']
            if values and len(values) > 6:
                # Find the full E-FIR data
                efir_id_partial = values[6]  # Reference column (partial)
                for efir in self.efir_reports:
                    if efir.get('efir_id', '').startswith(efir_id_partial.replace('...', '')):
                        details = f"""
📋 E-FIR DETAILED REPORT
{'='*50}

🔢 Reference ID: {efir.get('efir_id', 'N/A')}
👤 Filed By: {efir.get('user_name', 'Unknown')}
📋 Incident Type: {efir.get('incident_type', 'Unknown')}
📍 Location: {efir.get('location', 'Unknown')}
⏰ Filed Time: {efir.get('timestamp', 'Unknown')}
📊 Status: {efir.get('status', 'Filed')}

📝 INCIDENT DESCRIPTION:
{efir.get('description', 'No description provided')}

🗺️ COORDINATES:
{efir.get('coordinates', 'Not provided')}

{'='*50}
                        """
                        
                        self.efir_details.delete(1.0, tk.END)
                        self.efir_details.insert(1.0, details.strip())
                        break
    
    def on_closing(self):
        logger.info("Dashboard closing...")
        self.disconnect()
        self.root.destroy()
    
    def run(self):
        logger.info("Starting Improved Tourist Safety Dashboard...")
        
        def try_connect():
            time.sleep(1)
            if not self.connect():
                logger.error("Failed to connect to server.")
                self.root.after(0, lambda: messagebox.showerror(
                    "Connection Error", 
                    "Could not establish connection to server.\n\nPlease ensure the server is running and try again."
                ))
        
        threading.Thread(target=try_connect, daemon=True).start()
        self.root.mainloop()

def main():
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Enhanced server is running. Starting improved dashboard...")
        else:
            print("⚠️ Server returned error. Starting dashboard anyway...")
    except requests.exceptions.RequestException:
        print("⚠️ Warning: Cannot reach server. Starting dashboard in offline mode...")
    
    root = tk.Tk()
    app = ImprovedDashboardUI(root)
    app.run()

if __name__ == "__main__":
    main()