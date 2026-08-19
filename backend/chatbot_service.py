import re
from backend.translation_service import translate_crop_name

# Knowledge Base for AI Farmer Chatbot "Krishi Mitra"
KNOWLEDGE_BASE = [
    {
        "intent": "pest_disease",
        "keywords": ["pest", "bug", "insect", "disease", "worm", "borer", "fungus", "yellow", "curl", "कीड़ा", "कीट", "बीमारी", "कीड़े"],
        "responses": {
            "en": " For pest & disease control: 1) Monitor crops weekly. 2) Spray Neem Oil (5ml/L) as an organic deterrent. 3) For stem borer/caterpillars, use Chlorantraniliprole 18.5% SC. 4) For fungal leaf spots, spray Copper Oxychloride or Mancozeb 75% WP. Avoid over-watering to prevent root rot.",
            "hi": " कीट और बीमारी नियंत्रण के लिए: 1) साप्ताहिक निरीक्षण करें। 2) जैविक नियंत्रण के लिए नीम तेल (5 मिली/लीटर) छिड़कें। 3) तना छेदक या इल्ली के लिए क्लोरैंट्रानिलिप्रोले 18.5% SC का उपयोग करें। 4) फफूंद के लिए मैनकोजेब या कॉपर ऑक्सीक्लोराइड छिड़कें। अत्यधिक पानी से बचें।",
            "pa": " ਕੀੜੇ ਅਤੇ ਬਿਮਾਰੀਆਂ ਦੇ ਨਿਯੰਤਰਣ ਲਈ: 1) ਹਫ਼ਤਾਵਾਰੀ ਜਾਂਚ ਕਰੋ। 2) ਨੀਮ ਦਾ ਤੇਲ (5ml/L) ਸਪਰੇਅ ਕਰੋ। 3) ਤਣਾ ਛੇਦਕ ਲਈ ਕਲੋਰੈਂਟ੍ਰਾਨਿਲਿਪ੍ਰੋਲ ਦਾ ਪ੍ਰਯੋਗ ਕਰੋ।",
            "mr": " किडी आणि रोग नियंत्रणासाठी: १) दर आठवड्याला पिकांची पाहणी करा. २) सेंद्रिय नियंत्रणासाठी कडुनिंबाचे तेल (५ मि.ली./लीटर) फवारा. ३) खोडकिडीसाठी क्लोरँट्रानिलिप्रोल वापरा.",
            "te": " పురుగులు మరియు తెగుళ్ళ నివారణకు: 1) వారానికి ఒకసారి పంటను పరిశీలించండి. 2) వేప నూనె (5ml/L) పిచికారీ చేయండి. 3) పురుగుల నివారణకు క్లోరాంట్రానిలిప్రోల్ ఉపయోగించండి.",
            "ta": " பூச்சி மற்றும் நோய் கட்டுப்பாட்டிற்கு: 1) வாரம் ஒருமுறை பயிரை கண்காணிக்கவும். 2) வேப்பெண்ணெய் (5ml/L) தெளிக்கவும்.",
            "bn": " পোকা ও রোগ নিয়ন্ত্রণের জন্য: ১) সপ্তাহে একবার ফসল পরীক্ষা করুন। ২) নিম তেল (৫মিলি/লিটার) স্প্রে করুন।",
            "gu": " જીવાત અને રોગ નિયંત્રણ માટે: ૧) દર અઠવાડિયે પાકનું નિરીક્ષણ કરો. ૨) લીમડાનું તેલ (૫મિલિ/લીટર) છાંટો.",
            "kn": " ಕೀಟ ಮತ್ತು ರೋಗ ನಿಯಂತ್ರಣಕ್ಕಾಗಿ: 1) ವಾರಕ್ಕೊಮ್ಮೆ ಬೆಳೆ ಪರಿಶೀಲಿಸಿ. 2) ಬೇವಿನ ಎಣ್ಣೆ (5ml/L) ಸಿಂಪಡಿಸಿ."
        }
    },
    {
        "intent": "fertilizer",
        "keywords": ["fertilizer", "urea", "npk", "dap", "potash", "manure", "compost", "खाद", "उर्वरक", "यूरिया", "डीएपी"],
        "responses": {
            "en": " Fertilizer Advisory: 1) Apply NPK ratio according to your Soil Health Card. 2) Nitrogen should be applied in 3 split doses (at sowing, tillering, and flowering). 3) Apply DAP/P2O5 basally during field preparation. 4) Use Vermicompost or Farmyard Manure (FYM) to improve soil organic carbon.",
            "hi": " उर्वरक सलाह: 1) अपनी मृदा स्वास्थ्य कार्ड रिपोर्ट के अनुसार NPK दें। 2) नाइट्रोजन को 3 किस्तों में बांटकर दें (बुवाई, कल्ले निकलने और फूल आने पर)। 3) डीएपी बुवाई के समय डालें। 4) जैविक कार्बन बढ़ाने के लिए वर्मीकंपोस्ट या गोबर की खाद प्रयोग करें।",
            "pa": " ਖਾਦ ਸਲਾਹ: 1) ਆਪਣੀ ਮਿੱਟੀ ਦੀ ਰਿਪੋਰਟ ਅਨੁਸਾਰ NPK ਪਾਓ। 2) ਯੂਰੀਆ ਨੂੰ 3 ਹਿੱਸਿਆਂ ਵਿੱਚ ਵੰਡ ਕੇ ਪਾਓ। 3) ਗੋਬਰ ਦੀ ਖਾਦ ਦੀ ਵਰਤੋਂ ਕਰੋ।",
            "mr": " खत व्यवस्थापन: १) माती चाचणी अहवालानुसार NPK खते द्या. २) नत्र ३ हप्त्यांमध्ये विभागून द्या. ३) सेंद्रिय कर्ब वाढवण्यासाठी शेणखत किंवा गांडूळ खत वापरा.",
            "te": " ఎరువుల సలహా: 1) నేల పరీక్ష నివేదిక ప్రకారం NPK నిష్పత్తిని ఉపయోగించండి. 2) నత్రజనిని 3 విడతలలో ఇవ్వండి.",
            "ta": " உரம் ஆலோசனைகள்: 1) மண் பரிசோதனை அறிக்கைப்படி NPK உரமிடுங்கள். 2) நைட்ரஜனை 3 தவணைகளாக பிரிக்கவும்.",
            "bn": " সার ব্যবহার পরামর্শ: ১) মাটি পরীক্ষা রিপোর্ট অনুযায়ী NPK প্রয়োগ করুন। ২) ইউরিয়া ৩টি কিস্তিতে দিন।",
            "gu": " ખાતર સલાહ: ૧) સોઈલ હેલ્થ કાર્ડ મુજબ NPK આપો. ૨) નાઇટ્રોજન ૩ હપ્તામાં આપો. ૩) દેશી ખાતરનો ઉપયોગ કરો.",
            "kn": " ಗೊಬ್ಬರ ಸಲಹೆ: 1) ಮಣ್ಣಿನ ಪರೀಕ್ಷಾ ವರದಿಯಂತೆ NPK ಗೊಬ್ಬರ ನೀಡಿ. 2) ಯೂರಿಯಾವನ್ನು 3 ಕಂತುಗಳಲ್ಲಿ ನೀಡಿ."
        }
    },
    {
        "intent": "soil_ph",
        "keywords": ["ph", "acidic", "alkaline", "saline", "lime", "gypsum", "तेजाबी", "क्षारीय", "एसिडिक"],
        "responses": {
            "en": " Soil pH Management: Ideal pH is 6.0 - 7.5. If soil pH is Acidic (< 5.5), apply Agricultural Lime (CaCO3) @ 500 kg/ha. If soil pH is Alkaline (> 8.0), apply Agricultural Gypsum (CaSO4) and incorporate organic manure.",
            "hi": " मृदा pH प्रबंधन: आदर्श pH 6.0 - 7.5 है। यदि मिट्टी अम्लीय (pH < 5.5) है, तो कृषि चूना (500 किग्रा/हेक्टेयर) मिलाएं। यदि मिट्टी क्षारीय (pH > 8.0) है, तो जिप्सम और गोबर की खाद मिलाएं।",
            "pa": " ਮਿੱਟੀ ਦਾ pH: ਜੇਕਰ ਮਿੱਟੀ ਤੇਜ਼ਾਬੀ (pH < 5.5) ਹੈ ਤਾਂ ਚੂਨਾ ਪਾਓ। ਜੇਕਰ ਖਾਰੀ (pH > 8.0) ਹੈ ਤਾਂ ਜਿਪਸਮ ਪਾਓ।",
            "mr": " मातीचा pH: जर माती आम्लयुक्त (< 5.5) असेल तर चुनखडी वापरा. जर क्षारीय (> 8.0) असेल तर जिप्सम आणि शेणखत वापरा.",
            "te": " నేల pH యాజమాన్యం: pH 5.5 కంటే తక్కువ ఉంటే సున్నం వాడండి, 8.0 కంటే ఎక్కువ ఉంటే జిప్సం వాడండి.",
            "ta": " மண் pH மேலாண்மை: pH 5.5 க்கும் குறைவாக இருந்தால் சுண்ணாம்பு சேர்க்கவும்.",
            "bn": " মাটির pH ব্যবস্থাপনা: pH ৫.৫ এর নিচে হলে চুন দিন, ৮.০ এর উপরে হলে জিপসাম প্রয়োগ করুন।",
            "gu": " જમીન pH સંચાલન: જો જમીન એસિડિક (< 5.5) હોય તો ચૂનો ઉમેરો, અલ્કલાઇન (> 8.0) હોય તો જીપ્સમ ઉમેરો.",
            "kn": " ಮಣ್ಣಿನ pH ನಿರ್ವಹಣೆ: pH 5.5 ಕ್ಕಿಂತ ಕಡಿಮೆಯಿದ್ದರೆ ಸುಣ್ಣ ಸೇರಿಸಿ, 8.0 ಕ್ಕಿಂತ ಹೆಚ್ಚಿದ್ದರೆ ಜಿಪ್ಸಮ್ ಬಳಸಿ."
        }
    },
    {
        "intent": "subsidy_scheme",
        "keywords": ["scheme", "subsidy", "pm kisan", "pmfby", "money", "loan", "yojana", "योजना", "सब्सिडी", "पैसा", "किसान सम्मान"],
        "responses": {
            "en": " Scheme Assistance: 1) PM-KISAN gives ₹6,000/yr direct financial support. Apply on pmkisan.gov.in with Aadhaar & Land Record. 2) PMFBY provides crop loss insurance up to 98% subsidized premium. 3) Per Drop More Crop offers 55% subsidy on Drip & Sprinkler irrigation.",
            "hi": " सरकारी योजनाएं: 1) PM-KISAN के तहत हर साल ₹6,000 मिलते हैं। आधार और खसरा खतौनी के साथ pmkisan.gov.in पर आवेदन करें। 2) PMFBY फसल बीमा में केवल 1.5%-2% किश्त लगती है। 3) ड्रिप सिंचाई पर 55% तक सब्सिडी मिलती है।",
            "pa": " ਸਰਕਾਰੀ ਸਕੀਮਾਂ: PM-KISAN ਤਹਿਤ ₹6,000 ਸਾਲਾਨਾ ਮਿਲਦੇ ਹਨ। PMFBY ਤਹਿਤ ਫਸਲ ਬੀਮਾ ਕਰਵਾਓ।",
            "mr": " सरकारी योजना: १) PM-KISAN योजनेअंतर्गत वर्षाला ६,००० रुपये मिळतात. २) ड्रिप सिंचनासाठी ५५% अनुदान मिळते.",
            "te": " ప్రభుత్వ పథకాలు: PM-KISAN కింద ఏటా ₹6,000 లభిస్తాయి. పంటల బీమా కోసం PMFBY ఉపయోగించండి.",
            "ta": " அரசு திட்டங்கள்: PM-KISAN திட்டத்தில் ஆண்டுக்கு ₹6,000 நிதியுதவி ලැබේ.",
            "bn": " সরকারি প্রকল্প: PM-KISAN প্রকল্পে বছরে ৬,০০০ টাকা সরাসরি অ্যাকাউন্টে আসে।",
            "gu": " સરકારી યોજનાઓ: PM-KISAN હેઠળ વાર્ષિક ₹૬,૦૦૦ મળે છે. ડ્રીપ સિંચાઈ પર ૫૫% સબસીડી મળે છે.",
            "kn": " ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು: PM-KISAN ಯೋಜನೆಯಡಿ ವರ್ಷಕ್ಕೆ ₹6,000 ಸಿಗುತ್ತದೆ. ಹನಿ ನೀರಾವರಿಗೆ 55% ಸಬ್ಸಿಡಿ ಸಿಗುತ್ತದೆ."
        }
    }
]

