import pandas as pd
import os
from pathlib import Path

def merge_csv(file1_path, file2_path, output_path=None, merge_type='outer', on=None, encoding='utf-8'):
    """
    合并两个CSV文件
    
    参数:
        file1_path: 第一个CSV文件路径
        file2_path: 第二个CSV文件路径
        output_path: 输出文件路径（可选，默认为第一个文件所在目录下的merged.csv）
        merge_type: 合并方式（'inner', 'outer', 'left', 'right'）
        on: 用于合并的列名（可选，如果不指定则按索引合并）
        encoding: CSV文件编码（默认utf-8）
    
    返回:
        合并后的CSV文件路径
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(file1_path):
            raise FileNotFoundError(f"找不到第一个CSV文件: {file1_path}")
        if not os.path.exists(file2_path):
            raise FileNotFoundError(f"找不到第二个CSV文件: {file2_path}")
            
        # 如果未指定输出路径，使用默认路径
        if output_path is None:
            output_dir = os.path.dirname(file1_path)
            output_path = os.path.join(output_dir, "merged.csv")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 读取CSV文件
        df1 = pd.read_csv(file1_path, encoding=encoding)
        df2 = pd.read_csv(file2_path, encoding=encoding)
        
        # 合并数据框
        if on is not None:
            # 按指定列合并
            merged_df = pd.merge(df1, df2, on=on, how=merge_type)
        else:
            # 按索引合并
            merged_df = pd.merge(df1, df2, left_index=True, right_index=True, how=merge_type)
        
        # 保存合并后的文件
        merged_df.to_csv(output_path, encoding=encoding, index=False)
        
        print(f"合并成功！文件已保存至: {output_path}")
        print(f"合并前：文件1 - {len(df1)}行, 文件2 - {len(df2)}行")
        print(f"合并后：{len(merged_df)}行")
        return output_path
        
    except Exception as e:
        print(f"合并过程中出现错误: {str(e)}")
        return None

def batch_merge(input_dir, output_path=None, merge_type='outer', on=None, encoding='utf-8'):
    """
    批量合并目录下的所有CSV文件
    
    参数:
        input_dir: 输入目录路径
        output_path: 输出文件路径（可选）
        merge_type: 合并方式（'inner', 'outer', 'left', 'right'）
        on: 用于合并的列名（可选）
        encoding: CSV文件编码（默认utf-8）
    """
    try:
        # 获取目录下所有CSV文件
        csv_files = list(Path(input_dir).glob("*.csv"))
        
        if len(csv_files) < 2:
            print(f"在 {input_dir} 中找到的CSV文件少于2个，无法进行合并")
            return
        
        # 读取第一个文件作为基础
        result_df = pd.read_csv(str(csv_files[0]), encoding=encoding)
        print(f"读取第一个文件: {csv_files[0].name}")
        
        # 依次合并其他文件
        for csv_file in csv_files[1:]:
            print(f"正在合并文件: {csv_file.name}")
            df = pd.read_csv(str(csv_file), encoding=encoding)
            
            if on is not None:
                result_df = pd.merge(result_df, df, on=on, how=merge_type)
            else:
                result_df = pd.merge(result_df, df, left_index=True, right_index=True, how=merge_type)
        
        # 如果未指定输出路径，使用默认路径
        if output_path is None:
            output_path = os.path.join(input_dir, "merged_all.csv")
            
        # 保存合并后的文件
        result_df.to_csv(output_path, encoding=encoding, index=False)
        print(f"批量合并成功！文件已保存至: {output_path}")
        print(f"最终文件行数：{len(result_df)}行")
            
    except Exception as e:
        print(f"批量合并过程中出现错误: {str(e)}")

def append_csv(file1_path, file2_path, output_path=None, encoding='utf-8'):
    """
    将第二个CSV文件的内容追加到第一个CSV文件的末尾
    
    参数:
        file1_path: 第一个CSV文件路径
        file2_path: 第二个CSV文件路径
        output_path: 输出文件路径（可选，默认为第一个文件所在目录下的merged.csv）
        encoding: CSV文件编码（默认utf-8）
    
    返回:
        合并后的CSV文件路径
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(file1_path):
            raise FileNotFoundError(f"找不到第一个CSV文件: {file1_path}")
        if not os.path.exists(file2_path):
            raise FileNotFoundError(f"找不到第二个CSV文件: {file2_path}")
            
        # 如果未指定输出路径，使用默认路径
        if output_path is None:
            output_dir = os.path.dirname(file1_path)
            output_path = os.path.join(output_dir, "merged.csv")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 读取CSV文件
        df1 = pd.read_csv(file1_path, encoding=encoding)
        df2 = pd.read_csv(file2_path, encoding=encoding)
        
        # 简单地将两个数据框连接起来
        merged_df = pd.concat([df1, df2], ignore_index=True)
        
        # 保存合并后的文件
        merged_df.to_csv(output_path, encoding=encoding, index=False)
        
        print(f"追加成功！文件已保存至: {output_path}")
        print(f"合并前：文件1 - {len(df1)}行, 文件2 - {len(df2)}行")
        print(f"合并后：{len(merged_df)}行")
        return output_path
        
    except Exception as e:
        print(f"追加过程中出现错误: {str(e)}")
        return None

