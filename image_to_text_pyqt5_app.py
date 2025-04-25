import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QFileDialog, QMessageBox, QLabel, 
                             QStatusBar)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QBuffer, QIODevice
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\PRATIK\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"  # Update this path as needed
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from PyQt5.QtGui import QIcon




class ModernOCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt OCR Tool")
        self.setWindowIcon(QIcon("C:\\Users\\PRATIK\\Desktop\\imagetotext_app\\logo.png"))
        self.setGeometry(100, 100, 800, 600)
        self.setup_style()
        self.initUI()
        self.check_tesseract()
        
    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D2D;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #4A4A4A;
                padding: 8px;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #DCDCDC;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: 8px;
            }
            QLabel {
                color: #DCDCDC;
            }
        """)
        
    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Button panel
        btn_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton("📁 Open Image")
        self.upload_btn.clicked.connect(self.open_image)
        btn_layout.addWidget(self.upload_btn)
        
        self.paste_btn = QPushButton("📋 Paste Screenshot")
        self.paste_btn.clicked.connect(self.paste_screenshot)
        btn_layout.addWidget(self.paste_btn)
        
        self.save_btn = QPushButton("💾 Save Text")
        self.save_btn.clicked.connect(self.save_text)
        btn_layout.addWidget(self.save_btn)

        self.pdf_btn = QPushButton("📄 Export PDF")
        self.pdf_btn.clicked.connect(self.export_pdf)
        btn_layout.addWidget(self.pdf_btn)
        
        layout.addLayout(btn_layout)
        
        # Image preview
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedHeight(200)
        self.image_label.setStyleSheet("background-color: #1E1E1E; border-radius: 4px;")
        layout.addWidget(self.image_label)
        
        # Text output
        self.text_output = QTextEdit()
        self.text_output.setPlaceholderText("Extracted text will appear here...")
        layout.addWidget(self.text_output)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def check_tesseract(self):
        try:
            pytesseract.get_tesseract_version()
        except EnvironmentError:
            QMessageBox.critical(self, "Error", 
                "Tesseract OCR not found!\nPlease install it from https://github.com/UB-Mannheim/tesseract/wiki")
            self.close()

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            try:
                img = Image.open(file_path)
                self.process_image(img)
                self.show_image_preview(img)
                self.status_bar.showMessage("Image processed successfully", 3000)
            except Exception as e:
                self.show_error(f"Failed to process image: {str(e)}")

    def paste_screenshot(self):
        try:
            clipboard = QApplication.clipboard()
            if clipboard.mimeData().hasImage():
                qimage = clipboard.image()
                
                # Convert QImage to PIL Image using QBuffer
                buffer = QBuffer()
                buffer.open(QIODevice.ReadWrite)
                qimage.save(buffer, "PNG")
                pil_img = Image.open(io.BytesIO(buffer.data()))
                buffer.close()
                
                self.process_image(pil_img)
                self.show_image_preview(pil_img)
                self.status_bar.showMessage("Screenshot processed successfully", 3000)
            else:
                self.show_warning("No image found in clipboard")
        except Exception as e:
            self.show_error(f"Failed to paste image: {str(e)}")

    def show_image_preview(self, img):
        img.thumbnail((400, 200))
        qimage = QImage(
            img.tobytes(), 
            img.size[0], 
            img.size[1], 
            QImage.Format_RGB888
        )
        self.image_label.setPixmap(QPixmap.fromImage(qimage))

    def process_image(self, img):
        try:
            text = pytesseract.image_to_string(img)
            self.text_output.setPlainText(text)
        except Exception as e:
            self.show_error(f"OCR processing failed: {str(e)}")

    def save_text(self):
        text = self.text_output.toPlainText()
        if text.strip():
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Text", "", 
                "Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write(text)
                    self.status_bar.showMessage(f"Text saved to {file_path}", 3000)
                except Exception as e:
                    self.show_error(f"Failed to save file: {str(e)}")
        else:
            self.show_warning("No text to save")

    def export_pdf(self):
        text = self.text_output.toPlainText()
        if text.strip():
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export PDF", "",
                "PDF Files (*.pdf);;All Files (*)"
            )
            if file_path:
                try:
                    c = canvas.Canvas(file_path, pagesize=letter)
                    width, height = letter
                    c.setFont("Helvetica", 12)
                    
                    text_lines = text.split('\n')
                    y_position = height - 40
                    
                    for line in text_lines:
                        if y_position < 40:
                            c.showPage()
                            y_position = height - 40
                        c.drawString(40, y_position, line)
                        y_position -= 15
                    
                    c.save()
                    self.status_bar.showMessage(f"PDF exported to {file_path}", 3000)
                except Exception as e:
                    self.show_error(f"Failed to export PDF: {str(e)}")
        else:
            self.show_warning("No text to export")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.status_bar.showMessage("Error occurred", 3000)

    def show_warning(self, message):
        QMessageBox.warning(self, "Warning", message)
        self.status_bar.showMessage("Warning issued", 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernOCRApp()
    window.show()
    sys.exit(app.exec_())