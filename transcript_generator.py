from fpdf import *
from datetime import datetime
import os

class TranscriptGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.student_info = {}
        self.courses = []
        self.grade_system = None
        self.use_credits = None

    def add_student_info(self, **kwargs):
        self.student_info.update(kwargs)

    def add_course(self, course_code=None, semester=None, **course_data):
        course = course_data
        if course_code:
            course['course_code'] = course_code
        if semester:
            course['semester'] = semester
        self.courses.append(course)
        
    def add_courses(self, courses):
        self.courses.extend(courses)

    def set_system_info(self, grade_system, use_credits):
        self.grade_system = grade_system
        self.use_credits = use_credits

    def calculate_gpa(self):
        if not self.use_credits or not self.courses:
            return None

        total_credits = 0
        total_points = 0

        grade_points = {
            'AA': 4.0, 'BA': 3.5, 'BB': 3.0, 'CB': 2.5,
            'CC': 2.0, 'DC': 1.5, 'DD': 1.0, 'FF': 0.0
        }

        for course in self.courses:
            if 'credits' in course and 'grade' in course:
                credits = float(course['credits'])
                grade = course['grade']
                
                if self.grade_system == 'letter':
                    points = grade_points.get(grade, 0)
                elif self.grade_system == 'five':
                    points = float(grade) / 1.25
                elif self.grade_system == 'ten':
                    points = float(grade) / 2.5
                elif self.grade_system == 'hundred':
                    points = float(grade) / 25
                
                total_credits += credits
                total_points += credits * points

        return total_points / total_credits if total_credits > 0 else 0

    def generate_pdf(self, filename):
        class PDF(FPDF):
            def __init__(self):
                super().__init__()
                self.set_auto_page_break(auto=True, margin=15)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                page = f'Sayfa {self.page_no()}/{{nb}}'
                self.cell(0, 10, page, 0, 0, 'C')

        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Başlık
        pdf.cell(0, 10, 'TRANSKRIPT BELGESI', 0, 1, 'C')
        pdf.ln(10)

        # Öğrenci Bilgileri
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Ogrenci Bilgileri', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        info_items = [
            ('Adi Soyadi', 'name'),
            ('Ogrenci No', 'student_id'),
            ('Fakulte', 'faculty'),
            ('Bolum', 'department'),
            ('Program', 'program'),
            ('Ogrenim Baslangic Yili', 'start_year')
        ]

        for label, key in info_items:
            if key in self.student_info:
                value = str(self.student_info[key])
                pdf.cell(0, 8, f'{label}: {value}', 0, 1)
        
        pdf.ln(10)

        # Dersler
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Dersler', 0, 1)
        
        # Tablo başlıkları
        headers = ['Yariyil', 'Ders Kodu', 'Ders Adi']
        if self.use_credits:
            headers.append('Kredi')
        headers.append('Not')
        
        # Sütun genişlikleri
        col_widths = [20, 30, 80]
        if self.use_credits:
            col_widths.extend([20, 20])
        else:
            col_widths.append(20)

        # Tablo başlıkları
        pdf.set_font('Arial', 'B', 10)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1)
        pdf.ln()

        # Tablo içeriği
        pdf.set_font('Arial', '', 10)
        current_semester = None
        
        # Dersleri yarıyıla göre sırala
        sorted_courses = sorted(self.courses, key=lambda x: x['semester'])
        
        for course in sorted_courses:
            if current_semester != course['semester']:
                current_semester = course['semester']
                pdf.ln(5)
                
            pdf.cell(col_widths[0], 8, str(course['semester']), 1)
            pdf.cell(col_widths[1], 8, str(course.get('code', '')), 1)
            pdf.cell(col_widths[2], 8, str(course.get('name', '')), 1)
            
            if self.use_credits:
                pdf.cell(col_widths[3], 8, str(course.get('credits', '')), 1)
            pdf.cell(col_widths[-1], 8, str(course.get('grade', '')), 1)
            pdf.ln()

        # Genel Not Ortalaması
        if self.use_credits:
            pdf.ln(10)
            gpa = self.calculate_gpa()
            if gpa is not None:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f'Genel Not Ortalamasi: {gpa:.2f}', 0, 1)

        # Tarih ve İmza
        pdf.ln(20)
        current_date = datetime.now().strftime('%d/%m/%Y')
        pdf.cell(0, 10, f'Duzenleme Tarihi: {current_date}', 0, 1)
        
        pdf.output(filename)