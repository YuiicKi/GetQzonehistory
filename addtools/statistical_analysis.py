import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import calendar
import os

# macOS 中文字体设置
plt.rcParams['font.sans-serif'] = ['PingFang HK', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def load_and_prepare_data(csv_path):
    """
    加载并准备数据用于分析
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"加载数据时出现错误: {str(e)}")
        return None

def perform_chi_square_test(df):
    """
    执行卡方独立性检验
    """
    try:
        # 创建月份和数据量的列联表
        month_data = pd.crosstab(df['月份'], df['月份数据量'])
        chi2, p_value = stats.chi2_contingency(month_data)[:2]
        
        print("\n卡方独立性检验结果（月份与数据量）：")
        print(f"卡方统计量: {chi2:.2f}")
        print(f"P值: {p_value:.4f}")
        print(f"结论: {'数据量与月份存在显著关联' if p_value < 0.05 else '数据量与月份无显著关联'}")
        
        return chi2, p_value
    except Exception as e:
        print(f"执行卡方检验时出现错误: {str(e)}")
        return None, None

def perform_anova(df):
    """
    执行单因素方差分析
    """
    try:
        # 按小时分组的数据
        hour_groups = [group for _, group in df.groupby('小时')['小时数据量']]
        
        # 执行单因素方差分析
        f_stat, p_value = stats.f_oneway(*hour_groups)
        
        print("\n单因素方差分析结果（小时与数据量）：")
        print(f"F统计量: {f_stat:.2f}")
        print(f"P值: {p_value:.4f}")
        print(f"结论: {'不同时间段的数据量存在显著差异' if p_value < 0.05 else '不同时间段的数据量无显著差异'}")
        
        return f_stat, p_value
    except Exception as e:
        print(f"执行方差分析时出现错误: {str(e)}")
        return None, None

def perform_time_series_analysis(df, output_dir):
    """
    执行时间序列分析
    """
    try:
        # 准备时间序列数据
        hours_data = df[['小时', '小时数据量']].copy()
        hours_data = hours_data.sort_values('小时')
        
        # 处理缺失值
        hours_data['小时数据量'] = hours_data['小时数据量'].fillna(0)
        
        # 确保有24小时的完整数据
        full_hours = pd.DataFrame({'小时': range(24)})
        hours_data = pd.merge(full_hours, hours_data, on='小时', how='left')
        hours_data['小时数据量'] = hours_data['小时数据量'].fillna(0)
        
        # 创建时间序列
        time_series = pd.Series(hours_data['小时数据量'].values, 
                              index=hours_data['小时'])
        
        # 1. 创建时间序列分析图（4个子图）
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1.1 原始数据折线图
        ax1.plot(time_series.index, time_series.values, 'o-', color='blue', label='原始数据')
        ax1.set_title('24小时数据分布')
        ax1.set_xlabel('小时')
        ax1.set_ylabel('数据量')
        ax1.grid(True)
        ax1.legend()
        
        # 1.2 移动平均
        ma = time_series.rolling(window=3).mean()
        ax2.plot(ma.index, ma.values, 'r-', label='3小时移动平均')
        ax2.set_title('移动平均趋势')
        ax2.set_xlabel('小时')
        ax2.set_ylabel('数据量')
        ax2.grid(True)
        ax2.legend()
        
        # 1.3 数据波动
        std = time_series.rolling(window=3).std()
        ax3.plot(std.index, std.values, 'g-', label='标准差波动')
        ax3.set_title('数据波动性')
        ax3.set_xlabel('小时')
        ax3.set_ylabel('标准差')
        ax3.grid(True)
        ax3.legend()
        
        # 1.4 累计分布
        cumsum = time_series.cumsum()
        ax4.plot(cumsum.index, cumsum.values, 'm-', label='累计分布')
        ax4.set_title('数据累计分布')
        ax4.set_xlabel('小时')
        ax4.set_ylabel('累计数据量')
        ax4.grid(True)
        ax4.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'time_series_analysis.png'))
        
        # 2. 创建分布分析图（箱线图和小提琴图）
        fig2, (ax5, ax6) = plt.subplots(2, 1, figsize=(15, 12))
        
        # 2.1 箱线图
        # 准备数据
        plot_data = pd.DataFrame({
            '小时': range(24),
            '数据量': time_series.values
        })
        
        sns.boxplot(data=plot_data, x='小时', y='数据量', ax=ax5)
        ax5.set_title('各小时数据分布箱线图')
        ax5.set_xlabel('小时')
        ax5.set_ylabel('数据量')
        
        # 2.2 小提琴图
        sns.violinplot(data=plot_data, x='小时', y='数据量', ax=ax6)
        ax6.set_title('各小时数据分布小提琴图')
        ax6.set_xlabel('小时')
        ax6.set_ylabel('数据量')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'distribution_analysis.png'))
        
        # 3. 时段分析
        morning = time_series[6:12].mean()
        afternoon = time_series[12:18].mean()
        evening = time_series[18:24].mean()
        night = time_series[0:6].mean()
        
        # 创建时段分布图
        plt.figure(figsize=(10, 6))
        periods = ['凌晨(0-6点)', '早晨(6-12点)', '下午(12-18点)', '晚上(18-24点)']
        values = [night, morning, afternoon, evening]
        plt.bar(periods, values, color=['purple', 'orange', 'green', 'blue'])
        plt.title('各时段平均数据量分布')
        plt.ylabel('平均数据量')
        plt.xticks(rotation=45)
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'period_analysis.png'))
        
        # 打印统计结果
        print("\n时间序列分析结果：")
        print(f"平均每小时数据量: {time_series.mean():.2f}")
        print(f"最大小时数据量: {time_series.max():.2f}")
        print(f"最小小时数据量: {time_series.min():.2f}")
        print(f"数据量标准差: {time_series.std():.2f}")
        
        print("\n各时段平均数据量：")
        print(f"早晨(6-12点): {morning:.2f}")
        print(f"下午(12-18点): {afternoon:.2f}")
        print(f"晚上(18-24点): {evening:.2f}")
        print(f"凌晨(0-6点): {night:.2f}")
        
        return time_series
        
    except Exception as e:
        print(f"执行时间序列分析时出现错误: {str(e)}")
        return None

def create_correlation_heatmap(df):
    """
    创建相关性热力图
    """
    try:
        # 计算相关系数
        corr_matrix = df[['年份数据量', '月份数据量', '日期数据量', '小时数据量']].corr()
        
        # 创建热力图
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('数据量维度相关性分析')
        
        return corr_matrix
    except Exception as e:
        print(f"创建相关性热力图时出现错误: {str(e)}")
        return None

def main(csv_path):
    """
    主函数，执行所有统计分析
    """
    # 加载数据
    df = load_and_prepare_data(csv_path)
    if df is None:
        return
    
    # 设置输出目录
    output_dir = os.path.dirname(csv_path)
    
    # 1. 执行卡方独立性检验
    chi2, p_value = perform_chi_square_test(df)
    
    # 2. 执行方差分析
    f_stat, p_value = perform_anova(df)
    
    # 3. 创建相关性热力图
    plt.figure(figsize=(10, 8))
    corr_matrix = create_correlation_heatmap(df)
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
    
    # 4. 执行时间序列分析
    time_series = perform_time_series_analysis(df, output_dir)
    
    # 显示所有图表
    plt.show()

if __name__ == "__main__":
    print("统计分析工具")
    
    while True:
        csv_path = input("请输入date_statistics.csv文件路径：").strip()
        if csv_path and os.path.exists(csv_path):
            break
        print("文件不存在，请重新输入")
    
    main(csv_path) 