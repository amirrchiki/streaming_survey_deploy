"""
Опросник: Потребление стримингового видео
Тема №29 учебной практики
Streamlit + Firebase Firestore + Pandas + Plotly
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from collections import Counter

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================
st.set_page_config(
    page_title="Опрос: Потребление стримингового видео",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a5f;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    div[data-testid="stForm"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        background-color: #f8fafc;
    }
    .stButton>button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==================== ИНИЦИАЛИЗАЦИЯ FIREBASE ====================
# Поддерживает: 1) st.secrets (Streamlit Cloud)  2) локальный serviceAccountKey.json  3) демо-режим

def _fix_private_key(d):
    """Приводит private_key к виду с настоящими переносами строк."""
    if not isinstance(d, dict) or "private_key" not in d:
        return d
    pk = d["private_key"]
    if not isinstance(pk, str):
        return d
    # Если ключ пришёл как одна строка с литералами \n
    if "\\n" in pk and "\n" not in pk:
        d = dict(d)
        d["private_key"] = pk.replace("\\n", "\n")
    return d


def init_firebase():
    """Инициализация Firebase. Возвращает (db, ok, error_message)."""
    if firebase_admin._apps:
        try:
            return firestore.client(), True, None
        except Exception as e:
            return None, False, str(e)

    last_error = None

    # --- 1. Secrets: секция [firebase] ---
    try:
        if "firebase" in st.secrets:
            cred_dict = _fix_private_key(dict(st.secrets["firebase"]))
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            return firestore.client(), True, None
    except Exception as e:
        last_error = f"[firebase]: {type(e).__name__}: {e}"

    # --- 2. Secrets: FIREBASE_KEY = '{...json...}' ---
    try:
        if "FIREBASE_KEY" in st.secrets:
            import json
            raw = st.secrets["FIREBASE_KEY"]
            if isinstance(raw, str):
                cred_dict = json.loads(raw)
            else:
                cred_dict = dict(raw)
            cred_dict = _fix_private_key(cred_dict)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            return firestore.client(), True, None
    except Exception as e:
        last_error = f"FIREBASE_KEY: {type(e).__name__}: {e}"

    # --- 3. Локальный файл ---
    key_path = os.getenv("FIREBASE_KEY", "serviceAccountKey.json")
    if os.path.exists(key_path):
        try:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            return firestore.client(), True, None
        except Exception as e:
            last_error = f"local file: {type(e).__name__}: {e}"

    return None, False, last_error


db, FIREBASE_OK, FIREBASE_ERROR = init_firebase()

if not FIREBASE_OK:
    with st.sidebar:
        st.warning(
            "⚠️ Firebase **не подключён**\n\n"
            "Сейчас работает **демо-режим** (данные только в сессии браузера)."
        )
        if FIREBASE_ERROR:
            st.error(f"Ошибка подключения:\n\n`{FIREBASE_ERROR}`")
        st.markdown(
            """
**Как исправить на Streamlit Cloud:**