DEFAULT_RESPONSES = {
    "en": " I am Krishi Mitra, your AI Farm Assistant! I can help you with crop advice, fertilizer doses, pest management, weather tips, and government subsidies. Feel free to ask any farming question!",
    "hi": " मैं कृषि मित्र हूं, आपका AI खेती सहायक! मैं आपको फसल सलाह, उर्वरक मात्रा, कीट नियंत्रण, मौसम और सरकारी योजनाओं की जानकारी दे सकता हूं। कोई भी सवाल पूछें!",
    "pa": " ਮੈਂ ਕ੍ਰਿਸ਼ੀ ਮਿੱਤਰ ਹਾਂ, ਤੁਹਾਡਾ AI ਖੇਤੀ ਸਲਾਹਕਾਰ! ਫਸਲਾਂ, ਖਾਦਾਂ ਅਤੇ ਸਰਕਾਰੀ ਸਕੀਮਾਂ ਬਾਰੇ ਕੋਈ ਵੀ ਸਵਾਲ ਪੁੱਛੋ।",
    "mr": " मी कृषी मित्र आहे, तुमचा AI शेती सहाय्यक! पीक सल्ला, खत व्यवस्थापन, किड नियंत्रण आणि सरकारी योजनांबद्दल प्रश्न विचारा.",
    "te": " నేను కృషి మిత్ర, మీ AI వ్యవసాయ సహాయకుడిని! పంటల సలహాలు, ఎరువులు, తెగుళ్ళ నివారణ గురించి అడగండి.",
    "ta": " நான் கிருஷி மித்ரா, உங்கள் AI விவசாய உதவியாளர்! பயிர் ஆலோசனைகள் மற்றும் அரசு திட்டங்கள் பற்றி கேளுங்கள்.",
    "bn": " আমি কৃষি মিত্র, আপনার AI কৃষি সহকারী! ফসল, সার ও সরকারি প্রকল্প নিয়ে প্রশ্ন করুন।",
    "gu": " હું કૃષિ મિત્ર છું, તમારો AI ખેતી મદદનીશ! પાક, ખાતર અને સરકારી યોજનાઓ વિશે પ્રશ્નો પૂછો.",
    "kn": " ನಾನು ಕೃಷಿ ಮಿತ್ರ, ನಿಮ್ಮ AI ಕೃಷಿ ಸಹಾಯಕ! ಬೆಳೆ ಸಲಹೆ ಮತ್ತು ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಕೇಳಿ."
}

