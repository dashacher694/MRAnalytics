"""
Streamlit дашборд для визуализации метрик MR
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import asyncio
from loguru import logger

from src.core.factory import container
from src.core.logging import setup_logging

setup_logging()

st.set_page_config(page_title="MR Analytics", page_icon="", layout="wide")

# Initialize container


@st.cache_data(ttl=300)
def load_data():
    """Load data from database (cached for 5 minutes)"""
    async def _load():
        async with container.query_uow() as uow:
            metrics = await uow.metrics_repository.get_all()
            return metrics
    
    return asyncio.run(_load())


# Заголовок
st.title(" MR Analytics Dashboard")
st.markdown("  Merge Requests  ")

try:
    metrics = load_data()
    
    if not metrics:
        st.warning("   .  `python run_all.py`")
        st.stop()
    
    # Convert to DataFrame for visualization
    df_all = pd.DataFrame([
        {
            'mr_iid': m.mr_iid,
            'title': m.title,
            'author': m.author,
            'time_to_merge': m.time_to_merge,
            'review_rounds': m.review_rounds,
            'comment_density': m.comment_density,
            'formal_approval': m.formal_approval,
            'response_time_hours': m.response_time_hours,
            'num_comments': m.num_comments,
            'num_approvals': m.num_approvals,
            'web_url': m.web_url,
        }
        for m in metrics
    ])
    
    # Aggregate by author
    df_authors = df_all.groupby('author').agg({
        'mr_iid': 'count',
        'time_to_merge': 'mean',
        'comment_density': 'mean',
        'formal_approval': 'mean',
        'response_time_hours': 'mean',
        'review_rounds': 'mean',
    }).rename(columns={
        'mr_iid': 'total_mrs',
        'time_to_merge': 'avg_time_to_merge',
        'comment_density': 'avg_comment_density',
        'formal_approval': 'formal_approval_rate',
        'response_time_hours': 'avg_response_time',
        'review_rounds': 'avg_review_rounds',
    }).reset_index()
    
except Exception as e:
    logger.exception("Failed to load data")
    st.error(f"Ошибка загрузки данных: {e}")
    st.stop()

# Общая статистика
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Всего MR", len(df_all))
    
with col2:
    avg_time = df_all['time_to_merge'].mean()
    st.metric("Среднее время мержа", f"{avg_time:.1f}ч")
    
with col3:
    avg_comments = df_all['num_comments'].mean()
    st.metric("Среднее комментариев", f"{avg_comments:.1f}")
    
with col4:
    formal_rate = df_all['formal_approval'].mean() * 100
    st.metric("Формальных аппрувов", f"{formal_rate:.1f}%")

st.divider()

# Выбор режима просмотра
view_mode = st.radio(
    "Режим просмотра:",
    ["По авторам", "По MR", "Топ медленных"],
    horizontal=True
)

if view_mode == "По авторам":
    st.subheader("📈 Статистика по авторам")
    
    # График: среднее время мержа по авторам
    fig1 = px.bar(
        df_authors.sort_values('avg_time_to_merge', ascending=False).head(10),
        x='author',
        y='avg_time_to_merge',
        title='Среднее время мержа по авторам (топ-10)',
        labels={'avg_time_to_merge': 'Часы', 'author': 'Автор'},
        color='avg_time_to_merge',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # График: плотность комментариев vs раунды ревью
    fig2 = px.scatter(
        df_authors,
        x='avg_comment_density',
        y='avg_review_rounds',
        size='total_mrs',
        color='author',
        hover_data=['total_mrs', 'avg_time_to_merge'],
        title='Плотность комментариев vs Раунды ревью',
        labels={
            'avg_comment_density': 'Плотность комментариев',
            'avg_review_rounds': 'Раунды ревью'
        }
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Таблица
    st.subheader("Детальная статистика")
    st.dataframe(
        df_authors.style.format({
            'avg_time_to_merge': '{:.1f}',
            'avg_comment_density': '{:.3f}',
            'formal_approval_rate': '{:.2%}',
            'avg_response_time': '{:.1f}',
            'avg_review_rounds': '{:.1f}'
        }),
        use_container_width=True
    )
    
    # Экспорт
    csv = df_authors.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Скачать CSV",
        csv,
        "authors_stats.csv",
        "text/csv"
    )

elif view_mode == "По MR":
    st.subheader("📋 Все Merge Requests")
    
    # Фильтр по автору
    authors = ['Все'] + sorted(df_all['author'].unique().tolist())
    selected_author = st.selectbox("Фильтр по автору:", authors)
    
    df_filtered = df_all if selected_author == 'Все' else df_all[df_all['author'] == selected_author]
    
    # График распределения времени мержа
    fig3 = px.histogram(
        df_filtered,
        x='time_to_merge',
        nbins=20,
        title='Распределение времени мержа',
        labels={'time_to_merge': 'Часы', 'count': 'Количество MR'}
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Таблица MR
    st.dataframe(
        df_filtered[['mr_iid', 'title', 'author', 'time_to_merge', 'review_rounds', 
                     'num_comments', 'formal_approval']].style.format({
            'time_to_merge': '{:.1f}',
        }),
        use_container_width=True
    )
    
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Скачать CSV",
        csv,
        "all_mrs.csv",
        "text/csv"
    )

else:  # Топ медленных
    st.subheader("🐌 Топ-10 самых медленных MR")
    
    df_slow = df_all.nlargest(10, 'time_to_merge')[['mr_iid', 'title', 'author', 'time_to_merge', 'review_rounds', 'num_comments', 'web_url']]
    
    # График
    fig4 = px.bar(
        df_slow,
        x='mr_iid',
        y='time_to_merge',
        title='Самые медленные MR',
        labels={'time_to_merge': 'Часы', 'mr_iid': 'MR ID'},
        color='time_to_merge',
        color_continuous_scale='Reds',
        hover_data=['title', 'author', 'review_rounds']
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    # Таблица с ссылками
    st.dataframe(
        df_slow.style.format({
            'time_to_merge': '{:.1f}',
        }),
        use_container_width=True,
        column_config={
            "web_url": st.column_config.LinkColumn("Ссылка")
        }
    )
    
    # Подозрительные MR (формальные аппрувы)
    st.subheader("⚠️ Подозрительные MR (формальные аппрувы)")
    df_formal = df_all[df_all['formal_approval'] == 1]
    
    if not df_formal.empty:
        st.dataframe(
            df_formal[['mr_iid', 'title', 'author', 'num_approvals', 'num_comments']],
            use_container_width=True
        )
    else:
        st.success("✅ Формальных аппрувов не обнаружено!")

# Футер
st.divider()
st.caption("Данные обновляются при запуске `python run_all.py`")