if __name__ == "__main__":
    print("CSV文件合并工具")
    print("请选择操作模式：")
    print("1. 合并两个文件（按列合并）")
    print("2. 批量合并目录下的所有文件")
    print("3. 追加合并（第二个文件接在第一个文件后面）")
    
    choice = input("请输入选项（1、2或3）：").strip()
    
    if choice == "1":
        # 添加输入验证
        while True:
            file1_path = input("请输入第一个CSV文件路径：").strip()
            if file1_path:
                if not os.path.exists(file1_path):
                    print("文件不存在，请重新输入")
                    continue
                break
            print("路径不能为空，请重新输入")
            
        while True:
            file2_path = input("请输入第二个CSV文件路径：").strip()
            if file2_path:
                if not os.path.exists(file2_path):
                    print("文件不存在，请重新输入")
                    continue
                break
            print("路径不能为空，请重新输入")
        
        output_path = input("请输入输出文件路径（直接回车使用默认路径）：").strip()
        merge_type = input("请输入合并方式（inner/outer/left/right，直接回车使用outer）：").strip()
        on = input("请输入用于合并的列名（多个列用逗号分隔，直接回车则按索引合并）：").strip()
        
        output_path = output_path if output_path else None
        merge_type = merge_type if merge_type else 'outer'
        on = on.split(',') if on else None
        
        merge_csv(file1_path, file2_path, output_path, merge_type, on)
    
    elif choice == "2":
        # 添加输入验证
        while True:
            input_dir = input("请输入CSV文件所在目录路径：").strip()
            if input_dir:
                if not os.path.exists(input_dir):
                    print("目录不存在，请重新输入")
                    continue
                break
            print("路径不能为空，请重新输入")
            
        output_path = input("请输入输出文件路径（直接回车使用默认路径）：").strip()
        merge_type = input("请输入合并方式（inner/outer/left/right，直接回车使用outer）：").strip()
        on = input("请输入用于合并的列名（多个列用逗号分隔，直接回车则按索引合并）：").strip()
        
        output_path = output_path if output_path else None
        merge_type = merge_type if merge_type else 'outer'
        on = on.split(',') if on else None
        
        batch_merge(input_dir, output_path, merge_type, on)
    
    elif choice == "3":
        # 添加输入验证
        while True:
            file1_path = input("请输入第一个CSV文件路径：").strip()
            if file1_path:
                if not os.path.exists(file1_path):
                    print("文件不存在，请重新输入")
                    continue
                break
            print("路径不能为空，请重新输入")
            
        while True:
            file2_path = input("请输入第二个CSV文件路径：").strip()
            if file2_path:
                if not os.path.exists(file2_path):
                    print("文件不存在，请重新输入")
                    continue
                break
            print("路径不能为空，请重新输入")
        
        output_path = input("请输入输出文件路径（直接回车使用默认路径）：").strip()
        output_path = output_path if output_path else None
        
        append_csv(file1_path, file2_path, output_path)
    
    else:
        print("无效的选项！") 