def generate_chatbot_response(user_message: str, lang_code: str = "en", context_crop: str = None) -> str:
    """
    Generates AI Chatbot response based on user input, intent matching, and language localization.
    """
    msg_clean = user_message.lower()
    
    # Check knowledge base intents
    for item in KNOWLEDGE_BASE:
        if any(re.search(rf'\b{kw}\b', msg_clean, re.IGNORECASE) for kw in item["keywords"]):
            resp = item["responses"].get(lang_code, item["responses"].get("hi", item["responses"]["en"]))
            if context_crop:
                crop_trans = translate_crop_name(context_crop, lang_code)
                resp += f"\n\n👉 *Note for your recommended crop ({crop_trans}): Follow specific crop guidelines for best yield!*"
            return resp
            
    # Crop query
    if context_crop and ("crop" in msg_clean or "फसल" in msg_clean or "best" in msg_clean):
        crop_trans = translate_crop_name(context_crop, lang_code)
        if lang_code == "hi":
            return f"🌾 आपकी मिट्टी और मौसम के लिए सर्वोच्च अनुशंसित फसल **{crop_trans}** है। इसे बोने से आपको अधिकतम उत्पादन प्राप्त होगा।"
        else:
            return f"🌾 Based on your soil & weather data, your top recommended crop is **{crop_trans}**. Planting this crop ensures maximum profitability!"

    return DEFAULT_RESPONSES.get(lang_code, DEFAULT_RESPONSES["en"])
