import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QComboBox, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QFileDialog, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt
import pandas as pd
from datetime import datetime
from transcript_generator import TranscriptGenerator

class TranscriptUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.courses = []
        
    def initUI(self):
        self.setWindowTitle('Transkript Oluşturucu')
        self.setGeometry(100, 100, 1000, 800)
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Öğrenci Bilgileri Bölümü
        student_info_group = QGroupBox("Öğrenci Bilgileri")
        student_info_layout = QVBoxLayout()
        student_info_group.setLayout(student_info_layout)
        
        # Öğrenci bilgileri form alanları
        self.student_fields = {}
        fields = [
            ('name', 'Öğrenci Adı Soyadı:'),
            ('student_id', 'Öğrenci Numarası:'),
            ('faculty', 'Fakülte:'),
            ('department', 'Bölüm:'),
            ('program', 'Program:'),
            ('start_year', 'Öğrenim Başlangıç Yılı:')
        ]
        
        for field_name, label_text in fields:
            row = QHBoxLayout()
            label = QLabel(label_text)
            line_edit = QLineEdit()
            row.addWidget(label)
            row.addWidget(line_edit)
            self.student_fields[field_name] = line_edit
            student_info_layout.addLayout(row)
            
        main_layout.addWidget(student_info_group)
        
        # Sistem Seçenekleri Bölümü
        system_group = QGroupBox("Sistem Seçenekleri")
        system_layout = QVBoxLayout()
        system_group.setLayout(system_layout)
        
        # Kredi Sistemi
        credit_group = QGroupBox("Kredi Sistemi")
        credit_layout = QHBoxLayout()
        self.credit_checkbox = QCheckBox("Kredi sistemini kullan")
        credit_layout.addWidget(self.credit_checkbox)
        credit_group.setLayout(credit_layout)
        system_layout.addWidget(credit_group)
        
        # Not Sistemi
        grade_group = QGroupBox("Not Sistemi")
        grade_layout = QVBoxLayout()
        
        self.grade_systems = {
            'letter': QCheckBox("Harf Notu (AA, BA, BB, ...)"),
            'five': QCheckBox("5'lik Sistem (1-5)"),
            'ten': QCheckBox("10'luk Sistem (1-10)"),
            'hundred': QCheckBox("100'lük Sistem (0-100)")
        }
        
        for checkbox in self.grade_systems.values():
            grade_layout.addWidget(checkbox)
            checkbox.stateChanged.connect(self.on_grade_system_change)
            
        grade_group.setLayout(grade_layout)
        system_layout.addWidget(grade_group)
        
        main_layout.addWidget(system_group)
        
        # Butonlar
        button_group = QHBoxLayout()
        
        generate_template_btn = QPushButton("Excel Şablonu Oluştur")
        generate_template_btn.clicked.connect(self.generate_template)
        button_group.addWidget(generate_template_btn)
        
        import_excel_btn = QPushButton("Excel'den İçe Aktar")
        import_excel_btn.clicked.connect(self.import_excel)
        button_group.addWidget(import_excel_btn)
        
        generate_transcript_btn = QPushButton("Transkript Oluştur")
        generate_transcript_btn.clicked.connect(self.generate_transcript)
        button_group.addWidget(generate_transcript_btn)
        
        main_layout.addLayout(button_group)
        
        # Ders Listesi Tablosu
        self.course_table = QTableWidget()
        self.update_table_headers()
        main_layout.addWidget(self.course_table)

    def on_grade_system_change(self):
        sender = self.sender()
        if sender.isChecked():
            for checkbox in self.grade_systems.values():
                if checkbox != sender:
                    checkbox.setChecked(False)
        self.update_table_headers()
        
    def update_table_headers(self):
        headers = ["Yarıyıl", "Ders Kodu", "Ders Adı"]
        
        if self.credit_checkbox.isChecked():
            headers.append("Kredi")
            
        for system, checkbox in self.grade_systems.items():
            if checkbox.isChecked():
                if system == 'letter':
                    headers.append("Harf Notu")
                elif system == 'five':
                    headers.append("Not (5)")
                elif system == 'ten':
                    headers.append("Not (10)")
                elif system == 'hundred':
                    headers.append("Not (100)")
                break
                
        self.course_table.setColumnCount(len(headers))
        self.course_table.setHorizontalHeaderLabels(headers)
        
    def get_selected_grade_system(self):
        for system, checkbox in self.grade_systems.items():
            if checkbox.isChecked():
                return system
        return None
        
    def generate_template(self):
        if not any(checkbox.isChecked() for checkbox in self.grade_systems.values()):
            QMessageBox.warning(self, "Hata", "Lütfen bir not sistemi seçin!")
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Excel Şablonu Kaydet", "", "Excel Files (*.xlsx)")
            
        if file_name:
            headers = ["Yarıyıl", "Ders Kodu", "Ders Adı"]
            example_data = [
                ["1", "MAT101", "Matematik I"],
                ["1", "FİZ101", "Fizik I"],
                ["2", "MAT102", "Matematik II"]
            ]
            
            if self.credit_checkbox.isChecked():
                headers.append("Kredi")
                for row in example_data:
                    row.append("3")
                    
            grade_system = self.get_selected_grade_system()
            if grade_system:
                if grade_system == 'letter':
                    headers.append("Harf Notu")
                    grade_example = "BB"
                elif grade_system == 'five':
                    headers.append("Not (5)")
                    grade_example = "3"
                elif grade_system == 'ten':
                    headers.append("Not (10)")
                    grade_example = "7"
                elif grade_system == 'hundred':
                    headers.append("Not (100)")
                    grade_example = "75"
                    
                for row in example_data:
                    row.append(grade_example)
                    
            df = pd.DataFrame(example_data, columns=headers)
            
            try:
                writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Dersler', index=False)
                
                worksheet = writer.sheets['Dersler']
                
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    ) + 2
                    worksheet.set_column(idx, idx, max_length)
                
                header_format = writer.book.add_format({
                    'bold': True,
                    'bg_color': '#D3D3D3',
                    'border': 1
                })
                
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                writer.close()
                
                QMessageBox.information(
                    self, "Başarılı", 
                    "Excel şablonu oluşturuldu! Şablonu doldurup içe aktarabilirsiniz."
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Hata", 
                    f"Excel şablonu oluşturulurken hata: {str(e)}"
                )

    def import_excel(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Files (*.xlsx *.xls)")
        if file_name:
            try:
                df = pd.read_excel(file_name)
                self.course_table.setRowCount(0)
                self.course_table.setColumnCount(len(df.columns))
                self.course_table.setHorizontalHeaderLabels(df.columns)
                
                for idx, row in df.iterrows():
                    row_position = self.course_table.rowCount()
                    self.course_table.insertRow(row_position)
                    for col, value in enumerate(row):
                        self.course_table.setItem(
                            row_position, col, QTableWidgetItem(str(value)))
                            
                QMessageBox.information(
                    self, "Başarılı", "Veriler başarıyla içe aktarıldı!")
            except Exception as e:
                QMessageBox.warning(
                    self, "Hata", f"Excel dosyası yüklenirken hata: {str(e)}")
                
    def generate_transcript(self):
        if self.course_table.rowCount() == 0:
            QMessageBox.warning(self, "Hata", "Lütfen önce ders verilerini yükleyin!")
            return
            
        # Öğrenci bilgilerinin kontrolü
        for field, widget in self.student_fields.items():
            if not widget.text().strip():
                QMessageBox.warning(self, "Hata", f"Lütfen {field} alanını doldurun!")
                return
        
        # Not sistemi kontrolü
        grade_system = self.get_selected_grade_system()
        if not grade_system:
            QMessageBox.warning(self, "Hata", "Lütfen bir not sistemi seçin!")
            return
            
        transcript = TranscriptGenerator()
        
        # Öğrenci bilgilerini ekle
        student_info = {
            field: widget.text()
            for field, widget in self.student_fields.items()
        }
        transcript.add_student_info(**student_info)
        
        # Sistem bilgilerini ekle
        transcript.set_system_info(grade_system, self.credit_checkbox.isChecked())
        
        # Dersleri ekle
        try:
            for row in range(self.course_table.rowCount()):
                semester = self.course_table.item(row, 0).text()
                semester_num = int(semester.split('.')[0] if '.' in semester else semester)
                
                course_data = {
                    'semester': semester_num,
                    'course_code': self.course_table.item(row, 1).text(),
                    'course_name': self.course_table.item(row, 2).text()
                }
                
                col_index = 3
                if self.credit_checkbox.isChecked():
                    course_data['credits'] = float(self.course_table.item(row, col_index).text())
                    col_index += 1
                    
                course_data['grade'] = self.course_table.item(row, col_index).text()
                    
                transcript.add_course(**course_data)
                
            file_name, _ = QFileDialog.getSaveFileName(
                self, "PDF Kaydet", "", "PDF Files (*.pdf)")
            if file_name:
                try:
                    transcript.generate_pdf(file_name)
                    QMessageBox.information(
                        self, "Başarılı", 
                        "Transkript PDF olarak kaydedildi!"
                    )
                except Exception as e:
                    QMessageBox.warning(
                        self, "Hata", 
                        f"PDF oluşturulurken hata: {str(e)}"
                    )
        except Exception as e:
            QMessageBox.warning(
                self, "Hata", 
                f"Transkript oluşturulurken hata: {str(e)}"
            )

def main():
    app = QApplication(sys.argv)
    ex = TranscriptUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()