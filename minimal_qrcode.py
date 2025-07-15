"""
Minimal QR code implementation for AURACLE bot
Fallback when qrcode is not available
"""
import base64
import io

def generate_qr_text(data: str) -> str:
    """Generate a text-based QR code representation"""
    # Simple ASCII QR code placeholder
    qr_data = f"""
    ┌─────────────────────────────────────┐
    │ ████ ██   ██ ████ ██   ██ ████ ██ │
    │ ██   ██ █ ██   ██ ██ █ ██   ██ ██ │
    │ ████ ██   ██ ████ ██   ██ ████ ██ │
    │                                     │
    │ QR Code for: {data[:20]}...         │
    │                                     │
    │ ████ ██   ██ ████ ██   ██ ████ ██ │
    │ ██   ██ █ ██   ██ ██ █ ██   ██ ██ │
    │ ████ ██   ██ ████ ██   ██ ████ ██ │
    └─────────────────────────────────────┘
    """
    return qr_data

def generate_qr_image_bytes(data: str) -> bytes:
    """Generate QR code image bytes (fallback text representation)"""
    text_qr = generate_qr_text(data)
    return text_qr.encode('utf-8')

class QRCode:
    """Minimal QR code class"""
    
    def __init__(self, data=""):
        self.data = data
    
    def add_data(self, data):
        self.data = data
    
    def make(self):
        pass
    
    def make_image(self):
        return MockImage(self.data)

class MockImage:
    """Mock image class for QR codes"""
    
    def __init__(self, data):
        self.data = data
    
    def save(self, buffer, format="PNG"):
        if hasattr(buffer, 'write'):
            buffer.write(generate_qr_image_bytes(self.data))
        else:
            with open(buffer, 'wb') as f:
                f.write(generate_qr_image_bytes(self.data))