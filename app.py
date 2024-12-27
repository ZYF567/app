import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import pyecharts
from pyecharts.charts import WordCloud, Bar, Pie, Line, HeatMap, Scatter
from pyecharts import options as opts
from pyecharts.globals import ThemeType

# 设置 pyecharts 的全局配置项
pyecharts.options.GLOBAL_INIT_OPTIONS = pyecharts.options.InitOpts(
    theme=ThemeType.LIGHT,  # 设置主题
    font_family='SimHei'  # 设置字体为黑体
)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

def fetch_article(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果请求失败，抛出异常

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找 <article> 标签，其中 class="article" 和 id="mp-editor"
        article = soup.find('article', class_='article', id='mp-editor')

        # 如果找到了文章内容，则返回其文本内容，否则返回错误提示
        if article:
            return article.get_text(separator="\n", strip=True)  # 提取纯文本
        else:
            return "无法找到文章内容，页面结构可能有所不同。"

    except requests.exceptions.RequestException as e:
        # 捕获请求异常并返回错误信息
        return f"请求失败: {e}"

# 对文本进行分词并统计词频
def process_text_for_frequency(text):
    # 使用 jieba 分词
    words = jieba.cut(text)

    # 过滤掉无意义的单词（如：空格、数字、标点等）
    filtered_words = [word for word in words if
                      len(word) > 1 and word.strip() not in ['\n', ' ', '。', ',', '，', '！', '：', '；', '(', ')', '“',
                                                             '”']]

    # 统计词频
    word_counts = Counter(filtered_words)

    # 返回所有词频统计结果
    return word_counts

# 创建词云图
def create_wordcloud(words, frequencies):
    wordcloud = WordCloud()
    wordcloud.add("", [list(z) for z in zip(words, frequencies)], word_size_range=[20, 100])
    wordcloud.render_notebook()

# 创建柱状图
def create_bar_chart(data):
    bar = Bar()
    bar.add_xaxis(data['词语'].tolist())
    bar.add_yaxis("频率", data['频率'].tolist())
    bar.set_global_opts(title_opts=opts.TitleOpts(title="词频柱状图"))
    bar.render_notebook()

# 创建饼图
def create_pie_chart(data):
    pie = Pie()
    pie.add("", [list(z) for z in zip(data['词语'].tolist(), data['频率'].tolist())])
    pie.set_global_opts(title_opts=opts.TitleOpts(title="词频饼图"))
    pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    st_pie = pyecharts.charts.Pie(init_opts=opts.InitOpts(width="1000px", height="600px"))
    st_pie.add("", [list(z) for z in zip(data['词语'].tolist(), data['频率'].tolist())])
    st_pie.set_global_opts(title_opts=opts.TitleOpts(title="词频饼图"))
    st_pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    st_pie.render_notebook()

# 创建折线图
def create_line_chart(data):
    line = Line()
    line.add_xaxis(data['词语'].tolist())
    line.add_yaxis("频率", data['频率'].tolist())
    line.set_global_opts(title_opts=opts.TitleOpts(title="词频折线图"))
    line.render_notebook()

# 创建热力图
def create_heatmap(data):
    heatmap = HeatMap()
    data = data.pivot("词语", "频率", "频率")
    heatmap.add_xaxis(data.index.tolist())
    heatmap.add_yaxis("频率", data.columns.tolist(), data.values.tolist())
    heatmap.set_global_opts(title_opts=opts.TitleOpts(title="热力图"))
    heatmap.render_notebook()

# 创建散点图
def create_scatter_plot(data):
    scatter = Scatter()
    scatter.add_xaxis(data['词语'].tolist())
    scatter.add_yaxis("频率", data['频率'].tolist())
    scatter.set_global_opts(title_opts=opts.TitleOpts(title="词频散点图"))
    scatter.render_notebook()

# 主函数
def main():
    st.title("文章词频分析")

    # 文章URL输入框
    url = st.text_input("请输入文章URL:")

    if url:
        # 抓取文章内容
        article_content = fetch_article(url)

        # 如果抓取失败，则显示错误信息
        if "请求失败" in article_content or "无法找到" in article_content:
            st.error(article_content)
            return

        # 显示全文
        st.write("### 文章全文")
        st.text_area("全文显示", value=article_content, height=300)

        # 分词并统计词频
        word_freq_counts = process_text_for_frequency(article_content)

        # 将词频转换为 pandas DataFrame
        word_freq_df = pd.DataFrame(list(word_freq_counts.items()), columns=['词语', '频率']).sort_values(by='频率', ascending=False)

        # 显示所有词频统计结果
        st.write("### 所有词频统计结果")
        st.dataframe(word_freq_df)

        # 获取词频排名前20的词汇
        top_20_word_freq_df = pd.DataFrame(list(word_freq_counts.most_common(20)), columns=['词语', '频率'])

        # 显示词频 Top 20 表格
        st.write("### 词频 Top 20")
        st.dataframe(top_20_word_freq_df)

        # 侧边栏：选择图形类型和词频数量
        chart_type = st.sidebar.selectbox(
            "选择图形类型",
            ["词云图", "柱状图", "饼图", "折线图", "热力图", "散点图"]
        )
        top_n = st.sidebar.slider("选择显示的词频数量", min_value=1, max_value=len(word_freq_df), value=20, step=1)

        # 根据选择的词频数量和图形类型绘制相应的图形
        if top_n > 0:
            top_n_word_freq_df = word_freq_df.head(top_n)

            if chart_type == "词云图":
                st.write("### 词云图")
                create_wordcloud(top_n_word_freq_df['词语'].tolist(), top_n_word_freq_df['频率'].tolist())
            elif chart_type == "柱状图":
                st.write("### 词频柱状图")
                create_bar_chart(top_n_word_freq_df)
            elif chart_type == "饼图":
                st.write("### 词频饼图")
                create_pie_chart(top_n_word_freq_df)
            elif chart_type == "折线图":
                st.write("### 词频折线图")
                create_line_chart(top_n_word_freq_df)
            elif chart_type == "热力图":
                st.write("### 热力图")
                create_heatmap(top_n_word_freq_df)
            elif chart_type == "散点图":
                st.write("### 词频散点图")
                create_scatter_plot(top_n_word_freq_df)

if __name__ == "__main__":
    main()
