from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QFileDialog, QGroupBox, QLineEdit, QScrollArea, QSizePolicy, QSpacerItem
from PySide6.QtCore import Qt
import os
from log_list import *


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # initialize Log Journal
        self.log_journal = LogJournal()


        self.setWindowTitle("SSH Log Viewer")
        self.resize(800, 600)

        # Create widgets
        self.choose_file_button = QPushButton("Choose File")
        self.log_list_widget = QListWidget()
        self.prev_button = QPushButton("Prev")
        self.next_button = QPushButton("Next")
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)

        # create filter widgets
        self.from_field = QLineEdit()
        self.from_label = QLabel('From')

        self.to_field = QLineEdit()
        self.to_label = QLabel('To')

        self.ip_field = QLineEdit()
        self.ip_label = QLabel('IP:')

        self.filter_btn = QPushButton('Filter')

        # filter layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.from_label)
        filter_layout.addWidget(self.from_field)
        filter_layout.addWidget(self.to_label)
        filter_layout.addWidget(self.to_field)
        filter_layout.addWidget(self.ip_label)
        filter_layout.addWidget(self.ip_field)
        filter_layout.addWidget(self.filter_btn)


        # Create layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.choose_file_button)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)

        # Create detail layout
        detail_layout = QVBoxLayout()

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel('Date: '))
        self.date_field = QLabel('empty')
        # spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # date_layout.addItem(spacer)
        date_layout.addWidget(self.date_field)
        date_layout.setAlignment(Qt.AlignLeft)
        detail_layout.addLayout(date_layout)

        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel('Host: '))
        self.host_field = QLabel('empty')
        host_layout.addWidget(self.host_field)
        host_layout.setAlignment(Qt.AlignLeft)
        detail_layout.addLayout(host_layout)

        pid_layout = QHBoxLayout()
        pid_layout.addWidget(QLabel('PID: '))
        self.pid_field = QLabel('empty')
        pid_layout.addWidget(self.pid_field)
        pid_layout.setAlignment(Qt.AlignLeft)
        detail_layout.addLayout(pid_layout)
        
        event_layout = QHBoxLayout()
        event_layout.addWidget(QLabel('Event: '))
        self.event_field = QLabel('empty')
        event_layout.addWidget(self.event_field)
        event_layout.setAlignment(Qt.AlignLeft)
        detail_layout.addLayout(event_layout)
        
        detail_layout.addWidget(QLabel('IP addresses:'))
        self.log_ips = QListWidget()
        self.log_ips.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.log_ips.setFixedHeight(100)
        detail_layout.addWidget(self.log_ips)


        # create main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel(f"date format: {datetime.strftime(datetime.now(), self.log_journal.date_format)}"))
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.log_list_widget)
        main_layout.addLayout(detail_layout)


        # connecting inputs
        self.choose_file_button.clicked.connect(self.choose_file)
        self.log_list_widget.currentItemChanged.connect(self.show_log_details)
        self.filter_btn.clicked.connect(self.filter_logs)
        self.next_button.clicked.connect(self.show_next_log)
        self.prev_button.clicked.connect(self.show_prev_log)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def choose_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", os.getcwd(), "SSH Log Files (*.log)")
        if filename:
            self.log_journal.read_log_file(filename)
            self.update_log_list_widget(self.log_journal.get_str_log_list())
            self.choose_first_log()
            self.show_log_details()

    def update_log_list_widget(self, new_log_list):
        self.log_list_widget.addItems(new_log_list)

    def choose_first_log(self):
        if len(self.log_journal):
            self.current_log_index = 0
            self.log_list_widget.setCurrentRow(self.current_log_index)
            self.prev_button.setEnabled(False)
        else:
            self.show_invalid_data()

    def show_log_details(self):
        try:
            current_item = self.log_list_widget.currentItem().text()
        except AttributeError:
            self.show_invalid_data()
            return
        if current_item not in self.log_journal:
            self.show_invalid_data()
            return
        ssh_log = self.log_journal.get_log_of_str(current_item)
        if not ssh_log:
            self.show_invalid_data()
            return
        self.date_field.setText(ssh_log.get_date())
        self.event_field.setText(ssh_log.event)
        self.host_field.setText(ssh_log.host)
        self.pid_field.setText(ssh_log.pid)

        self.log_ips.clear()
        ips = ssh_log.get_ipv4s()
        self.log_ips.addItems(ips)

        self.next_button.setEnabled(True)
        self.prev_button.setEnabled(True)
        if self.log_journal.find_log_index(current_item) == 0:
            self.prev_button.setEnabled(False)
        elif self.log_journal.find_log_index(current_item) == self.log_list_widget.count() - 1:
            self.next_button.setEnabled(False)

    def show_invalid_data(self):
        self.date_field.setText('Invalid')
        self.event_field.setText('Invalid')
        self.host_field.setText('Invalid')
        self.pid_field.setText('Invalid')

    def filter_logs(self):
        start_date = self.from_field.text()
        end_date = self.to_field.text()
        ip = self.ip_field.text()

        self.log_list_widget.clear()
        filtered_logs = self.log_journal.return_filtered_logs(start_date=start_date, end_date=end_date, ip=ip)
        self.log_list_widget.addItems(filtered_logs)
        self.choose_first_log()

    def show_prev_log(self):
        if self.current_log_index is not None and self.current_log_index > 0:
            self.current_log_index -= 1
            self.log_list_widget.setCurrentRow(self.current_log_index)
            self.show_log_details()

    def show_next_log(self):
        if self.current_log_index is not None and self.current_log_index < self.log_list_widget.count() -1:
            self.current_log_index += 1
            self.log_list_widget.setCurrentRow(self.current_log_index)
            self.show_log_details()


