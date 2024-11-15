import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re
import os
import matplotlib.font_manager as fm
import numpy as np

# macOS 中文字体设置
plt.rcParams['font.sans-serif'] = ['PingFang HK', 'Arial Unicode MS']  # macOS 常用中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 如果上面的字体设置不起作用，可以尝试使用以下函数来设置字体
def set_macos_chinese_font():
    # 获取系统字体列表
    fonts = [f.name for f in fm.fontManager.ttflist]
    
    # macOS 常用中文字体优先级
    chinese_fonts = [
        'PingFang HK',
        'Arial Unicode MS',
        'Heiti TC',
        'Hiragino Sans GB',
        'STHeiti',
        'Microsoft YaHei'
    ]
    
    # 查找第一个可用的中文字体
    for font in chinese_fonts:
        if font in fonts:
            plt.rcParams['font.sans-serif'] = [font]
            print(f"使用字体: {font}")
            break
    
    plt.rcParams['axes.unicode_minus'] = False

def save_statistics_to_csv(year_counts, month_counts, day_counts, hour_counts, output_dir):
    """
    将统计结果保存到CSV文件
    """
    try:
        # 创建统计数据的DataFrame
        stats_data = {
            '年份': year_counts.index,
            '年份数据量': year_counts.values,
            '月份': month_counts.index,
            '月份数据量': month_counts.values,
            '日期': day_counts.index,
            '日期数据量': day_counts.values,
            '小时': hour_counts.index,
            '小时数据量': hour_counts.values,
        }
        
        # 找到最长的序列长度
        max_len = max(len(year_counts), len(month_counts), len(day_counts), len(hour_counts))
        
        # 将所有序列补齐到相同长度（用NaN填充）
        for key in stats_data:
            if len(stats_data[key]) < max_len:
                stats_data[key] = pd.Series(list(stats_data[key]) + [None] * (max_len - len(stats_data[key])))
        
        # 创建DataFrame
        stats_df = pd.DataFrame(stats_data)
        
        # 保存到CSV
        stats_path = os.path.join(output_dir, 'date_statistics.csv')
        stats_df.to_csv(stats_path, encoding='utf-8-sig', index=False)
        print(f"统计结果已保存至: {stats_path}")
        
        return stats_path
        
    except Exception as e:
        print(f"保存统计结果时出现错误: {str(e)}")
        return None

