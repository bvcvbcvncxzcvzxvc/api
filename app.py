import sys, time, random, urllib.parse, asyncio, os
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWidgets import (QApplication, QDialog, QLabel, QVBoxLayout, QHBoxLayout, 
                             QProgressBar, QLineEdit, QPushButton, QMessageBox, QMainWindow, QWidget, QTextEdit)
from PyQt6.QtGui import QDesktopServices, QFont

# ---------------------------
# Environment Variables Setup
# ---------------------------
# These values should be set in your Render dashboard
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
TELEGRAM_NUMERIC_ID = int(os.environ.get("TELEGRAM_NUMERIC_ID", "0"))
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# ---------------------------
# TELETHON CLIENT SETUP
# ---------------------------
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

# Create a global event loop for Telethon (PyQt uses its own loop)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Create the Telethon client using environment variables
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)
else:
    client = TelegramClient("my_session", API_ID, API_HASH, loop=loop)

async def ensure_telethon_auth():
    """
    Ensures that the Telethon client is authorized.
    The first time you run this, you will be prompted in the console.
    """
    await client.connect()
    if not await client.is_user_authorized():
        print("Telethon: Please log in to Telegram.")
        phone = input("Phone number (international format): ")
        await client.send_code_request(phone)
        code = input("Enter the code you received: ")
        try:
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            password = input("Two-step verification password: ")
            await client.sign_in(password=password)
    print("Telethon is authorized.")

async def send_telegram_message(message_text: str):
    """
    Sends a message via Telethon to the numeric user ID.
    """
    await ensure_telethon_auth()
    await client.send_message(TELEGRAM_NUMERIC_ID, message_text)
    print("Message sent successfully to numeric ID:", TELEGRAM_NUMERIC_ID)

# ---------------------------
# Stage 1: Splash Screen (15 seconds)
# ---------------------------
class SplashScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #1e1e1e;")
        self.setFixedSize(500, 300)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel("Loading Ultra License Checker...")
        self.label.setStyleSheet("color: #61dafb;")
        self.label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setFixedWidth(400)
        self.progress.setMaximum(100)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
        # Increase progress over 15 seconds (15000 ms)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        self.timer.start(15000 // 100)
    
    def update_progress(self):
        self.progress_value += 1
        self.progress.setValue(self.progress_value)
        if self.progress_value >= 100:
            self.timer.stop()
            self.accept()

