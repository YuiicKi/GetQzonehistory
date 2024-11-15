import pandas as pd
import os
from pathlib import Path

def excel_to_csv(excel_path, output_dir=None, encoding='utf-8'):
    """
    将Excel文件转换为CSV文件
    
    参数:
        excel_path: Excel文件路径
        output_dir: 输出目录路径（可选，默认与Excel文件相同目录）
        encoding: CSV文件编码（默认utf-8）
    
    返回:
        转换后的CSV文件路径
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"找不到Excel文件: {excel_path}")
            
        # 获取文件名（不含扩展名）
        file_name = Path(excel_path).stem
        
        # 如果未指定输出目录，使用Excel文件所在目录
        if output_dir is None:
            output_dir = os.path.dirname(excel_path)
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建输出文件路径
        csv_path = os.path.join(output_dir, f"{file_name}.csv")
        
        # 读取Excel文件
        df = pd.read_excel(excel_path)
        
        # 将数据框保存为CSV
        df.to_csv(csv_path, encoding=encoding, index=False)
        
        print(f"转换成功！CSV文件已保存至: {csv_path}")
        return csv_path
        
    except Exception as e:
        print(f"转换过程中出现错误: {str(e)}")
        return None

def batch_convert(input_dir, output_dir=None, encoding='utf-8'):
    """
    批量转换目录下的所有Excel文件
    
    参数:
        input_dir: 输入目录路径
        output_dir: 输出目录路径（可选）
        encoding: CSV文件编码（默认utf-8）
    """
    try:
        # 支持的Excel文件扩展名
        excel_extensions = ['.xlsx', '.xls']
        
        # 获取目录下所有Excel文件
        excel_files = []
        for ext in excel_extensions:
            excel_files.extend(Path(input_dir).glob(f"*{ext}"))
        
        if not excel_files:
            print(f"在 {input_dir} 中未找到Excel文件")
            return
        
        # 转换每个文件
        for excel_file in excel_files:
            excel_to_csv(str(excel_file), output_dir, encoding)
            
    except Exception as e:
        print(f"批量转换过程中出现错误: {str(e)}")

if __name__ == "__main__":
    # 使用示例
    print("Excel转CSV工具")
    print("请选择操作模式：")
    print("1. 转换单个文件")
    print("2. 批量转换目录")
    
    choice = input("请输入选项（1或2）：").strip()
    
    if choice == "1":
        excel_path = input("请输入Excel文件路径：").strip()
        output_dir = input("请输入输出目录路径（直接回车使用相同目录）：").strip()
        output_dir = output_dir if output_dir else None
        excel_to_csv(excel_path, output_dir)
    
    elif choice == "2":
        input_dir = input("请输入Excel文件所在目录路径：").strip()
        output_dir = input("请输入输出目录路径（直接回车使用相同目录）：").strip()
        output_dir = output_dir if output_dir else None
        batch_convert(input_dir, output_dir)
    
    else:
        print("无效的选项！") 