from fpdf import FPDF
from datetime import datetime
import os

class TranscriptGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.student_info = {}
        self.courses = []
        self.grade_system = None
        self.use_credits = None
        self.use_course_code = None
        self.use_ects = None
        self.semester_courses = {}
        
        # Türkçe karakter desteği için font ayarları
        self.pdf.add_font("Roboto", "", os.path.join(os.path.dirname(__file__), "Roboto-Regular.ttf"))
        self.pdf.add_font("Roboto", "B", os.path.join(os.path.dirname(__file__), "Roboto-Bold.ttf"))

    def add_student_info(self, **kwargs):
        # Varsayılan değerler
        default_values = {
            'name': 'Örnek Öğrenci',
            'student_id': '123456789',
            'faculty': 'Fen-Edebiyat Fakültesi',
            'department': 'Kimya',
            'start_year': '2025',
            'graduation_date': '',
            'dean_name': kwargs.get('dean_name', ''),
            'dean_title': kwargs.get('dean_title', '')
        }
        
        # Boş değerler için varsayılan değerleri kullan
        for key, default_value in default_values.items():
            if key in kwargs and not kwargs[key].strip():
                kwargs[key] = default_value
                
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

    def add_semester_courses(self, semester, courses):
        self.semester_courses[semester] = courses

    def set_system_info(self, grade_system, use_credits, use_course_code=False, use_ects=False):
        self.grade_system = grade_system
        self.use_credits = use_credits
        self.use_course_code = use_course_code
        self.use_ects = use_ects

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
        try:
            # PDF oluştur
            pdf = self.pdf
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=10)
            
            # Logo ekleme
            try:
                logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
                if os.path.exists(logo_path):
                    pdf.image(logo_path, x=10, y=3, w=40)
                else:
                    print(f"Logo dosyası bulunamadı: {logo_path}")
            except Exception as e:
                print(f"Logo yüklenirken hata oluştu: {str(e)}")
            
            # Üniversite adı
            pdf.set_font('Roboto', 'B', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.set_y(8)
            pdf.cell(0, 6, 'İSTANBUL TEKNİK ÜNİVERSİTESİ', 0, 1, 'C')
            
            # Fakülte adı
            pdf.set_font('Roboto', 'B', 8)
            pdf.cell(0, 5, self.student_info.get('faculty', 'FEN EDEBİYAT FAKÜLTESİ'), 0, 1, 'C')
            
            # Belge adı
            pdf.set_font('Roboto', 'B', 8)
            pdf.cell(0, 5, 'TRANSKRİPT BELGESİ', 0, 1, 'C')
            
            # Sadece tarih bilgisi
            pdf.set_font('Roboto', '', 6)
            pdf.set_text_color(80, 80, 80)
            current_time = datetime.now().strftime("%d.%m.%Y")
            pdf.set_xy(pdf.w - 45, 5)
            pdf.cell(35, 4, f'{current_time}', 0, 1, 'R')
            
            # Başlıklar sonrası boşluk
            pdf.ln(25)
            
            # Öğrenci Bilgileri - 3 Kolon halinde
            y_start = pdf.get_y()
            
            student_info = [
                ('Adı Soyadı', self.student_info.get('name', '')),
                ('Öğrenci No', self.student_info.get('student_id', '')),
                ('Fakülte', self.student_info.get('faculty', '')),
                ('Bölüm', self.student_info.get('department', '')),
                ('Mezuniyet Tarihi', self.student_info.get('graduation_date', '')),  # Program yerine Mezuniyet Tarihi
                ('Başlangıç Yılı', self.student_info.get('start_year', ''))
            ]
            
            # Her kolonda 2 bilgi olacak şekilde düzenle
            col_width = (pdf.w - 20) / 3
            for i, (label, value) in enumerate(student_info):
                col = i // 2
                row = i % 2
                x_pos = 10 + (col * col_width)
                y_pos = y_start + (row * 5)
                
                pdf.set_xy(x_pos, y_pos)
                pdf.set_font('Roboto', '', 7)
                pdf.cell(25, 5, f'{label}:', 0, 0)
                pdf.set_font('Roboto', 'B', 7)
                pdf.cell(col_width - 25, 5, value, 0, 0)
            
            # Öğrenci bilgileri ile dersler arası boşluk
            pdf.ln(10)

            # Dersleri yarıyıllara göre sırala
            sorted_semesters = sorted(self.semester_courses.keys())
            page_width = pdf.w - 20
            
            for semester_idx, semester in enumerate(sorted_semesters):
                # Yarıyıl başlığı
                y_start = pdf.get_y()
                pdf.set_fill_color(245, 245, 245)
                pdf.rect(10, y_start, page_width, 6, 'F')
                
                pdf.set_font('Roboto', 'B', 8)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(0, 6, f'{semester}. Yarıyıl', 0, 1, 'L')
                
                courses = self.semester_courses[semester]
                total_courses = len(courses)
                courses_per_column = (total_courses + 1) // 2
                
                col_width = page_width / 2
                
                if self.use_course_code:
                    code_width = col_width * 0.2
                    name_width = col_width * 0.6
                    grade_width = col_width * 0.2
                else:
                    name_width = col_width * 0.8
                    grade_width = col_width * 0.2
                
                # Tablo başlıkları
                pdf.set_font('Roboto', '', 6)
                pdf.set_text_color(80, 80, 80)
                
                x_start = pdf.get_x()
                if self.use_course_code:
                    pdf.cell(code_width, 4, 'Ders Kodu', 0)
                pdf.cell(name_width, 4, 'Ders Adı', 0)
                pdf.cell(grade_width, 4, 'Not', 0)
                
                pdf.set_x(x_start + col_width)
                if self.use_course_code:
                    pdf.cell(code_width, 4, 'Ders Kodu', 0)
                pdf.cell(name_width, 4, 'Ders Adı', 0)
                pdf.cell(grade_width, 4, 'Not', 0)
                pdf.ln()
                
                # İnce çizgi
                pdf.set_draw_color(220, 220, 220)
                pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
                
                # Dersleri yazdır
                pdf.set_font('Roboto', '', 7)
                pdf.set_text_color(0, 0, 0)
                
                for i in range(courses_per_column):
                    x_start = pdf.get_x()
                    
                    if i < len(courses):
                        course = courses[i]
                        if self.use_course_code:
                            pdf.set_font('Roboto', 'B', 7)
                            pdf.cell(code_width, 5, course.get('course_code', ''), 0)
                            pdf.set_font('Roboto', '', 7)
                        pdf.cell(name_width, 5, course.get('course_name', ''), 0)
                        pdf.set_font('Roboto', 'B', 7)
                        pdf.cell(grade_width, 5, str(course.get('grade', '')), 0)
                        pdf.set_font('Roboto', '', 7)
                    
                    right_idx = i + courses_per_column
                    if right_idx < len(courses):
                        pdf.set_x(x_start + col_width)
                        course = courses[right_idx]
                        if self.use_course_code:
                            pdf.set_font('Roboto', 'B', 7)
                            pdf.cell(code_width, 5, course.get('course_code', ''), 0)
                            pdf.set_font('Roboto', '', 7)
                        pdf.cell(name_width, 5, course.get('course_name', ''), 0)
                        pdf.set_font('Roboto', 'B', 7)
                        pdf.cell(grade_width, 5, str(course.get('grade', '')), 0)
                        pdf.set_font('Roboto', '', 7)
                    
                    pdf.ln()
                
                # Yarıyıllar arası boşluk
                if semester_idx < len(sorted_semesters) - 1:
                    pdf.ln(1)
            
            # GPA
            if pdf.page_no() == 1:  # Sadece ilk sayfada göster
                if self.use_credits:
                    gpa = self.calculate_gpa()
                    if gpa is not None:
                        pdf.ln(5)
                        pdf.set_font('Roboto', 'B', 8)
                        pdf.set_text_color(0, 0, 0)
                        pdf.cell(0, 6, f'Genel Not Ortalaması: {gpa:.2f}', 0, 1, 'R')
                
                # Dekan bilgisi - sadece ilk sayfada
                pdf.set_y(279)
                pdf.set_font('Roboto', '', 8)
                pdf.set_text_color(0, 0, 0)
                dean_title = self.student_info.get('dean_title', 'Fen Edebiyat Fakültesi Dekanı')
                pdf.cell(0, 4, dean_title, 0, 1, 'R')
                pdf.set_font('Roboto', 'B', 8)
                dean_name = self.student_info.get('dean_name', '')
                pdf.cell(0, 4, dean_name, 0, 1, 'R')

            pdf.output(filename)
        except Exception as e:
            print(f"PDF oluşturulurken hata: {str(e)}")
            raise