# ---------------------------
# Stage 2: License Entry Window
# ---------------------------
class LicenseWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("License")
        self.setFixedSize(400, 200)
        self.setStyleSheet("background-color: #282c34; color: white;")
        self.license_code = ""
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel("Enter your 12-digit license key:")
        label.setFont(QFont("Helvetica", 14))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self.licenseEdit = QLineEdit()
        self.licenseEdit.setMaxLength(12)
        self.licenseEdit.setFont(QFont("Helvetica", 14))
        self.licenseEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.licenseEdit.setPlaceholderText("Enter 12 digits")
        layout.addWidget(self.licenseEdit)
        
        self.verifyBtn = QPushButton("Verify")
        self.verifyBtn.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        self.verifyBtn.setStyleSheet("background-color: #61dafb; color: #282c34;")
        self.verifyBtn.clicked.connect(self.check_license)
        layout.addWidget(self.verifyBtn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
    
    def check_license(self):
        code = self.licenseEdit.text().strip()
        if len(code) != 12 or not code.isdigit():
            QMessageBox.critical(self, "Error", "License key must be exactly 12 digits!")
            return
        self.license_code = code
        self.accept()

# ---------------------------
# Stage 3: License Processing Window (15 seconds)
# ---------------------------
class ProcessingWindow(QDialog):
    def __init__(self, license_code):
        super().__init__()
        self.license_code = license_code
        self.setWindowTitle("Processing License")
        self.setFixedSize(500, 300)
        self.setStyleSheet("background-color: #1e1e1e; color: #61dafb;")
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel("Verifying your license...\nPlease wait.")
        label.setFont(QFont("Helvetica", 16, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self.progress = QProgressBar()
        self.progress.setFixedWidth(400)
        self.progress.setMaximum(100)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
        self.progress_value = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(15000 // 100)
    
    def update_progress(self):
        self.progress_value += 1
        self.progress.setValue(self.progress_value)
        if self.progress_value >= 100:
            self.timer.stop()
            self.accept()

# ---------------------------
# Stage 4: Verify Product & Send Telegram Message via Telethon
# ---------------------------
class VerifyProductWindow(QDialog):
    def __init__(self, license_code):
        super().__init__()
        self.license_code = license_code
        self.setWindowTitle("Verify Product")
        self.setFixedSize(400, 200)
        self.setStyleSheet("background-color: #282c34; color: white;")
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel("Verifying product and sending code to Telegram...")
        label.setFont(QFont("Helvetica", 14))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)
        # After 3 seconds, send the message using Telethon
        QTimer.singleShot(3000, self.send_via_telethon)
    
    def send_via_telethon(self):
        message_text = f"Your license code is {self.license_code}"
        
        async def do_send():
            try:
                await send_telegram_message(message_text)
                QMessageBox.information(self, "Response", "License code verified")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to send message:\n{e}")
                self.reject()
        
        loop.create_task(do_send())

# ---------------------------
# Stage 5: Main Window (Hacking Simulator)
# ---------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WhatsApp Hack Vulnerability")
        self.setFixedSize(600, 500)
        self.setStyleSheet("background-color: black;")
        self.initUI()
    
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Phone number input section
        phone_layout = QHBoxLayout()
        phone_label = QLabel("Enter your phone number:")
        phone_label.setStyleSheet("color: #00FF00;")
        phone_label.setFont(QFont("Courier", 12))
        self.phoneEdit = QLineEdit()
        self.phoneEdit.setFont(QFont("Courier", 12))
        self.phoneEdit.setStyleSheet("background-color: black; color: #00FF00;")
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phoneEdit)
        layout.addLayout(phone_layout)
        
        # Buttons for simulated operations
        btn_layout = QHBoxLayout()
        self.btnExtractInfo = QPushButton("Extract Info")
        self.btnExtractCallLog = QPushButton("Extract Call Log")
        self.btnExtractLocation = QPushButton("Extract Location")
        for btn in (self.btnExtractInfo, self.btnExtractCallLog, self.btnExtractLocation):
            btn.setFont(QFont("Courier", 12))
            btn.setStyleSheet("background-color: #00FF00; color: black;")
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)
        
        # Log window
        self.logText = QTextEdit()
        self.logText.setFont(QFont("Courier", 12))
        self.logText.setStyleSheet("background-color: black; color: #00FF00;")
        layout.addWidget(self.logText)
        
        central_widget.setLayout(layout)
        
        # Connect buttons to simulated operations
        self.btnExtractInfo.clicked.connect(lambda: self.simulate_operation("Extracting detailed information..."))
        self.btnExtractCallLog.clicked.connect(lambda: self.simulate_operation("Extracting call logs..."))
        self.btnExtractLocation.clicked.connect(lambda: self.simulate_operation("Extracting location data..."))
    
    def simulate_operation(self, operation_text):
        messages = [
            f"{operation_text}",
            "Initializing secure connection...",
            "Decrypting data packets...",
            "Fetching records from server...",
            "Performing advanced algorithm calculations...",
            "Error: API rate limit exceeded, retrying...",
            "Data extraction complete."
        ]
        self.logText.append("\n--------------------------")
        for msg in messages:
            self.logText.append(msg)
            QApplication.processEvents()
            time.sleep(random.uniform(0.5, 1.5))
        self.logText.append("--------------------------\n")

# ---------------------------
# MAIN EXECUTION
# ---------------------------
def main():
    # Start Telethon client authentication (will prompt in console if needed)
    loop.run_until_complete(ensure_telethon_auth())
    
    app = QApplication(sys.argv)
    
    # Stage 1: Splash Screen
    splash = SplashScreen()
    if splash.exec() == QDialog.DialogCode.Accepted:
        # Stage 2: License Entry Window
        license_win = LicenseWindow()
        if license_win.exec() == QDialog.DialogCode.Accepted:
            license_code = license_win.license_code
            # Stage 3: License Processing Window
            processing = ProcessingWindow(license_code)
            if processing.exec() == QDialog.DialogCode.Accepted:
                # Stage 4: Verify Product & Send Telegram Message
                verify_product = VerifyProductWindow(license_code)
                if verify_product.exec() == QDialog.DialogCode.Accepted:
                    # Stage 5: Main Window (Hacking Simulator)
                    main_win = MainWindow()
                    main_win.show()
                    sys.exit(app.exec())
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
