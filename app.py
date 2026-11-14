import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Что сажать? Сокулук", page_icon="🌾", layout="wide")

# ---------- Цвета (одни и те же везде) ----------
GREEN, WHEAT, BG = "#2F5D3A", "#C99A2E", "#FAF7F0"
SC = {"dry": "#B5573A", "typ": "#5B7C99", "wet": "#3E8E5A", "cold": "#7B5EA7"}
SC_NAME = {"dry": "Сухой год", "typ": "Типичный", "wet": "Влажный"}

# ---------- Настраиваемые пороги ----------
DRY_LIMIT_MM = 100   # вегетация меньше этого = сухой год
WET_LIMIT_MM = 250   # вегетация больше этого = влажный год

# ---------- Данные NASA POWER 2015-2024 (из задания) ----------
CLIMATE = pd.DataFrame({
    "year": range(2015, 2025),
    "precip_year": [431.8, 599.1, 381.3, 359.8, 367.1, 296.2, 287.3, 404.3, 203.5, 313.8],
    "precip_veg": [172.4, 327.0, 226.9, 153.5, 199.1, 183.2, 97.7, 144.3, 71.9, 144.6],
    "hot_days": [50, 20, 43, 36, 44, 33, 51, 34, 55, 40],
    "frost_days": [2, 0, 5, 0, 0, 2, 4, 0, 1, 1],
})
LAT, LON = 42.87, 74.30

# ---------- ЗАГЛУШКА: оценки заменит движок из этапа 3 ----------
ROTATIONS = [
    {"name": "Вариант А", "crops": "🌾 Пшеница → 🫘 Фасоль → 🌻 Подсолнечник", "dry": 62, "typ": 74, "wet": 70},
    {"name": "Вариант Б", "crops": "🌿 Люцерна → 🌾 Ячмень → 🥔 Картофель", "dry": 55, "typ": 80, "wet": 85},
    {"name": "Вариант В", "crops": "🌽 Кукуруза → 🌾 Пшеница → 🫘 Фасоль", "dry": 38, "typ": 72, "wet": 88},
]
for r in ROTATIONS:
    r["worst"] = min(r["dry"], r["typ"], r["wet"])
ROTATIONS.sort(key=lambda r: r["worst"], reverse=True)

# ---------- Язык (заголовки; кыргызский проверить носителем) ----------
LANG = {
    "Русский": "Осадки в Сокулуке за вегетацию: от {lo} до {hi} мм. Что сажать?",
    "Кыргызча": "Сокулукта вегетация убагындагы жаан-чачын: {lo} мм ден {hi} мм ге чейин. Эмне эгебиз?",
    "English": "Growing-season rainfall in Sokuluk: {lo} to {hi} mm. What to plant?",
}

st.markdown(
    f"""<style>
    .block-container {{padding-top: 1.5rem;}}
    h1 {{color:{GREEN}; font-size:2rem !important;}}
    .badge {{display:inline-block; padding:2px 10px; border-radius:12px; font-size:0.75rem; margin-right:6px;}}
    .nasa {{background:{GREEN}; color:white;}}
    .ext {{background:{WHEAT}; color:#2B2B2B;}}
    .stub {{background:#DDD; color:#555;}}
    .big {{font-size:2.2rem; font-weight:700; color:{GREEN}; line-height:1;}}
    .small {{font-size:0.85rem; color:#777;}}
    </style>""",
    unsafe_allow_html=True,
)

# ---------- Шапка ----------
top_l, top_r = st.columns([5, 1])
lang = top_r.selectbox("Язык", list(LANG), label_visibility="collapsed")
lo, hi = CLIMATE.precip_veg.min(), CLIMATE.precip_veg.max()
top_l.title("🌾 " + LANG[lang].format(lo=round(lo), hi=round(hi)))
st.markdown(
    '<span class="badge nasa">Данные NASA POWER</span>'
    '<span class="badge ext">Внешний источник: SoilGrids</span>'
    '<span class="badge stub">Оценки: демо-заглушка</span>',
    unsafe_allow_html=True,
)

# ---------- Первый экран: ввод слева, результат справа ----------
left, right = st.columns([1, 2.4], gap="large")

with left:
    st.subheader("Ваше хозяйство")
    water = st.radio("Доступность воды для полива", ["Хорошая", "Ограниченная"], horizontal=True)
    st.caption("NASA каналы и орошение не видит, поэтому воду указываете вы.")
    st.markdown("**Что для вас важнее**")
    w_water = st.slider("💧 Экономия воды", 0, 10, 5)
    w_soil = st.slider("🌱 Плодородие почвы", 0, 10, 5)
    w_income = st.slider("💰 Доход", 0, 10, 5)
    w_risk = st.slider("🛡️ Устойчивость к риску", 0, 10, 5)
    organic = st.number_input("Органика почвы, % (по желанию)", 0.0, 10.0, 3.1, 0.1,
                              help="SoilGrids даёт ~3.1 %, но это модель и может быть завышено.")

