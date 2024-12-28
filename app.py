import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import numpy as np
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import os

matplotlib.rcParams['font.family'] = 'SimHei'
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

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
def create_wordcloud(words):
    fig, ax = plt.subplots(figsize=(10, 5))
    # 指定字体文件的路径
    font_path = 'SimHei.ttf'  # 假设字体文件已经上传到应用根目录
    if not os.path.isfile(font_path):
        st.error("字体文件SimHei.ttf不存在，请上传字体文件到应用根目录。")
        return
    wordcloud = WordCloud(font_path=font_path, width=800, height=400).generate(' '.join(words))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

def create_bar_chart(data):
    matplotlib.rcParams['font.family'] = 'SimHei'
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']
    matplotlib.rcParams['axes.unicode_minus'] = False
    if data is None or data.empty:
        print("没有可绘制的数据。")
        return

    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 5))  # 设置图表大小
    sns.barplot(x='词语', y='频率', data=data, palette="viridis")  # 绘制柱状图

    # 设置图表属性
    ax.set_xlabel("词语")  # X轴
    ax.set_ylabel("频率")  # Y轴
    ax.set_title("词频柱状图")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')  # 设置X轴标签的旋转角度和对齐方式

    # 在每个柱子上方显示频率值
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center',
                    fontsize=10, color='black',
                    xytext=(0, 5), textcoords='offset points')

    # 显示图表
    st.pyplot(fig)
    
# 创建饼图
def create_pie_chart(data):
    if data is None or data.empty:
        print("没有可绘制的数据。")
        return

    if data.index.name == '词语':
        data = data.reset_index()

    labels = data['词语']
    sizes = data['频率'].astype(float)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title("词频饼图")
    ax.axis('equal')
    st.pyplot(fig)

# 创建折线图
def create_line_chart(data):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data.index, data.values, marker='o', color='b', linestyle='-', linewidth=2, markersize=8)
    ax.set_xlabel("词语")
    ax.set_ylabel("频率")
    ax.set_title("词频折线图")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)
# 创建热力图
def create_heatmap(data):
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(data, annot=True, cmap="coolwarm", cbar=True, ax=ax)
    ax.set_title("热力图")
    st.pyplot(fig)

# 创建散点图
def create_scatter_plot(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(data.index, data.values, color='r')
    ax.set_xlabel("词语")
    ax.set_ylabel("频率")
    ax.set_title("词频散点图")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)

# 创建条形图
def create_horizontal_bar_chart(data):
    if data is None or data.empty:
        print("没有可绘制的数据。")
        return

    if data.index.name == '词语':
        data = data.reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='频率', y='词语', data=data, palette="muted", orient="h")
    ax.set_xlabel("频率")
    ax.set_ylabel("词语")
    ax.set_title("词频条形图")
    st.pyplot(fig)

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
        word_freq_df = pd.DataFrame(list(word_freq_counts.items()), columns=['词语', '频率']).sort_values(by='频率',
                                                                                                          ascending=False)

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
            ["词云图", "柱状图", "饼图", "折线图", "热力图", "散点图", "条形图"]
        )
        top_n = st.sidebar.slider("选择显示的词频数量", min_value=1, max_value=len(word_freq_df), value=20, step=1)

        # 根据选择的词频数量和图形类型绘制相应的图形
        if top_n > 0:
            top_n_word_freq_df = word_freq_df.head(top_n)

            if chart_type == "词云图":
                st.write("### 词云图")
                create_wordcloud(top_n_word_freq_df['词语'].tolist())
            elif chart_type == "柱状图":
                st.write("### 词频柱状图")
                create_bar_chart(top_n_word_freq_df.set_index('词语'))
            elif chart_type == "饼图":
                st.write("### 词频饼图")
                create_pie_chart(top_n_word_freq_df.set_index('词语'))
            elif chart_type == "折线图":
                st.write("### 词频折线图")
                create_line_chart(top_n_word_freq_df.set_index('词语'))
            elif chart_type == "热力图":
                st.write("### 热力图")
                create_heatmap(top_n_word_freq_df.set_index('词语').T)
            elif chart_type == "散点图":
                st.write("### 词频散点图")
                create_scatter_plot(top_n_word_freq_df.set_index('词语'))
            elif chart_type == "条形图":
                st.write("### 词频条形图")
                create_horizontal_bar_chart(top_n_word_freq_df.set_index('词语'))


if __name__ == "__main__":
    main()
