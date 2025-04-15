import os
import json
import google.generativeai as genai
from typing import List, Dict, Any

class GeminiContentGenerator:
    def __init__(self, api_key="AIzaSyDp_K9yfy_ikEO1worB8cWjIXmMIyJ3-A4"):
        """تهيئة مولد المحتوى باستخدام Gemini API"""
        # استخدام مفتاح API المقدم أو من المتغيرات البيئية إذا لم يتم تمريره
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("تحذير: لم يتم تعيين مفتاح API لـ Gemini. يرجى تعيين GEMINI_API_KEY كمتغير بيئي أو تمريره عند إنشاء الكائن.")
            print("سيتم استخدام المحتوى المولد افتراضيًا بدون تحسين.")
            return
        
        # تهيئة Gemini API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def is_available(self) -> bool:
        """التحقق من توفر Gemini API"""
        return self.api_key is not None
    
    def generate_main_topics(self, niche: str, count: int = 6) -> List[str]:
        """توليد المواضيع الرئيسية بناءً على النيتش باستخدام Gemini"""
        if not self.is_available():
            return []
        
        prompt = f"""أنت خبير في استراتيجية المحتوى. 
        قم بإنشاء {count} مواضيع رئيسية مناسبة لمجال \"{niche}\" لخطة محتوى لمدة 30 يومًا.
        المواضيع يجب أن تكون:
        1. مترابطة ومتسلسلة لبناء اهتمام تدريجي
        2. متنوعة لتغطية جوانب مختلفة من المجال
        3. ذات صلة بالجمهور المستهدف
        4. قابلة للتوسع في محتوى متنوع
        
        أعطني قائمة بالمواضيع فقط، بدون أي مقدمات أو تعليقات إضافية.
        """
        
        try:
            response = self.model.generate_content(prompt)
            topics = [line.strip() for line in response.text.split('\n') if line.strip()]
            # تنظيف القائمة من أي ترقيم أو رموز
            topics = [topic.strip().lstrip('0123456789-.*').strip() for topic in topics]
            return topics[:count]  # التأكد من الحصول على العدد المطلوب فقط
        except Exception as e:
            print(f"خطأ في توليد المواضيع: {e}")
            return []
    
    def generate_title(self, topic: str, content_type: str, niche: str) -> str:
        """توليد عنوان جذاب باستخدام Gemini"""
        if not self.is_available():
            return ""
        
        prompt = f"""أنت خبير في كتابة العناوين الجذابة. 
        قم بإنشاء عنوان جذاب لمحتوى من نوع \"{content_type}\" حول موضوع \"{topic}\" في مجال \"{niche}\".
        العنوان يجب أن يكون:
        1. جذاب ويثير الفضول
        2. واضح ومباشر
        3. يحتوي على كلمات مفتاحية مناسبة
        4. لا يزيد عن 70 حرفًا
        
        أعطني العنوان فقط، بدون علامات اقتباس أو أي نص إضافي.
        """
        
        try:
            response = self.model.generate_content(prompt)
            title = response.text.strip()
            return title
        except Exception as e:
            print(f"خطأ في توليد العنوان: {e}")
            return ""
    
    def generate_meta_description(self, topic: str, content_type: str, niche: str) -> str:
        """توليد وصف SEO باستخدام Gemini"""
        if not self.is_available():
            return ""
        
        prompt = f"""أنت خبير في تحسين محركات البحث (SEO). 
        قم بإنشاء وصف ميتا (Meta Description) لمحتوى من نوع \"{content_type}\" حول موضوع \"{topic}\" في مجال \"{niche}\".
        الوصف يجب أن:
        1. يكون جذابًا ويحفز على النقر
        2. يتضمن الكلمات المفتاحية المناسبة
        3. يلخص محتوى الصفحة بشكل دقيق
        4. لا يتجاوز 160 حرفًا
        
        أعطني الوصف فقط، بدون علامات اقتباس أو أي نص إضافي.
        """
        
        try:
            response = self.model.generate_content(prompt)
            description = response.text.strip()
            # التأكد من أن الوصف لا يتجاوز 160 حرفًا
            if len(description) > 160:
                description = description[:157] + "..."
            return description
        except Exception as e:
            print(f"خطأ في توليد وصف SEO: {e}")
            return ""
    
    def generate_hashtags(self, topic: str, niche: str) -> List[str]:
        """توليد هاشتاغات مناسبة باستخدام Gemini"""
        if not self.is_available():
            return []
        
        prompt = f"""أنت خبير في وسائل التواصل الاجتماعي. 
        قم بإنشاء 5 هاشتاغات مناسبة وشائعة لمحتوى حول موضوع \"{topic}\" في مجال \"{niche}\".
        الهاشتاغات يجب أن تكون:
        1. ذات صلة بالموضوع والمجال
        2. شائعة ومستخدمة بكثرة
        3. مزيج من هاشتاغات عامة وخاصة
        4. مناسبة للغة العربية
        
        أعطني قائمة بالهاشتاغات فقط، بدون أي مقدمات أو تعليقات إضافية.
        تأكد من إضافة علامة # قبل كل هاشتاغ.
        """
        
        try:
            response = self.model.generate_content(prompt)
            hashtags = [line.strip() for line in response.text.split('\n') if line.strip()]
            # تنظيف القائمة وإضافة # إذا لم تكن موجودة
            hashtags = [tag if tag.startswith('#') else f"#{tag}" for tag in hashtags]
            return hashtags[:5]  # التأكد من الحصول على 5 هاشتاغات فقط
        except Exception as e:
            print(f"خطأ في توليد الهاشتاغات: {e}")
            return []
    
    def enhance_content_calendar(self, calendar: List[Dict[str, Any]], niche: str) -> List[Dict[str, Any]]:
        """تحسين جدول المحتوى الموجود باستخدام Gemini"""
        if not self.is_available():
            return calendar
        
        enhanced_calendar = []
        
        for day in calendar:
            topic = day['topic']
            content_type = day['content_type']
            
            # تحسين العنوان
            title = self.generate_title(topic, content_type, niche)
            if title:
                day['title'] = title
            
            # تحسين وصف SEO
            meta_description = self.generate_meta_description(topic, content_type, niche)
            if meta_description:
                day['meta_description'] = meta_description
            
            # تحسين الهاشتاغات
            hashtags = self.generate_hashtags(topic, niche)
            if hashtags:
                day['hashtags'] = hashtags
            
            enhanced_calendar.append(day)
        
        return enhanced_calendar

# مثال على الاستخدام
if __name__ == "__main__":
    # اختبار الوظائف
    generator = GeminiContentGenerator()
    if generator.is_available():
        topics = generator.generate_main_topics("التسويق الرقمي", 3)
        print("المواضيع المقترحة:")
        for topic in topics:
            print(f"- {topic}")
            
        title = generator.generate_title("استراتيجيات السوشيال ميديا", "نصائح", "التسويق الرقمي")
        print(f"\nالعنوان المقترح: {title}")
        
        description = generator.generate_meta_description("استراتيجيات السوشيال ميديا", "نصائح", "التسويق الرقمي")
        print(f"\nوصف SEO: {description}")
        
        hashtags = generator.generate_hashtags("استراتيجيات السوشيال ميديا", "التسويق الرقمي")
        print("\nالهاشتاغات المقترحة:")
        for tag in hashtags:
            print(tag)
    else:
        print("Gemini API غير متوفر. يرجى تعيين مفتاح API.")