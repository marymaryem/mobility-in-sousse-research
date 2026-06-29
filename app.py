
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Mobilité Sousse | سوسة للتنقل",
    page_icon="🚐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: "DM Sans", sans-serif;
}

.hero {
    background: linear-gradient(135deg, #1B2A4A 0%, #2E5090 100%);
    padding: 48px 32px;
    border-radius: 12px;
    margin-bottom: 32px;
    text-align: center;
}
.hero h1 {
    font-family: "Syne", sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: #D4A017;
    margin-bottom: 8px;
}
.hero p {
    color: #CBD5E1;
    font-size: 1.1rem;
    max-width: 600px;
    margin: 0 auto;
}
.stat-card {
    background: linear-gradient(135deg, #1B2A4A, #2E5090);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    color: white;
    margin-bottom: 16px;
}
.stat-number {
    font-family: "Syne", sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: #D4A017;
    line-height: 1;
}
.stat-label {
    font-size: 0.85rem;
    color: #94A3B8;
    margin-top: 6px;
}
.case-card {
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 12px;
    border-left: 4px solid;
}
.risk-high {
    background: #FEE2E2;
    border-color: #EF4444;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}
.risk-medium {
    background: #FEF3C7;
    border-color: #F59E0B;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}
.risk-low {
    background: #D1FAE5;
    border-color: #10B981;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}
.section-title {
    font-family: "Syne", sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #1B2A4A;
    margin-bottom: 4px;
}
.lang-badge {
    display: inline-block;
    background: #D4A017;
    color: #1B2A4A;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 700;
    margin-bottom: 12px;
}
.status-box {
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    font-size: 1rem;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ── Load models and data ──────────────────────────────────────
@st.cache_resource
def load_models():
    rf_wait  = joblib.load("models/model_wait.pkl")
    rf_case1 = joblib.load("models/model_case1.pkl")
    encoders = joblib.load("models/encoders.pkl")
    return rf_wait, rf_case1, encoders

@st.cache_data
def load_data():
    df = pd.read_csv("data/Mobility_survey2.csv")
    df.columns = df.columns.str.strip()
    df["case_full"] = df["case"].str.contains("ممتلئ", na=False).astype(int)
    df["case_rush"] = df["case"].str.contains("يتدافعون", na=False).astype(int)
    zone_map = {
        "(la poste) البريد  القلعة الكبرى": "Kalaa Kebira",
        "معهد علي بورقيبة القلعة الكبرى": "Kalaa Kebira",
        "سير عويتي القلعة الكبرى": "Kalaa Kebira",
        "المراح القلعة الكبرى": "Kalaa Kebira",
        "الحي الجديد (مخبزة زايد) القلعة الكبرى": "Kalaa Kebira",
        "دردور القلعة الكبرى": "Kalaa Kebira",
        "الوردة أكودة": "Akouda",
        "قمعون أكودة": "Akouda",
        "مفترق حنبعل أكودة": "Akouda",
        "مفترق موبلاتكس حمام سوسة": "Sousse City",
        "سيدي سالم حمام سوسة": "Sousse City",
        "المنشية حمام سوسة": "Sousse City",
        "خزامة": "Sousse City",
        "مفترق بانوراما": "Sousse City",
        "محطة مستشفى فرحات حشاد": "Sousse City",
        "باب بحر": "Sousse City",
    }
    df["zone"] = df["station"].map(zone_map)
    df["zone"] = df["zone"].fillna("Kalaa Kebira")
    return df

rf_wait, rf_case1, encoders = load_models()
df = load_data()

le_zone  = encoders["zone"]
le_time  = encoders["time_slot"]
le_freq  = encoders["frequency"]
le_wait  = encoders["wait_time"]

# ── Language selector ─────────────────────────────────────────
lang = st.sidebar.selectbox(
    "🌐 Language / اللغة / Langue",
    ["English", "Français", "العربية"]
)

# ── Text content by language ──────────────────────────────────
content = {
    "English": {
        "title": "Mobility Crisis in Sousse",
        "subtitle": "The first data-driven study of shared taxi demand on the Kalaa Kebira → Beb Bhar corridor",
        "nav": ["🏠 The Problem", "📊 The Data", "🚐 Your Commute", "💡 The Fix"],
        "problem_title": "The Problem",
        "problem_text": "Sousse has a bus network — but it's unreliable. So 75% of daily commuters depend on shared taxis (louages) on the KK → Beb Bhar corridor. No schedule, no data, no coordination. The result: unpredictable waits, full louages, and daily chaos.",
        "stats": ["of commuters wait >15 min", "experience full louages daily", "say Monday is the worst day", "never or rarely use the bus"],
        "predict_title": "Predict Your Commute",
        "predict_title": "Predict Your Commute",
        "predict_desc": "Select your profile to see your predicted wait time and risk level.",
        "zone_label": "Your boarding zone",
        "time_label": "Your usual time slot",
        "best_window": "Your Best Travel Window",
        "predict_desc": "Select your profile to see your predicted wait time and risk level.",
        "time_label": "Your usual time slot",
        "freq_label": "How often do you travel?",
        "predict_btn": "🔍 Predict My Commute",
        "best_window": "Your Best Travel Window",
        "fix_title": "What Would Actually Fix This",
        "solutions": [
            ("🕐 Regulate departure intervals", "Fix scheduled departures every 12 min at KK during peak hours. Eliminates supply gaps (Case 3)."),
            ("📍 Queue markers at key stops", "Paint boarding zones at Gamooun and Sidi Salem. Eliminates boarding rush (Case 4)."),
            ("🚐 Pre-position louages mid-route", "One louage per cycle starts from Akouda or H.Sousse — not KK. Fixes full louage problem (Case 1) for mid-route passengers."),
            ("🚌 Fix the bus — fix the louage", "Bus unreliability forces passengers onto louages. Improving bus frequency directly reduces louage overcrowding."),
        ],
    },
    "Français": {
        "title": "Crise de Mobilité à Sousse",
        "subtitle": "La première étude basée sur les données de la demande en taxis collectifs sur le corridor Kalaa Kebira → Beb Bhar",
        "nav": ["🏠 Le Problème", "📊 Les Données", "🚐 Votre Trajet", "💡 Les Solutions"],
        "problem_title": "Le Problème",
        "problem_text": "Sousse dispose d'un réseau de bus — mais il est peu fiable. Ainsi, 75% des navetteurs quotidiens dépendent des taxis collectifs (louages) sur le corridor KK → Beb Bhar. Pas d'horaires, pas de données, pas de coordination. Résultat: des attentes imprévisibles et un chaos quotidien.",
        "stats": ["des navetteurs attendent >15 min", "vivent des louages complets chaque jour", "disent que le lundi est le pire jour", "n'utilisent jamais le bus"],
        "predict_title": "Prédire Votre Trajet",
        "predict_desc": "Sélectionnez votre profil pour voir votre temps d'attente prédit.",
        "zone_label": "Votre zone d'embarquement",
        "time_label": "Votre créneau habituel",
        "freq_label": "À quelle fréquence voyagez-vous?",
        "predict_btn": "🔍 Prédire Mon Trajet",
        "best_window": "Votre Meilleure Fenêtre de Trajet",
        "fix_title": "Ce Qui Résoudrait Vraiment Ce Problème",
        "solutions": [
            ("🕐 Réguler les intervalles de départ", "Départs programmés toutes les 12 min à KK aux heures de pointe. Élimine les gaps d'offre (Case 3)."),
            ("📍 Marquages de file aux arrêts clés", "Peindre des zones d'embarquement à Gamooun et Sidi Salem. Élimine la bousculade (Case 4)."),
            ("🚐 Pré-positionner des louages en milieu de trajet", "Un louage par cycle part d'Akouda ou H.Sousse. Résout le problème des louages complets (Case 1)."),
            ("🚌 Réparer le bus — réparer le louage", "Le manque de fiabilité du bus force les passagers vers les louages. Améliorer la fréquence des bus réduit directement la surpopulation des louages."),
        ],
    },
    "العربية": {
        "title": "أزمة التنقل في سوسة",
        "subtitle": "أول دراسة مبنية على البيانات حول الطلب على التاكسي الجماعي في محور القلعة الكبرى ← باب البحر",
        "nav": ["🏠 المشكلة", "📊 البيانات", "🚐 رحلتك", "💡 الحلول"],
        "problem_title": "المشكلة",
        "problem_text": "سوسة لديها شبكة حافلات — لكنها غير موثوقة. لذلك 75% من المسافرين اليوميين يعتمدون على التاكسي الجماعي في محور القلعة الكبرى ← باب البحر. لا جداول زمنية، لا بيانات، لا تنسيق. النتيجة: انتظار غير متوقع وفوضى يومية.",
        "stats": ["من المسافرين ينتظرون أكثر من 15 دقيقة", "يواجهون لوّاجات ممتلئة يومياً", "يقولون الاثنين هو أسوأ يوم", "لا يستخدمون الحافلة أبداً أو نادراً"],
        "predict_title": "تنبأ برحلتك",
        "predict_desc": "اختر ملفك الشخصي لمعرفة وقت الانتظار المتوقع ومستوى المخاطرة.",
        "zone_label": "منطقة صعودك",
        "time_label": "الفترة الزمنية المعتادة",
        "freq_label": "كم مرة تسافر؟",
        "predict_btn": "🔍 تنبأ برحلتي",
        "best_window": "أفضل وقت للسفر",
        "fix_title": "ما الذي سيحل المشكلة فعلاً",
        "solutions": [
            ("🕐 تنظيم فترات المغادرة", "مغادرة منظمة كل 12 دقيقة من القلعة الكبرى خلال ساعات الذروة. يلغي فجوات العرض (الحالة 3)."),
            ("📍 علامات الطابور في المحطات الرئيسية", "رسم مناطق الصعود في قمعون وسيدي سالم. يلغي الاندفاع عند الصعود (الحالة 4)."),
            ("🚐 تمركز لوّاجات في منتصف الخط", "لوّاج واحد لكل دورة ينطلق من أكودة أو ح.سوسة. يحل مشكلة اللوّاجات الممتلئة (الحالة 1)."),
            ("🚌 إصلاح الحافلة = إصلاح اللوّاج", "عدم موثوقية الحافلة يجبر الركاب على اللوّاج. تحسين تكرار الحافلات يقلل مباشرة من الاكتظاظ."),
        ],
    },
}

C = content[lang]

# ── Navigation ────────────────────────────────────────────────
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", C["nav"])

# ══════════════════════════════════════════════════════════════
# PAGE 1 — THE PROBLEM
# ══════════════════════════════════════════════════════════════
if page == C["nav"][0]:

    st.markdown(f"""
    <div class="hero">
        <h1>🚐 {C["title"]}</h1>
        <p>{C["subtitle"]}</p>
    </div>
    """, unsafe_allow_html=True)

    # Live status based on current time
    now = datetime.now(timezone.utc) + timedelta(hours=1)  # Tunisia = UTC+1
    hour = now.hour
    day  = now.weekday()  # 0=Monday

    if hour in range(7, 9) or hour in range(17, 20):
        risk_level = "🔴 HIGH RISK" if lang == "English" else "🔴 RISQUE ÉLEVÉ" if lang == "Français" else "🔴 خطر عالٍ"
        risk_color = "#FEE2E2"
        risk_msg = {
            "English": f"Right now ({now.strftime('%H:%M')}) is peak hour. Expect full louages and long waits.",
            "Français": f"En ce moment ({now.strftime('%H:%M')}) c'est l'heure de pointe. Attendez-vous à des louages complets.",
            "العربية": f"الآن ({now.strftime('%H:%M')}) هي ساعة الذروة. توقع لوّاجات ممتلئة وانتظاراً طويلاً."
        }[lang]
    elif hour in range(12, 14):
        risk_level = "🟢 LOW RISK" if lang == "English" else "🟢 FAIBLE RISQUE" if lang == "Français" else "🟢 خطر منخفض"
        risk_color = "#D1FAE5"
        risk_msg = {
            "English": f"Right now ({now.strftime('%H:%M')}) is the best window. 64% of commuters wait only 5-15 min at midday.",
            "Français": f"En ce moment ({now.strftime('%H:%M')}) c'est la meilleure fenêtre. 64% des navetteurs attendent seulement 5-15 min à midi.",
            "العربية": f"الآن ({now.strftime('%H:%M')}) هو أفضل وقت. 64% من المسافرين ينتظرون 5-15 دقيقة فقط في منتصف النهار."
        }[lang]
    else:
        risk_level = "🟡 MODERATE RISK" if lang == "English" else "🟡 RISQUE MODÉRÉ" if lang == "Français" else "🟡 خطر متوسط"
        risk_color = "#FEF3C7"
        risk_msg = {
            "English": f"Right now ({now.strftime('%H:%M')}) is moderate. Check your commute profile on Page 3.",
            "Français": f"En ce moment ({now.strftime('%H:%M')}) le risque est modéré. Vérifiez votre profil sur la Page 3.",
            "العربية": f"الآن ({now.strftime('%H:%M')}) الخطر متوسط. تحقق من ملفك الشخصي في الصفحة 3."
        }[lang]

    if day == 0:
        risk_msg += " ⚠️ MONDAY — historically the worst day on this corridor (87% of respondents)." if lang == "English" else " ⚠️ LUNDI — historiquement le pire jour (87% des répondants)." if lang == "Français" else " ⚠️ الاثنين — تاريخياً أسوأ يوم في هذا المحور (87% من المستطلعين)."

    st.markdown(f"""
    <div class="status-box" style="background:{risk_color}; border-left: 4px solid #1B2A4A; color: #1B2A4A;">
        <strong>{risk_level}</strong> — {risk_msg}
    </div>
    """, unsafe_allow_html=True)

    # Key stats
    st.markdown(f'<div class="section-title">{C["problem_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#64748B;margin-bottom:24px'>{C['problem_text']}</p>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    stats_nums = ["73%", "68%", "87%", "75%"]
    for col, num, label in zip([col1,col2,col3,col4], stats_nums, C["stats"]):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{num}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # The 4 cases
    st.markdown("---")
    cases_en = [
        ("🔴 Case 1", "#FEE2E2", "#EF4444", "Full louage passes", "The louage arrives but is already carrying 8 passengers. You watch it drive past."),
        ("🟡 Case 2", "#FEF3C7", "#F59E0B", "Wrong-line louage", "A louage passes but it's going to Sahloul, not Beb Bhar. Doesn't help you."),
        ("⚫ Case 3", "#F1F5F9", "#64748B", "No louage at all", "Minutes pass with zero louages. A supply gap — the most frustrating wait."),
        ("🟠 Case 4", "#FED7AA", "#F97316", "Boarding rush", "A louage finally arrives. Everyone rushes. You don't make it. Wait resets."),
    ]
    col1, col2 = st.columns(2)
    for i, (title, bg, border, subtitle, desc) in enumerate(cases_en):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""
            <div class="case-card" style="background:{bg};border-left-color:{border}">
                <strong>{title} — {subtitle}</strong><br>
                <span style="font-size:0.9rem;color:#475569">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

    # Corridor map
    st.markdown("---")
    st.markdown('<div class="section-title">📍 The Corridor</div>', unsafe_allow_html=True)
    corridor_data = pd.DataFrame({
        "Station": ["Kalaa Kebira", "El Warda", "Gamooun", "Rp. Meublatex", "Sidi Salem", "Menchia", "Khzema", "Panorama", "Hospital", "Beb Bhar"],
        "lat": [35.8748, 35.8698, 35.8658, 35.8587, 35.8547, 35.8498, 35.8387, 35.8312, 35.8267, 35.8198],
        "lon": [10.5089, 10.5156, 10.5198, 10.5267, 10.5312, 10.5356, 10.5498, 10.5567, 10.5623, 10.5698],
        "type": ["Origin", "Akouda", "Akouda", "H.Sousse", "H.Sousse", "H.Sousse", "Sousse City", "Sousse City", "Sousse City", "Destination"],
    })
    st.image("images/corridor_map.png", use_column_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 2 — THE DATA
# ══════════════════════════════════════════════════════════════
elif page == C["nav"][1]:

    st.markdown(f'<div class="section-title">📊 {C["nav"][1]}</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B;margin-bottom:24px'>230 real survey responses from daily KK → Beb Bhar commuters.</p>", unsafe_allow_html=True)

    # Wait time distribution
    wait_order = ["less than 5 min", "5-15 min", "15-30 min", "more than 30 min"]
    wait_counts = df["wait_time"].value_counts().reindex(wait_order).reset_index()
    wait_counts.columns = ["Wait Time", "Count"]
    fig1 = px.bar(wait_counts, x="Wait Time", y="Count",
                  color="Count", color_continuous_scale="YlOrRd",
                  title="Wait Time Distribution (n=230)")
    fig1.update_layout(showlegend=False, plot_bgcolor="white")
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        case_data = pd.DataFrame({
            "Case": ["Case 1 Full", "Case 2 Wrong line", "Case 3 No supply", "Case 4 Rush"],
            "Count": [df["case_full"].sum(),
                      df["case"].str.contains("سهلول", na=False).sum(),
                      df["case"].str.contains("لا يمر", na=False).sum(),
                      df["case"].str.contains("يتدافعون", na=False).sum()]
        })
        case_data["Pct"] = (case_data["Count"] / 230 * 100).round(1)
        fig2 = px.bar(case_data, x="Case", y="Count",
                      color="Count", color_continuous_scale="Reds",
                      title="Failure Case Frequency",
                      text=case_data["Pct"].apply(lambda x: f"{x}%"))
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False, plot_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Worst day
        day_order = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
        day_counts = df["worst_day"].value_counts().reindex(day_order).reset_index()
        day_counts.columns = ["Day", "Count"]
        fig3 = px.bar(day_counts, x="Day", y="Count",
                      color="Count", color_continuous_scale="Reds",
                      title="Worst Day for Waiting")
        fig3.update_layout(showlegend=False, plot_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)

    # Bus usage
    bus_counts = df["use_bus"].value_counts().reset_index()
    bus_counts.columns = ["Bus Usage", "Count"]
    fig4 = px.pie(bus_counts, names="Bus Usage", values="Count",
                  title="Bus Usage Among Louage Commuters",
                  color_discrete_sequence=["#1B2A4A", "#D4A017", "#4FC3A1"])
    st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 3 — YOUR COMMUTE
# ══════════════════════════════════════════════════════════════
elif page == C["nav"][2]:

    st.markdown(f'<div class="section-title">🚐 {C["predict_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#64748B;margin-bottom:24px'>{C['predict_desc']}</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    zone_options    = {"القلعة الكبرى / Kalaa Kebira": "Kalaa_Kebira", "أكودة / Akouda": "Akouda", "مدينة سوسة / Sousse City": "Sousse_City"}
    timeslot_options = {
        "05:00–07:00": "الصباح الباكر 05:00–07:00",
        "07:00–09:00": "الصباح 07:00–09:00",
        "09:00–11:00": "الضحى 09:00–11:00",
        "12:00–14:00": "الظهيرة 12:00–14:00",
        "16:00–18:00": "بعد الظهر 16:00–18:00",
        "18:00–20:00": "المساء 18:00–20:00",
    }
    freq_options = {
        "Every day / كل يوم": "كل يوم",
        "3-5x per week / 3 الى 5 مرات": "3 الى 5 مرات",
        "1-2x per week / مرة أو مرتين": "مرة أو مرتين",
    }

    with col1:
        zone_display = st.selectbox(C["zone_label"], list(zone_options.keys()))
    with col2:
        time_display = st.selectbox(C["time_label"], list(timeslot_options.keys()))
    with col3:
        freq_display = st.selectbox(C["freq_label"], list(freq_options.keys()))

    if st.button(C["predict_btn"], type="primary"):

        zone_val = zone_options[zone_display]
        time_val = timeslot_options[time_display]
        freq_val = freq_options[freq_display]

        try:
            zone_enc = le_zone.transform([zone_val])[0]
            time_enc = le_time.transform([time_val])[0]
            freq_enc = le_freq.transform([freq_val])[0]

            X_input = pd.DataFrame([[zone_enc, time_enc, freq_enc]],
                                    columns=["zone_enc","time_slot_enc","frequency_enc"])

            wait_pred  = le_wait.inverse_transform(rf_wait.predict(X_input))[0]
            case1_prob = rf_case1.predict_proba(X_input)[0][1]

            # Risk level
            if case1_prob >= 0.75 or wait_pred == "more than 30 min":
                risk_class = "risk-high"
                risk_icon  = "🔴"
                risk_text  = "HIGH RISK" if lang=="English" else "RISQUE ÉLEVÉ" if lang=="Français" else "خطر عالٍ"
            elif case1_prob >= 0.55 or wait_pred == "15-30 min":
                risk_class = "risk-medium"
                risk_icon  = "🟡"
                risk_text  = "MODERATE RISK" if lang=="English" else "RISQUE MODÉRÉ" if lang=="Français" else "خطر متوسط"
            else:
                risk_class = "risk-low"
                risk_icon  = "🟢"
                risk_text  = "LOW RISK" if lang=="English" else "FAIBLE RISQUE" if lang=="Français" else "خطر منخفض"

            col_r1, col_r2, col_r3 = st.columns(3)

            with col_r1:
                st.markdown(f"""
                <div class="{risk_class}">
                    <div style="font-size:2rem">{risk_icon}</div>
                    <div style="font-size:1.1rem;font-weight:700">{risk_text}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_r2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{wait_pred.replace("more than", ">").replace("less than", "<")}</div>
                    <div class="stat-label">Predicted wait time</div>
                </div>
                """, unsafe_allow_html=True)

            with col_r3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{case1_prob:.0%}</div>
                    <div class="stat-label">Chance of full louage</div>
                </div>
                """, unsafe_allow_html=True)

            # Best window for their zone
            st.markdown("---")
            st.markdown(f'<div class="section-title">⏰ {C["best_window"]}</div>', unsafe_allow_html=True)

            time_slots_all = list(timeslot_options.values())
            best_data = []
            for ts in time_slots_all:
                try:
                    te = le_time.transform([ts])[0]
                    xi = pd.DataFrame([[zone_enc, te, freq_enc]],
                                       columns=["zone_enc","time_slot_enc","frequency_enc"])
                    cp = rf_case1.predict_proba(xi)[0][1]
                    wp = le_wait.inverse_transform(rf_wait.predict(xi))[0]
                    best_data.append({"Time": list(timeslot_options.keys())[time_slots_all.index(ts)],
                                      "Case1 Risk": cp, "Wait": wp})
                except:
                    pass

            best_df = pd.DataFrame(best_data).sort_values("Case1 Risk")
            fig_best = px.bar(best_df, x="Time", y="Case1 Risk",
                              color="Case1 Risk", color_continuous_scale="RdYlGn_r",
                              title=f"Case 1 Risk by Time Slot — {zone_display}",
                              text=best_df["Case1 Risk"].apply(lambda x: f"{x:.0%}"))
            fig_best.update_traces(textposition="outside")
            fig_best.update_layout(showlegend=False, plot_bgcolor="white", yaxis_tickformat=".0%")
            st.plotly_chart(fig_best, use_container_width=True)

            # Peer comparison
            st.markdown("---")
            peer_mask = df["zone"] == zone_display
            peer_df   = df[peer_mask]
            if len(peer_df) > 0:
                peer_wait = peer_df["wait_time"].value_counts(normalize=True) * 100
                st.markdown(f"**Among {len(peer_df)} survey respondents from {zone_display}:**")
                for wt in ["more than 30 min", "15-30 min", "5-15 min", "less than 5 min"]:
                    pct = peer_wait.get(wt, 0)
                    color = "#EF4444" if wt == "more than 30 min" else "#F59E0B" if wt == "15-30 min" else "#10B981"
                    st.markdown(f"<span style='color:{color};font-weight:600'>{pct:.0f}%</span> waited **{wt}**", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Prediction error: {e}")

# ══════════════════════════════════════════════════════════════
# PAGE 4 — THE FIX
# ══════════════════════════════════════════════════════════════
elif page == C["nav"][3]:

    st.markdown(f'<div class="section-title">💡 {C["fix_title"]}</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B;margin-bottom:32px'>Data-backed interventions — ordered by feasibility and impact.</p>", unsafe_allow_html=True)

    for i, (title, desc) in enumerate(C["solutions"]):
        st.markdown(f"""
        <div class="case-card" style="background:#F8FAFC;border-left-color:#1B2A4A;margin-bottom:16px">
            <strong style="font-size:1.05rem">{title}</strong><br>
            <span style="color:#475569">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

    # Impact simulator
    st.markdown("---")
    st.markdown('<div class="section-title">🔬 Impact Simulator</div>', unsafe_allow_html=True)
    st.markdown("Simulate what happens if we add more louages during peak hours.")

    extra_louages = st.slider("Extra louages added at KK during 07:00–09:00", 0, 5, 0)
    baseline_case1 = 0.60

    simulated_risk = max(0.15, baseline_case1 - (extra_louages * 0.08))
    improvement    = (baseline_case1 - simulated_risk) * 100

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Baseline Case 1 Risk (KK morning)", f"{baseline_case1:.0%}")
    with col2:
        st.metric("Simulated Risk", f"{simulated_risk:.0%}", delta=f"-{improvement:.0f}%")
    with col3:
        st.metric("Extra louages added", extra_louages)

    fig_sim = go.Figure(go.Indicator(
        mode="gauge+number",
        value=simulated_risk * 100,
        title={"text": "Predicted Case 1 Risk (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#1B2A4A"},
            "steps": [
                {"range": [0, 40],  "color": "#D1FAE5"},
                {"range": [40, 70], "color": "#FEF3C7"},
                {"range": [70, 100],"color": "#FEE2E2"},
            ],
            "threshold": {"line": {"color": "#EF4444","width": 4}, "value": 60}
        }
    ))
    st.plotly_chart(fig_sim, use_container_width=True)

    # Research note
    st.markdown("---")
    st.info("📋 This study is based on 230 survey responses from daily KK → Beb Bhar commuters. Data collected 2025. Conducted independently by Mariem Belaid, CS student, Sousse.")
    st.markdown("[📂 View full research on GitHub](https://github.com/marymaryem/mobility-in-sousse-research)")

