import os
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetsExporter:
    def __init__(self, api_key=None, target_email=None):
        """تهيئة مصدر Google Sheets"""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.target_email = target_email
        self.credentials_file = "credentials.json"
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # إنشاء ملف اعتماد مؤقت للوصول إلى Google Sheets API
        self._create_credentials_file()
    
    def _create_credentials_file(self):
        """إنشاء ملف اعتماد مؤقت للوصول إلى Google Sheets API"""
        # هذه بيانات اعتماد بسيطة للوصول إلى Google Sheets API
        # في التطبيق الحقيقي، يجب استخدام طريقة أكثر أمانًا
        credentials_data = {
            "type": "service_account",
            "project_id": "content-strategist",
            "private_key_id": "private_key_id",
            "private_key": "-----BEGIN PRIVATE KEY-----\n-----END PRIVATE KEY-----\n",
            "client_email": "content-strategist@content-strategist.iam.gserviceaccount.com",
            "client_id": "client_id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/content-strategist%40content-strategist.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        
        # حفظ بيانات الاعتماد في ملف مؤقت
        with open(self.credentials_file, "w", encoding="utf-8") as f:
            json.dump(credentials_data, f, ensure_ascii=False, indent=4)
    
    def export_to_sheets(self, content_calendar, spreadsheet_title="خطة المحتوى"):
        """تصدير جدول المحتوى إلى Google Sheets"""
        try:
            # استخدام gspread للتعامل مع Google Sheets
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, self.scopes)
            client = gspread.authorize(credentials)
            
            # إنشاء جدول بيانات جديد
            spreadsheet = client.create(spreadsheet_title)
            
            # مشاركة الجدول مع البريد الإلكتروني المستهدف إذا تم تحديده
            if self.target_email:
                spreadsheet.share(self.target_email, perm_type='user', role='writer')
            
            # الحصول على الورقة الأولى
            worksheet = spreadsheet.get_worksheet(0)
            
            # إعداد رؤوس الأعمدة
            headers = ["اليوم", "التاريخ", "الموضوع", "نوع المحتوى", "العنوان", "وصف SEO", "الهاشتاغات"]
            worksheet.append_row(headers)
            
            # إضافة بيانات جدول المحتوى
            for day in content_calendar:
                row = [
                    day["day"],
                    day["date"],
                    day["topic"],
                    day["content_type"],
                    day["title"],
                    day["meta_description"],
                    ", ".join(day["hashtags"])
                ]
                worksheet.append_row(row)
            
            # تنسيق الجدول
            worksheet.format("A1:G1", {
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
                "horizontalAlignment": "CENTER",
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            })
            
            # ضبط عرض الأعمدة
            worksheet.columns_auto_resize(0, 7)
            
            return {
                "success": True,
                "spreadsheet_url": spreadsheet.url,
                "spreadsheet_id": spreadsheet.id
            }
            
        except Exception as e:
            print(f"خطأ في تصدير البيانات إلى Google Sheets: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# مثال على الاستخدام
if __name__ == "__main__":
    # اختبار التصدير إلى Google Sheets
    exporter = GoogleSheetsExporter(api_key="YOUR_API_KEY", target_email="example@gmail.com")
    
    # بيانات اختبار
    test_calendar = [
        {
            "day": 1,
            "date": "2023-01-01",
            "topic": "موضوع اختبار",
            "content_type": "نصائح",
            "title": "عنوان اختبار",
            "meta_description": "وصف اختبار",
            "hashtags": ["#اختبار1", "#اختبار2"]
        }
    ]
    
    result = exporter.export_to_sheets(test_calendar)
    print(result)