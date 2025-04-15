from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from app import ContentStrategist
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from google_sheets_integration import GoogleSheetsExporter

app = Flask(__name__)

# إذا لم يكن مجلد templates موجودًا، قم بإنشائه
if not os.path.exists('templates'):
    os.makedirs('templates')

# إذا لم يكن مجلد static موجودًا، قم بإنشائه
if not os.path.exists('static'):
    os.makedirs('static')

# إنشاء ملف HTML الرئيسي
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write('''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>وكيل استراتيجية المحتوى</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>وكيل استراتيجية المحتوى</h1>
            <p>أداة ذكية لإنشاء خطة محتوى شاملة لمدة 30 يومًا</p>
        </header>
        
        <div class="form-container">
            <form id="niche-form">
                <div class="input-group">
                    <label for="niche">أدخل اسم المشروع أو النيتش (المجال):</label>
                    <input type="text" id="niche" name="niche" required>
                </div>
                <button type="submit" id="generate-btn">
                    <i class="fas fa-magic"></i> إنشاء خطة المحتوى
                </button>
            </form>
        </div>
        
        <div id="loading" class="hidden">
            <div class="spinner"></div>
            <p>جاري إنشاء خطة المحتوى... يرجى الانتظار</p>
        </div>
        
        <div id="results" class="hidden">
            <div class="actions">
                <button id="export-json" class="action-btn">
                    <i class="fas fa-file-download"></i> تصدير إلى JSON
                </button>
                <button id="export-sheets" class="action-btn">
                    <i class="fas fa-table"></i> تصدير إلى Google Sheets
                </button>
            </div>
            
            <div class="calendar-container">
                <h2>خطة المحتوى لمدة 30 يومًا</h2>
                <div id="calendar"></div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
''')

# إنشاء ملف CSS
with open('static/style.css', 'w', encoding='utf-8') as f:
    f.write('''
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Tajawal', sans-serif;
}

body {
    background-color: #f7f9fc;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

header {
    text-align: center;
    margin-bottom: 3rem;
}

header h1 {
    color: #2c3e50;
    margin-bottom: 0.5rem;
    font-size: 2.5rem;
}

header p {
    color: #7f8c8d;
    font-size: 1.2rem;
}

.form-container {
    background-color: white;
    border-radius: 10px;
    padding: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}

.input-group {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #2c3e50;
}

input[type="text"] {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
}

button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
    transition: background-color 0.3s;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

button i {
    margin-left: 0.5rem;
}

button:hover {
    background-color: #2980b9;
}

#loading {
    text-align: center;
    margin: 2rem 0;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid #3498db;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.hidden {
    display: none;
}

.actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.action-btn {
    background-color: #2ecc71;
}

.action-btn:hover {
    background-color: #27ae60;
}

.calendar-container {
    background-color: white;
    border-radius: 10px;
    padding: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.calendar-container h2 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: #2c3e50;
}

.day-card {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border-right: 5px solid #3498db;
}

.day-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.5rem;
}

.day-number {
    font-weight: 700;
    color: #3498db;
    font-size: 1.2rem;
}

.day-date {
    color: #7f8c8d;
}

.content-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #2c3e50;
}

.content-meta {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.5rem;
    color: #7f8c8d;
    font-size: 0.9rem;
}

.content-description {
    margin-bottom: 1rem;
    line-height: 1.6;
}

.hashtags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.hashtag {
    background-color: #e1f0fa;
    color: #3498db;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.9rem;
}

@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
    
    header h1 {
        font-size: 2rem;
    }
    
    .actions {
        flex-direction: column;
    }
}
''')

