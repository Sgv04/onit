import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QPushButton)
from PyQt6.QtCore import Qt
from models import Device, Session, init_db

# --- ОКОННОЕ ПРИЛОЖЕНИЕ (ЛР1-2) ---
class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Inventory (CRUD)")
        self.setMinimumSize(700, 450)
        self.session = Session()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        self.host_input = QLineEdit(placeholderText="Hostname")
        self.ip_input = QLineEdit(placeholderText="IP Address")
        self.type_input = QLineEdit(placeholderText="Type (Router/Switch)")
        input_layout.addWidget(self.host_input)
        input_layout.addWidget(self.ip_input)
        input_layout.addWidget(self.type_input)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить устройство")
        add_btn.clicked.connect(self.add_device)
        delete_btn = QPushButton("Удалить выбранное")
        delete_btn.clicked.connect(self.delete_device)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Hostname", "IP Address", "Device Type"])
        self.table.itemChanged.connect(self.update_device)

        layout.addLayout(input_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_data(self):
        self.table.blockSignals(True) 
        self.table.setRowCount(0)
        devices = self.session.query(Device).all()
        for i, device in enumerate(devices):
            self.table.insertRow(i)
            id_item = QTableWidgetItem(str(device.id))
            id_item.setFlags(id_item.flags() ^ Qt.ItemFlag.ItemIsEditable) 
            self.table.setItem(i, 0, id_item)
            self.table.setItem(i, 1, QTableWidgetItem(device.hostname))
            self.table.setItem(i, 2, QTableWidgetItem(device.ip_address))
            self.table.setItem(i, 3, QTableWidgetItem(device.device_type))
        self.table.blockSignals(False)

    def add_device(self):
        if not self.host_input.text(): return
        new_device = Device(
            hostname=self.host_input.text(),
            ip_address=self.ip_input.text(),
            device_type=self.type_input.text()
        )
        self.session.add(new_device)
        self.session.commit()
        self.load_data()
        self.host_input.clear()
        self.ip_input.clear()
        self.type_input.clear()

    def update_device(self, item):
        row, col = item.row(), item.column()
        device_id = int(self.table.item(row, 0).text())
        device = self.session.query(Device).filter(Device.id == device_id).first()
        if device:
            if col == 1: device.hostname = item.text()
            elif col == 2: device.ip_address = item.text()
            elif col == 3: device.device_type = item.text()
            self.session.commit()

    def delete_device(self):
        current_row = self.table.currentRow()
        if current_row < 0: return
        device_id = int(self.table.item(current_row, 0).text())
        device = self.session.query(Device).filter(Device.id == device_id).first()
        if device:
            self.session.delete(device)
            self.session.commit()
            self.load_data()

# --- ТОЧКА ВХОДА ---
if __name__ == "__main__":
    init_db()

    if os.getenv("RUN_MODE") == "WEB":
        import uvicorn
        from fastapi import FastAPI

        web_app = FastAPI()

        #endpoint 
        @web_app.get("/health")
        def health():
            return {
                "status": "ok",
                "service": "inventory-api"
            }

        # главный endpoint 
        @web_app.get("/")
        def read_root():
            return {
                "status": "DEPLOY OK 🚀",
                "node_name": os.getenv("HOSTNAME"),
                "mode": "WEB",
                "version": "1.0-cicd-test"
            }

        #безопасное получение данных (исправленная версия)
        @web_app.get("/devices")
        def get_all_devices():
            session = Session()
            try:
                devices = session.query(Device).all()
                return [
                    {
                        "id": d.id,
                        "hostname": d.hostname,
                        "ip": d.ip_address,
                        "type": d.device_type
                    }
                    for d in devices
                ]
            finally:
                session.close()

        print("Запуск WEB-сервера (FastAPI) для Docker...")
        uvicorn.run(web_app, host="0.0.0.0", port=8000)

    else:
        print("Запуск GUI (PyQt6)...")
        app = QApplication(sys.argv)
        window = InventoryApp()
        window.show()
        sys.exit(app.exec())