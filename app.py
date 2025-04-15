import json
import os
import sys
from datetime import datetime, timedelta
import random
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from gemini_integration import GeminiContentGenerator
# استيراد مكتبات إضافية للتكامل مع Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class ContentStrategist:
    def __init__(self, use_gemini=True, api_key="AIzaSyDp_K9yfy_ikEO1worB8cWjIXmMIyJ3-A4", target_email=None):
        self.niche = ""
        self.content_calendar = []
        self.content_types = [
            "نصائح",
            "معلومات",
            "أسئلة",
            "اقتباسات",
            "قصص نجاح",
            "تحديات",
            "حقائق",
            "مقارنات",
            "دراسات حالة",
            "تقنيات"
        ]
        
        # إعداد مفتاح API والبريد الإلكتروني المستهدف
        self.api_key = api_key
        self.target_email = target_email
        
        # إعداد LangChain مع Gemini API
        self.use_gemini = use_gemini
        self.gemini_generator = GeminiContentGenerator(api_key=self.api_key)
        
        # إعداد LangChain إذا كان مفتاح API متوفر
        if self.api_key and use_gemini:
            try:
                self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=self.api_key)
                self.langchain_available = True
            except Exception as e:
                print(f"خطأ في تهيئة LangChain: {e}")
                self.langchain_available = False
        else:
            self.langchain_available = False
    
    def set_niche(self, niche):
        self.niche = niche
    
    def generate_content_calendar(self):
        """إنشاء جدول محتوى لمدة 30 يومًا"""
        start_date = datetime.now()
        
        # تحديد المواضيع الرئيسية بناءً على النيتش
        if self.use_gemini and self.gemini_generator.is_available():
            # استخدام Gemini لتوليد مواضيع أكثر ذكاءً
            main_topics = self.gemini_generator.generate_main_topics(self.niche)
            if not main_topics or len(main_topics) < 6:
                # استخدام الطريقة الاحتياطية إذا فشل Gemini
                main_topics = self._generate_main_topics()
        else:
            main_topics = self._generate_main_topics()
        
        # إنشاء محتوى لكل يوم
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            
            # اختيار موضوع من المواضيع الرئيسية بشكل دوري
            topic_index = i % len(main_topics)
            base_topic = main_topics[topic_index]
            
            # اختيار نوع المحتوى بشكل عشوائي
            content_type = random.choice(self.content_types)
            
            # إنشاء عنوان جذاب باستخدام Gemini إذا كان متاحًا
            if self.use_gemini and self.gemini_generator.is_available():
                title = self.gemini_generator.generate_title(base_topic, content_type, self.niche)
                if not title:  # استخدام الطريقة الاحتياطية إذا فشل Gemini
                    title = self._generate_title(base_topic, content_type)
            else:
                title = self._generate_title(base_topic, content_type)
            
            # إنشاء وصف SEO باستخدام Gemini إذا كان متاحًا
            if self.use_gemini and self.gemini_generator.is_available():
                meta_description = self.gemini_generator.generate_meta_description(base_topic, content_type, self.niche)
                if not meta_description:  # استخدام الطريقة الاحتياطية إذا فشل Gemini
                    meta_description = self._generate_meta_description(base_topic, content_type)
            else:
                meta_description = self._generate_meta_description(base_topic, content_type)
            
            # إنشاء هاشتاغات باستخدام Gemini إذا كان متاحًا
            if self.use_gemini and self.gemini_generator.is_available():
                hashtags = self.gemini_generator.generate_hashtags(base_topic, self.niche)
                if not hashtags:  # استخدام الطريقة الاحتياطية إذا فشل Gemini
                    hashtags = self._generate_hashtags(base_topic)
            else:
                hashtags = self._generate_hashtags(base_topic)
            
            # إضافة المحتوى إلى الجدول
            self.content_calendar.append({
                "day": i + 1,
                "date": date_str,
                "topic": base_topic,
                "content_type": content_type,
                "title": title,
                "meta_description": meta_description,
                "hashtags": hashtags
            })
        
        return self.content_calendar
    
    def _generate_main_topics(self):
        """توليد المواضيع الرئيسية بناءً على النيتش"""
        # هذه مجرد أمثلة، يمكن تحسينها باستخدام نماذج لغوية متقدمة
        if "صحة" in self.niche or "لياقة" in self.niche:
            return [
                "التغذية السليمة",
                "تمارين رياضية",
                "الصحة النفسية",
                "نمط حياة صحي",
                "الوقاية من الأمراض",
                "العناية بالجسم"
            ]
        elif "تكنولوجيا" in self.niche or "تقنية" in self.niche:
            return [
                "الذكاء الاصطناعي",
                "تطوير التطبيقات",
                "أمن المعلومات",
                "التقنيات الناشئة",
                "الحوسبة السحابية",
                "البرمجة"
            ]
        elif "أعمال" in self.niche or "ريادة" in self.niche:
            return [
                "ريادة الأعمال",
                "التسويق الرقمي",
                "إدارة المشاريع",
                "الاستثمار",
                "تطوير المهارات",
                "القيادة"
            ]
        elif "تعليم" in self.niche or "تعلم" in self.niche:
            return [
                "طرق التعلم الفعالة",
                "تنمية المهارات",
                "التعليم عن بعد",
                "تطوير الذات",
                "اللغات",
                "المناهج التعليمية"
            ]
        elif "سفر" in self.niche or "سياحة" in self.niche:
            return [
                "وجهات سياحية",
                "نصائح السفر",
                "ثقافات العالم",
                "تجارب سفر",
                "السياحة المستدامة",
                "أكلات عالمية"
            ]
        else:
            # نيتش غير معروف، إنشاء مواضيع عامة
            return [
                f"أساسيات {self.niche}",
                f"تطوير مهارات {self.niche}",
                f"اتجاهات حديثة في {self.niche}",
                f"دراسات حالة في {self.niche}",
                f"نصائح لتحسين {self.niche}",
                f"مستقبل {self.niche}"
            ]
    
    def _generate_title(self, topic, content_type):
        """توليد عنوان جذاب بناءً على الموضوع ونوع المحتوى"""
        templates = {
            "نصائح": [
                f"10 نصائح فعالة لتحسين {topic} لم تسمع عنها من قبل",
                f"كيف تتقن {topic} في أقل من أسبوع؟ إليك الطريقة",
                f"أسرار {topic} التي لا يخبرك بها الخبراء"
            ],
            "معلومات": [
                f"كل ما تحتاج معرفته عن {topic} في 2023",
                f"حقائق مذهلة عن {topic} ستغير نظرتك للأبد",
                f"دليلك الشامل لفهم {topic} من الصفر للاحتراف"
            ],
            "أسئلة": [
                f"هل تعرف حقًا كيف يعمل {topic}؟ اختبر معلوماتك الآن",
                f"ما الذي يجعل {topic} ضروريًا في حياتك اليومية؟",
                f"لماذا يفشل معظم الناس في {topic}؟ والحل البسيط"
            ],
            "اقتباسات": [
                f"5 مقولات ملهمة عن {topic} ستغير حياتك",
                f"اقتباسات خالدة من رواد {topic} لتحفيزك يوميًا",
                f"كلمات من ذهب: ما قاله العظماء عن {topic}"
            ],
            "قصص نجاح": [
                f"من الصفر للقمة: قصة نجاح ملهمة في مجال {topic}",
                f"كيف حول هذا الشخص شغفه بـ {topic} إلى ملايين؟",
                f"قصص ملهمة: هكذا تغلبوا على التحديات في {topic}"
            ],
            "تحديات": [
                f"تحدي الـ 30 يوم في {topic}: انضم إلينا الآن",
                f"أصعب 3 تحديات ستواجهك في {topic} وكيفية التغلب عليها",
                f"تحدي الخروج من منطقة الراحة في {topic}: هل أنت مستعد؟"
            ],
            "حقائق": [
                f"7 حقائق صادمة عن {topic} لم تكن تعرفها من قبل",
                f"الحقيقة المخفية وراء {topic} التي لا يريدونك أن تعرفها",
                f"حقائق وأرقام: الدليل العلمي حول {topic}"
            ],
            "مقارنات": [
                f"{topic} قديمًا وحديثًا: تطور مذهل عبر السنين",
                f"مقارنة شاملة: أفضل طرق {topic} - أيها تختار؟",
                f"الفرق بين المبتدئين والمحترفين في {topic}: دراسة تحليلية"
            ],
            "دراسات حالة": [
                f"دراسة حالة: كيف حقق {self.niche} نجاحًا باهرًا في {topic}",
                f"تحليل معمق: نموذج ناجح في {topic} يمكنك تطبيقه",
                f"من الفشل للنجاح: دراسة حالة واقعية في {topic}"
            ],
            "تقنيات": [
                f"5 تقنيات متقدمة في {topic} ستضاعف إنتاجيتك",
                f"التقنية السرية التي يستخدمها الخبراء في {topic}",
                f"أحدث التقنيات في {topic} لعام 2023"
            ]
        }
        
        # اختيار قالب عشوائي من القوالب المتاحة لنوع المحتوى
        templates_for_type = templates.get(content_type, templates["معلومات"])
        return random.choice(templates_for_type)
    
    def _generate_meta_description(self, topic, content_type):
        """توليد وصف SEO لا يتجاوز 160 حرفًا"""
        templates = {
            "نصائح": f"اكتشف أفضل النصائح العملية في مجال {topic} لتحسين مهاراتك وتحقيق نتائج أفضل. نصائح حصرية من خبراء {self.niche}.",
            "معلومات": f"دليل شامل يقدم معلومات قيمة عن {topic} بأسلوب مبسط. كل ما تحتاج معرفته في مكان واحد لفهم {self.niche} بعمق.",
            "أسئلة": f"إجابات على الأسئلة الشائعة حول {topic} من خبراء {self.niche}. اكتشف الحقائق وتجاوز المفاهيم الخاطئة.",
            "اقتباسات": f"اقتباسات ملهمة من رواد {topic} ستمنحك الدافع والإلهام. كلمات من ذهب لتحفيزك في رحلتك مع {self.niche}.",
            "قصص نجاح": f"قصص نجاح ملهمة في مجال {topic} تكشف أسرار التفوق والتميز. تجارب واقعية من عالم {self.niche}.",
            "تحديات": f"تعرف على أبرز التحديات في {topic} وكيفية التغلب عليها بخطوات عملية. دليلك للنجاح في {self.niche}.",
            "حقائق": f"حقائق مدهشة ومعلومات موثقة عن {topic} تكشف جوانب خفية في عالم {self.niche}. اكتشف ما لم تعرفه من قبل.",
            "مقارنات": f"مقارنة تفصيلية بين أفضل الممارسات في {topic} لمساعدتك على اتخاذ القرار الأمثل في رحلتك مع {self.niche}.",
            "دراسات حالة": f"تحليل معمق لحالات نجاح في {topic} مع استخلاص الدروس والعبر. خبرات عملية من واقع {self.niche}.",
            "تقنيات": f"أحدث التقنيات والأساليب المبتكرة في {topic} لتطوير مهاراتك في {self.niche}. حلول عملية للتحديات اليومية."
        }
        
        description = templates.get(content_type, templates["معلومات"])
        
        # التأكد من أن الوصف لا يتجاوز 160 حرفًا
        if len(description) > 160:
            description = description[:157] + "..."
        
        return description
    
    def _generate_hashtags(self, topic):
        """توليد 5 هاشتاغات مناسبة"""
        # هاشتاغات عامة مرتبطة بالنيتش
        general_hashtags = [
            f"#{self.niche}",
            f"#{self.niche}_tips",
            f"#{topic.replace(' ', '')}",
            f"#محتوى_{self.niche.replace(' ', '')}",
            f"#خبراء_{self.niche.replace(' ', '')}",
            f"#نصائح_{self.niche.replace(' ', '')}",
            f"#تعلم_{self.niche.replace(' ', '')}",
            f"#أفضل_{self.niche.replace(' ', '')}",
            f"#دليل_{self.niche.replace(' ', '')}",
            f"#أسرار_{self.niche.replace(' ', '')}"
        ]
        
        # هاشتاغات خاصة بالموضوع
        topic_hashtags = [
            f"#{topic.replace(' ', '')}",
            f"#كيفية_{topic.replace(' ', '')}",
            f"#أفضل_{topic.replace(' ', '')}",
            f"#تطوير_{topic.replace(' ', '')}",
            f"#تحسين_{topic.replace(' ', '')}",
            f"#دليل_{topic.replace(' ', '')}",
            f"#نصائح_{topic.replace(' ', '')}",
            f"#أساسيات_{topic.replace(' ', '')}",
            f"#مهارات_{topic.replace(' ', '')}",
            f"#تعلم_{topic.replace(' ', '')}"
        ]
        
        # هاشتاغات شائعة عامة
        popular_hashtags = [
            "#محتوى_قيم",
            "#تطوير_الذات",
            "#نصائح_مفيدة",
            "#تعلم_مهارة_جديدة",
            "#نجاح",
            "#تحفيز",
            "#إلهام",
            "#مهارات",
            "#تعليم",
            "#معرفة"
        ]
        
        # اختيار 5 هاشتاغات بشكل عشوائي من المجموعات المختلفة
        selected_hashtags = []
        selected_hashtags.append(random.choice(general_hashtags))
        selected_hashtags.append(random.choice(topic_hashtags))
        
        # إضافة 3 هاشتاغات إضافية بشكل عشوائي
        remaining_hashtags = list(set(general_hashtags + topic_hashtags + popular_hashtags) - set(selected_hashtags))
        selected_hashtags.extend(random.sample(remaining_hashtags, 3))
        
        # التأكد من عدم وجود تكرار
        return list(set(selected_hashtags))[:5]
    
    def export_to_json(self, filename="content_calendar.json"):
        """تصدير جدول المحتوى إلى ملف JSON"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.content_calendar, f, ensure_ascii=False, indent=4)
        return filename
        
    def export_to_sheets(self, spreadsheet_title=None):
        """تصدير جدول المحتوى إلى Google Sheets"""
        from google_sheets_integration import GoogleSheetsExporter
        
        if not spreadsheet_title:
            spreadsheet_title = f"خطة محتوى - {self.niche}"
            
        exporter = GoogleSheetsExporter(api_key=self.api_key, target_email=self.target_email)
        result = exporter.export_to_sheets(self.content_calendar, spreadsheet_title)
        
        return result

def main():
    # استخدام مفتاح API المقدم
    api_key = "AIzaSyDp_K9yfy_ikEO1worB8cWjIXmMIyJ3-A4"
    target_email = "mahmoudali002ai@gmail.com"
    use_gemini = True
    
    strategist = ContentStrategist(use_gemini=use_gemini, api_key=api_key, target_email=target_email)
    
    # الحصول على النيتش من المستخدم
    print("مرحبًا بك في وكيل استراتيجية المحتوى!")
    print("سأساعدك في إنشاء خطة محتوى شاملة لمدة 30 يومًا.")
    niche = input("\nالرجاء إدخال اسم المشروع أو النيتش (المجال): ")
    
    strategist.set_niche(niche)
    
    print(f"\nجاري إنشاء خطة محتوى لمدة 30 يومًا لمجال: {niche}...")
    if use_gemini:
        print("(جاري استخدام Gemini AI لتحسين جودة المحتوى)")
    
    content_calendar = strategist.generate_content_calendar()
    
    # تصدير النتائج إلى ملف JSON
    output_file = strategist.export_to_json()
    print(f"\nتم إنشاء خطة المحتوى بنجاح وتصديرها إلى الملف: {output_file}")
    
    # تصدير النتائج إلى Google Sheets
    print("\nجاري تصدير خطة المحتوى إلى Google Sheets...")
    sheets_result = strategist.export_to_sheets()
    
    if sheets_result.get("success"):
        print(f"تم تصدير خطة المحتوى بنجاح إلى Google Sheets!")
        print(f"رابط الجدول: {sheets_result.get('spreadsheet_url')}")
        print(f"تم مشاركة الجدول مع البريد الإلكتروني: {target_email}")
    else:
        print(f"حدث خطأ أثناء تصدير البيانات إلى Google Sheets: {sheets_result.get('error')}")
        print("تم تصدير البيانات إلى ملف JSON فقط.")
    
    # عرض مثال على المحتوى
    print("\nمثال على المحتوى المقترح:")
    example = content_calendar[0]
    print(f"اليوم {example['day']} - {example['date']}")
    print(f"الموضوع: {example['topic']} ({example['content_type']})")
    print(f"العنوان: {example['title']}")
    print(f"وصف SEO: {example['meta_description']}")
    print(f"الهاشتاغات: {', '.join(example['hashtags'])}")

if __name__ == "__main__":
    main()