# إنشاء ملف JavaScript
with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write('''
document.addEventListener('DOMContentLoaded', function() {
    const nicheForm = document.getElementById('niche-form');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const calendarDiv = document.getElementById('calendar');
    const exportJsonBtn = document.getElementById('export-json');
    const exportSheetsBtn = document.getElementById('export-sheets');
    
    nicheForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const niche = document.getElementById('niche').value;
        if (!niche) return;
        
        // إظهار شاشة التحميل
        loadingDiv.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
        
        // إرسال طلب إلى الخادم
        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ niche: niche })
        })
        .then(response => response.json())
        .then(data => {
            // إخفاء شاشة التحميل وإظهار النتائج
            loadingDiv.classList.add('hidden');
            resultsDiv.classList.remove('hidden');
            
            // عرض جدول المحتوى
            displayCalendar(data);
        })
        .catch(error => {
            console.error('Error:', error);
            loadingDiv.classList.add('hidden');
            alert('حدث خطأ أثناء إنشاء خطة المحتوى. يرجى المحاولة مرة أخرى.');
        });
    });
    
    // عرض جدول المحتوى
    function displayCalendar(calendar) {
        calendarDiv.innerHTML = '';
        
        calendar.forEach(day => {
            const dayCard = document.createElement('div');
            dayCard.className = 'day-card';
            
            dayCard.innerHTML = `
                <div class="day-header">
                    <div class="day-number">اليوم ${day.day}</div>
                    <div class="day-date">${day.date}</div>
                </div>
                <div class="content-title">${day.title}</div>
                <div class="content-meta">
                    <div class="content-topic">${day.topic}</div>
                    <div class="content-type">${day.content_type}</div>
                </div>
                <div class="content-description">${day.meta_description}</div>
                <div class="hashtags">
                    ${day.hashtags.map(tag => `<span class="hashtag">${tag}</span>`).join('')}
                </div>
            `;
            
            calendarDiv.appendChild(dayCard);
        });
    }
    
    // تصدير إلى ملف JSON
    exportJsonBtn.addEventListener('click', function() {
        fetch('/export-json')
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'content_calendar.json';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('حدث خطأ أثناء تصدير الملف. يرجى المحاولة مرة أخرى.');
            });
    });
    
    // تصدير إلى Google Sheets
    exportSheetsBtn.addEventListener('click', function() {
        fetch('/export-sheets')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`تم تصدير خطة المحتوى بنجاح إلى Google Sheets!\nرابط الملف: ${data.spreadsheet_url}`);
                    window.open(data.spreadsheet_url, '_blank');
                } else {
                    alert('حدث خطأ أثناء التصدير: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('حدث خطأ أثناء التصدير إلى Google Sheets. يرجى المحاولة مرة أخرى.');
            });
    });
});
''')

# إنشاء ملف requirements.txt
with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write('''
flask==2.0.1
google-api-python-client==2.47.0
google-auth-httplib2==0.1.0
google-auth-oauthlib==0.5.1
''')

# إنشاء ملف credentials.json للتوثيق مع Google Sheets API
with open('credentials_info.txt', 'w', encoding='utf-8') as f:
    f.write('''
لاستخدام ميزة تصدير البيانات إلى Google Sheets، يجب عليك إنشاء ملف credentials.json من خلال اتباع الخطوات التالية:

1. انتقل إلى Google Cloud Console: https://console.cloud.google.com/
2. قم بإنشاء مشروع جديد
3. قم بتفعيل Google Sheets API لهذا المشروع
4. قم بإنشاء بيانات اعتماد OAuth 2.0 Client ID
5. قم بتنزيل ملف بيانات الاعتماد وتسميته credentials.json
6. ضع الملف في نفس المجلد مع هذا التطبيق

عند تشغيل التطبيق لأول مرة، سيطلب منك تسجيل الدخول والموافقة على الصلاحيات المطلوبة.
''')

# تنفيذ واجهة الويب
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    niche = data.get('niche', '')
    
    # إنشاء استراتيجية المحتوى باستخدام مفتاح API المقدم
    api_key = "AIzaSyDp_K9yfy_ikEO1worB8cWjIXmMIyJ3-A4"
    target_email = "mahmoudali002ai@gmail.com"
    strategist = ContentStrategist(use_gemini=True, api_key=api_key, target_email=target_email)
    strategist.set_niche(niche)
    content_calendar = strategist.generate_content_calendar()
    
    # حفظ النتائج في ملف JSON
    strategist.export_to_json()
    
    return jsonify(content_calendar)

@app.route('/export-json')
def export_json():
    if os.path.exists('temp_calendar.json'):
        return send_file('temp_calendar.json', as_attachment=True, download_name='content_calendar.json')
    else:
        return jsonify({'error': 'لم يتم إنشاء خطة محتوى بعد'}), 400

# دالة للتحقق من وجود بيانات الاعتماد وتحديثها إذا لزم الأمر
def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    
    # التحقق من وجود token.pickle
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # إذا لم تكن هناك بيانات اعتماد صالحة، فقم بإنشائها
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                return None, "ملف credentials.json غير موجود. يرجى اتباع التعليمات في ملف credentials_info.txt"
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # حفظ بيانات الاعتماد للاستخدام لاحقًا
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds, None

@app.route('/export-sheets')
def export_sheets():
    # استخدام الفئة المخصصة لتصدير البيانات إلى Google Sheets
    try:
        # قراءة بيانات جدول المحتوى من الملف
        with open('content_calendar.json', 'r', encoding='utf-8') as f:
            content_calendar = json.load(f)
        
        # تصدير البيانات إلى Google Sheets
        api_key = "AIzaSyDp_K9yfy_ikEO1worB8cWjIXmMIyJ3-A4"
        target_email = "mahmoudali002ai@gmail.com"
        exporter = GoogleSheetsExporter(api_key=api_key, target_email=target_email)
        result = exporter.export_to_sheets(content_calendar)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'spreadsheet_url': result.get('spreadsheet_url'),
                'message': f'تم تصدير البيانات بنجاح ومشاركتها مع {target_email}'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error')
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # استيراد datetime هنا لتجنب تعارض الاستيراد مع وحدة app
    from datetime import datetime
    app.run(debug=True)