with right:
    st.subheader("Три варианта севооборота на 3 года")
    cols = st.columns(3)
    for i, (c, r) in enumerate(zip(cols, ROTATIONS)):
        with c.container(border=True):
            st.markdown(("🥇 " if i == 0 else "") + f"**{r['name']}**")
            st.markdown(r["crops"])
            st.markdown(f'<div class="big">{r["worst"]}</div>'
                        '<div class="small">в худшем сценарии (главный показатель устойчивости)</div>',
                        unsafe_allow_html=True)
            st.markdown(" ".join(f"<span style='color:{SC[k]}'>●</span> {r[k]}" for k in ("dry", "typ", "wet")),
                        unsafe_allow_html=True)
    st.caption("Баллы 0-100. Сейчас это заглушка: настоящие оценки придут из движка (этап 3).")

    # ---------- График по сценариям ----------
    fig, ax = plt.subplots(figsize=(8, 3.2))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    width = 0.25
    for j, k in enumerate(("dry", "typ", "wet")):
        xs = [i + (j - 1) * width for i in range(len(ROTATIONS))]
        ax.bar(xs, [r[k] for r in ROTATIONS], width, color=SC[k], label=SC_NAME[k])
    ax.set_xticks(range(len(ROTATIONS)))
    ax.set_xticklabels([r["name"] for r in ROTATIONS])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Баллы")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    st.pyplot(fig)

# ---------- Вероятность: частота по 10 годам, не прогноз ----------
n = len(CLIMATE)
n_dry = int((CLIMATE.precip_veg < DRY_LIMIT_MM).sum())
n_wet = int((CLIMATE.precip_veg > WET_LIMIT_MM).sum())
st.subheader("Как часто так бывает")
m1, m2, m3 = st.columns(3)
m1.metric("Сухие годы", f"{n_dry} из {n}", f"вегетация < {DRY_LIMIT_MM} мм", delta_color="off")
m2.metric("Типичные годы", f"{n - n_dry - n_wet} из {n}", "между порогами", delta_color="off")
m3.metric("Влажные годы", f"{n_wet} из {n}", f"вегетация > {WET_LIMIT_MM} мм", delta_color="off")
st.caption("Это доля лет за 2015-2024, а не прогноз на будущий сезон. Десять лет это мало для точной вероятности.")

# ---------- Карта ----------
with st.expander("📍 Участок на карте", expanded=True):
    st.map(pd.DataFrame({"lat": [LAT], "lon": [LON]}), zoom=9)
    st.caption("Анализ района (сетка NASA POWER около полградуса), а не конкретного поля.")

# ---------- Вкладки для тех, кто хочет глубже ----------
t1, t2, t3, t4 = st.tabs(["📒 Мой урожай", "🛰️ Данные NASA", "🌽 Культуры", "⚠️ Ограничения"])

with t1:
    st.caption("Вносите факт по своим полям. Данные хранятся только в этой сессии.")
    base = pd.DataFrame({"Год": [2024], "Культура": ["Пшеница"], "Площадь, га": [2.0], "Урожай, т/га": [3.5]})
    harvest = st.data_editor(base, num_rows="dynamic", use_container_width=True)
    clean = harvest.dropna()
    if len(clean):
        st.bar_chart(clean.set_index("Год")["Урожай, т/га"], color=GREEN)

with t2:
    fig2, ax2 = plt.subplots(figsize=(8, 3))
    fig2.patch.set_facecolor(BG)
    ax2.set_facecolor(BG)
    demo = {2023: SC["dry"], 2018: SC["typ"], 2016: SC["wet"]}
    ax2.bar(CLIMATE.year, CLIMATE.precip_veg, color=[demo.get(y, "#CFC8B8") for y in CLIMATE.year])
    ax2.set_ylabel("Осадки апрель-сентябрь, мм")
    ax2.set_xticks(CLIMATE.year)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    st.pyplot(fig2)
    st.caption("Цветом выделены демо-годы: 2023 сухой, 2018 типичный, 2016 влажный. "
               "Сухие годы совпадают с жаркими (2023: 55 жарких дней).")
    st.dataframe(CLIMATE.rename(columns={
        "year": "Год", "precip_year": "Осадки за год, мм", "precip_veg": "Осадки за вегетацию, мм",
        "hot_days": "Дней > 35 °C", "frost_days": "Заморозки апр-май, дней"}), hide_index=True)
    st.caption("Цифра про жаркие дни может быть завышена из-за грубой сетки, нужна проверка. "
               "SMAP, SRTM и MODIS NDVI ещё собираем.")

with t3:
    st.info("Здесь будет таблица культур из этапа 1 (CSV).")

with t4:
    st.markdown(
        "- Это анализ района, а не конкретного поля.\n"
        "- NASA POWER: сетка около полградуса. SMAP и IMERG: километры.\n"
        "- SoilGrids это модель, не NASA и не замер. Органику лучше ввести вручную.\n"
        "- Орошение и каналы NASA не видит: воду вводит фермер.\n"
        "- Значения культур и пороги правил это допущения, их нужно проверить у агронома.\n"
        "- Оценки на экране сейчас демо-заглушка."
    )