def analyze_dates(csv_path, date_column=0, encoding='utf-8'):
    """
    分析CSV文件中的年、月、日分布并生成可视化图表
    """
    try:
        # 设置中文字体
        set_macos_chinese_font()
        
        # 检查文件是否存在
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"找不到CSV文件: {csv_path}")
        
        # 读取CSV文件
        df = pd.read_csv(csv_path, encoding=encoding)
        date_series = df.iloc[:, date_column]
        
        # 提取年、月、日、时
        years = []
        months = []
        days = []
        hours = []
        
        for date_str in date_series:
            # 使用正则表达式匹配年月日时
            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{1,2}):', str(date_str))
            if match:
                years.append(int(match.group(1)))
                months.append(int(match.group(2)))
                days.append(int(match.group(3)))
                hours.append(int(match.group(4)))
        
        if not years:
            print("未找到任何符合格式的日期数据")
            return
        
        # 创建包含年份信息的数据结构
        date_data = pd.DataFrame({
            'year': years,
            'month': months,
            'day': days,
            'hour': hours
        })
        
        # 统计次数
        year_counts = pd.Series(years).value_counts().sort_index()
        hour_counts = pd.Series(hours).value_counts().sort_index()
        
        # 按年份分组统计月份和日期
        month_by_year = {}
        day_by_year = {}
        unique_years = sorted(set(years))
        
        # 创建月份和日期的数据矩阵
        month_matrix = np.zeros((len(unique_years), 12))
        day_matrix = np.zeros((len(unique_years), 31))
        
        for i, year in enumerate(unique_years):
            year_data = date_data[date_data['year'] == year]
            month_counts = year_data['month'].value_counts()
            day_counts = year_data['day'].value_counts()
            
            # 填充月份数据
            for month, count in month_counts.items():
                month_matrix[i, month-1] = count
            
            # 填充日期数据
            for day, count in day_counts.items():
                day_matrix[i, day-1] = count
        
        # 创建子图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 15))
        
        # 1. 年份统计图
        year_counts.plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_title('年份数据分布统计', fontsize=14, pad=10)
        ax1.set_xlabel('年份', fontsize=12)
        ax1.set_ylabel('数据条数', fontsize=12)
        for i, v in enumerate(year_counts):
            ax1.text(i, v, str(v), ha='center', va='bottom', fontsize=10)
        
        # 2. 月份统计图（堆叠式）
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_years)))
        bottom = np.zeros(12)
        
        for i, year in enumerate(unique_years):
            bars = ax2.bar(range(1, 13), month_matrix[i], bottom=bottom,
                          label=f'{year}年', color=colors[i])
            
            # 更新底部位置
            bottom += month_matrix[i]
            
            # 添加数值标签
            for j, bar in enumerate(bars):
                height = bar.get_height()
                if height > 0:  # 只显示非零值
                    ax2.text(bar.get_x() + bar.get_width()/2,
                            bar.get_y() + height/2,
                            str(int(height)), ha='center', va='center',
                            fontsize=8, color='black')
        
        ax2.set_title('月份数据分布统计（按年份堆叠）', fontsize=14, pad=10)
        ax2.set_xlabel('月份', fontsize=12)
        ax2.set_ylabel('数据条数', fontsize=12)
        ax2.set_xticks(range(1, 13))
        ax2.legend()
        
        # 3. 日期统计图（堆叠式）
        bottom = np.zeros(31)
        
        for i, year in enumerate(unique_years):
            bars = ax3.bar(range(1, 32), day_matrix[i], bottom=bottom,
                          label=f'{year}年', color=colors[i])
            
            # 更新底部位置
            bottom += day_matrix[i]
            
            # 添加数值标签
            for j, bar in enumerate(bars):
                height = bar.get_height()
                if height > 0:  # 只显示非零值
                    ax3.text(bar.get_x() + bar.get_width()/2,
                            bar.get_y() + height/2,
                            str(int(height)), ha='center', va='center',
                            fontsize=8, color='black')
        
        ax3.set_title('日期数据分布统计（按年份堆叠）', fontsize=14, pad=10)
        ax3.set_xlabel('日期', fontsize=12)
        ax3.set_ylabel('数据条数', fontsize=12)
        ax3.set_xticks(range(1, 32))
        ax3.legend()
            
        # 4. 小时统计图
        hour_counts.plot(kind='bar', ax=ax4, color='purple')
        ax4.set_title('24小时数据分布统计', fontsize=14, pad=10)
        ax4.set_xlabel('小时', fontsize=12)
        ax4.set_ylabel('数据条数', fontsize=12)
        for i, v in enumerate(hour_counts):
            ax4.text(i, v, str(v), ha='center', va='bottom', fontsize=10)
        
        # 调整所有子图的x轴标签角度
        for ax in [ax1, ax2, ax3, ax4]:
            ax.tick_params(axis='x', rotation=45)
        
        # 打印统计结果
        print("\n年份统计结果：")
        for year, count in year_counts.items():
            print(f"{year}年: {count}条数据")
            
        print("\n月份统计结果：")
        for month, count in month_counts.items():
            print(f"{month}月: {count}条数据")
            
        print("\n日期统计结果：")
        for day, count in day_counts.items():
            print(f"{day}日: {count}条数据")
            
        print("\n小时统计结果：")
        for hour, count in hour_counts.items():
            print(f"{hour}时: {count}条数据")
        
        # 保存统计结果到CSV
        output_dir = os.path.dirname(csv_path)
        save_statistics_to_csv(year_counts, month_counts, day_counts, hour_counts, output_dir)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        plot_path = os.path.join(output_dir, 'date_distribution.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"\n统计图表已保存至: {plot_path}")
        
        # 显示图表
        plt.show()
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")

if __name__ == "__main__":
    print("CSV文件日期分析工具")
    
    # 获取CSV文件路径
    while True:
        csv_path = input("请输入CSV文件路径：").strip()
        if csv_path:
            if not os.path.exists(csv_path):
                print("文件不存在，请重新输入")
                continue
            break
        print("路径不能为空，请重新输入")
    
    # 获取日期列索引
    while True:
        try:
            date_column = input("请输入日期所在列的索引（第一列为0，直接回车默认为0）：").strip()
            if not date_column:
                date_column = 0
            else:
                date_column = int(date_column)
            break
        except ValueError:
            print("请输入有效的数字")
    
    # 分析数据
    analyze_dates(csv_path, date_column) 