1. Правый верхний угол → **⋮ → Settings → Secrets**
2. Вставьте ключ в формате TOML (см. инструкцию)
3. **Save** — приложение перезапустится
"""
        )
else:
    st.sidebar.success("✅ Firebase подключён")

# ==================== ЗАГОЛОВОК ====================
st.markdown('<p class="main-header" id="potreblenie-strimingovogo-video">📺 Потребление стримингового видео</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Анонимный опрос среди студентов. Данные используются только в учебных целях.</p>',
    unsafe_allow_html=True
)
st.caption("Тема №29 учебной практики · Streamlit + Firebase")

# ==================== ФОРМА ОПРОСА ====================
with st.form("streaming_survey", clear_on_submit=True):
    st.subheader("1. Профиль респондента")
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Возраст", min_value=14, max_value=60, value=20, step=1)
    with col2:
        gender = st.selectbox("Пол", ["Мужской", "Женский", "Предпочитаю не указывать"])
    with col3:
        course = st.selectbox("Курс обучения", ["1", "2", "3", "4", "Магистратура", "Не студент"])

    st.subheader("2. Платформы и объём потребления")
    platforms = st.multiselect(
        "Какими стриминговыми платформами вы пользуетесь? (можно несколько)",
        ["YouTube", "Netflix", "Кинопоиск HD", "IVI", "Wink", "Okko", "Premier",
         "START", "TV+", "Twitch", "VK Видео", "Другое"],
        default=["YouTube"]
    )

    col_a, col_b = st.columns(2)
    with col_a:
        hours_per_day = st.slider(
            "Сколько часов в среднем в день вы смотрите стриминговое видео?",
            min_value=0.0, max_value=12.0, value=2.0, step=0.5
        )
    with col_b:
        days_per_week = st.slider(
            "Сколько дней в неделю вы обычно смотрите стриминги?",
            min_value=0, max_value=7, value=5, step=1
        )

    content_types = st.multiselect(
        "Какой контент вы смотрите чаще всего?",
        ["Фильмы", "Сериалы", "Видеоблоги / YouTube", "Образовательные видео",
         "Спорт", "Музыкальные клипы", "Подкасты / интервью", "Аниме", "Другое"]
    )

    st.subheader("3. Влияние на учёбу и повседневную жизнь")
    influence = st.radio(
        "Как стриминговое видео влияет на вашу учёбу?",
        ["Сильно мешает (отвлекает)", "Скорее мешает", "Нейтрально / не влияет",
         "Скорее помогает (образовательный контент)", "Сильно помогает"],
        index=2
    )

    multitasking = st.radio(
        "Смотрите ли вы видео параллельно с учёбой / работой?",
        ["Да, часто", "Иногда", "Редко", "Никогда"]
    )

    sleep_impact = st.select_slider(
        "Влияние на качество сна",
        options=["Сильно ухудшает", "Скорее ухудшает", "Не влияет", "Скорее улучшает", "Улучшает"],
        value="Не влияет"
    )

    satisfaction = st.slider(
        "Общая удовлетворённость стриминговыми сервисами (1–10)",
        min_value=1, max_value=10, value=7
    )

    st.subheader("4. Дополнительно")
    reasons = st.multiselect(
        "Основные причины использования стриминга",
        ["Развлечение / отдых", "Обучение и саморазвитие", "Социальное общение (реакции, обсуждения)",
         "Привычка / фон", "Экономия (вместо кинотеатра)", "Доступность контента"]
    )

    comment = st.text_area("Ваш комментарий или пожелания (необязательно)", height=100)

    submitted = st.form_submit_button("Отправить ответы ✅")

# ==================== СОХРАНЕНИЕ ====================
if submitted:
    if not platforms:
        st.warning("Пожалуйста, выберите хотя бы одну платформу.")
    elif not content_types:
        st.warning("Пожалуйста, укажите типы контента.")
    else:
        record = {
            "age": int(age),
            "gender": gender,
            "course": course,
            "platforms": platforms,
            "hours_per_day": float(hours_per_day),
            "days_per_week": int(days_per_week),
            "content_types": content_types,
            "influence": influence,
            "multitasking": multitasking,
            "sleep_impact": sleep_impact,
            "satisfaction": int(satisfaction),
            "reasons": reasons,
            "comment": comment.strip() if comment else "",
            "timestamp": datetime.utcnow().isoformat()
        }

        if FIREBASE_OK and db is not None:
            try:
                db.collection("streaming_responses").add(record)
                st.success("Спасибо! Ваш ответ успешно сохранён в облаке.")
                st.balloons()
            except Exception as e:
                st.error(f"Ошибка сохранения в Firebase: {e}")
        else:
            # Демо-режим: сохраняем в session_state
            if "demo_data" not in st.session_state:
                st.session_state.demo_data = []
            st.session_state.demo_data.append(record)
            st.success("Спасибо! Ответ сохранён в демо-режиме (локально в сессии).")
            st.info("Для постоянной записи добавьте serviceAccountKey.json.")

# ==================== АНАЛИТИКА ====================
st.markdown("---")
show_analytics = st.checkbox("📊 Показать аналитику (режим преподавателя / исследователя)", value=False)

if show_analytics:
    st.header("Аналитическая панель")

    # Загрузка данных
    data = []
    if FIREBASE_OK and db is not None:
        try:
            docs = db.collection("streaming_responses").stream()
            data = [doc.to_dict() for doc in docs]
        except Exception as e:
            st.error(f"Ошибка загрузки из Firebase: {e}")
    elif "demo_data" in st.session_state:
        data = st.session_state.demo_data

    if not data:
        st.info("Пока нет собранных ответов. Заполните форму выше или добавьте ключ Firebase.")
    else:
        df = pd.DataFrame(data)

        # Преобразование timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        # KPI
        st.subheader("Ключевые показатели")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Всего ответов", len(df))
        with k2:
            avg_hours = df["hours_per_day"].mean() if "hours_per_day" in df.columns else 0
            st.metric("Среднее время в день", f"{avg_hours:.1f} ч")
        with k3:
            avg_sat = df["satisfaction"].mean() if "satisfaction" in df.columns else 0
            st.metric("Средняя удовлетворённость", f"{avg_sat:.1f}/10")
        with k4:
            unique_platforms = set()
            if "platforms" in df.columns:
                for p_list in df["platforms"]:
                    if isinstance(p_list, list):
                        unique_platforms.update(p_list)
            st.metric("Уникальных платформ", len(unique_platforms))

        st.markdown("---")

        # Таблица
        st.subheader("Сырые данные (первые 15 записей)")
        display_cols = [c for c in ["age", "gender", "course", "hours_per_day",
                                    "days_per_week", "influence", "satisfaction", "timestamp"]
                        if c in df.columns]
        st.dataframe(df[display_cols].head(15), use_container_width=True)

        # Визуализации
        st.subheader("Визуализация")

        c1, c2 = st.columns(2)

        with c1:
            if "satisfaction" in df.columns:
                fig1 = px.histogram(
                    df, x="satisfaction", nbins=10,
                    title="Распределение удовлетворённости (1–10)",
                    labels={"satisfaction": "Оценка", "count": "Количество"},
                    color_discrete_sequence=["#3b82f6"]
                )
                fig1.update_layout(bargap=0.1)
                st.plotly_chart(fig1, use_container_width=True)

        with c2:
            if "influence" in df.columns:
                infl_counts = df["influence"].value_counts().reset_index()
                infl_counts.columns = ["influence", "count"]
                fig2 = px.pie(
                    infl_counts, names="influence", values="count",
                    title="Влияние стриминга на учёбу",
                    hole=0.35,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)

        with c3:
            if "hours_per_day" in df.columns:
                fig3 = px.histogram(
                    df, x="hours_per_day", nbins=12,
                    title="Распределение времени просмотра (часы/день)",
                    labels={"hours_per_day": "Часы в день"},
                    color_discrete_sequence=["#10b981"]
                )
                st.plotly_chart(fig3, use_container_width=True)

        with c4:
            if "multitasking" in df.columns:
                mt_counts = df["multitasking"].value_counts().reset_index()
                mt_counts.columns = ["multitasking", "count"]
                fig4 = px.bar(
                    mt_counts, x="multitasking", y="count",
                    title="Мультитаскинг: просмотр + учёба",
                    labels={"multitasking": "Частота", "count": "Ответов"},
                    color_discrete_sequence=["#f59e0b"]
                )
                st.plotly_chart(fig4, use_container_width=True)

        # Топ платформ
        if "platforms" in df.columns:
            all_plats = []
            for p in df["platforms"]:
                if isinstance(p, list):
                    all_plats.extend(p)
            if all_plats:
                plat_counts = pd.Series(all_plats).value_counts().reset_index()
                plat_counts.columns = ["platform", "count"]
                fig5 = px.bar(
                    plat_counts, x="count", y="platform", orientation="h",
                    title="Популярность платформ",
                    labels={"platform": "Платформа", "count": "Упоминаний"},
                    color_discrete_sequence=["#8b5cf6"]
                )
                fig5.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig5, use_container_width=True)

        # Топ типов контента
        if "content_types" in df.columns:
            all_ct = []
            for c in df["content_types"]:
                if isinstance(c, list):
                    all_ct.extend(c)
            if all_ct:
                ct_counts = pd.Series(all_ct).value_counts().reset_index()
                ct_counts.columns = ["content", "count"]
                fig6 = px.bar(
                    ct_counts, x="content", y="count",
                    title="Предпочитаемые типы контента",
                    labels={"content": "Тип", "count": "Упоминаний"},
                    color_discrete_sequence=["#ec4899"]
                )
                st.plotly_chart(fig6, use_container_width=True)

        # Экспорт
        st.subheader("Экспорт данных")
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ Скачать CSV",
            data=csv,
            file_name=f"streaming_survey_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

# ==================== FOOTER ====================
st.markdown("---")
st.caption(
    "Учебная практика · Тема №29 «Потребление стримингового видео» · "
    "Streamlit + Firebase Firestore · Данные анонимны"
)
