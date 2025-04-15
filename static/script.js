
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
                    alert(`تم تصدير خطة المحتوى بنجاح إلى Google Sheets!
رابط الملف: ${data.spreadsheet_url}`);
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
