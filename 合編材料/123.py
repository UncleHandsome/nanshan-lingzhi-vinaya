import math
import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd

# ==========================================
# ⚙️ 設定區：每幾個工作表切成一個 .md 檔案？
# ==========================================
SHEETS_PER_FILE = 5  # 👈 可隨意修改這個數字（例如：5 或 10）


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """自動清理 DataFrame：移除空白、浮點數四捨五入、清理欄位名稱"""
    # 刪除整列都是空的、整欄都是空的無效資料
    df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)
    if df.empty:
        return df

    # 清理欄位名稱頭尾空白
    df.columns = [str(col).strip() for col in df.columns]

    # 清理字串資料頭尾空白
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # 浮點數四捨五入（保留 4 位小數，節省 Token）
    float_cols = df.select_dtypes(include=["float"]).columns
    for col in float_cols:
        df[col] = df[col].round(4)

    # NaN 空值轉為空字串
    df = df.fillna("")

    return df


def excel_to_chunked_markdown():
    # 隱藏 tkinter 主視窗
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    print("請在彈出的視窗中選擇 Excel 檔案...")
    file_path = filedialog.askopenfilename(
        title="請選擇要轉換的 Excel 檔案",
        filetypes=[
            ("Excel Files", "*.xlsx *.xls *.xlsm"),
            ("All Files", "*.*"),
        ],
    )

    if not file_path:
        print("❌ 已取消選擇。")
        return

    excel_filename = os.path.basename(file_path)
    base_name = os.path.splitext(file_path)[0]

    print(f"\n正在讀取檔案：{excel_filename}...")
    try:
        sheets = pd.read_excel(file_path, sheet_name=None)
    except Exception as e:
        print(f"❌ 讀取 Excel 失敗：{e}")
        return

    all_sheet_names = list(sheets.keys())
    total_sheets = len(all_sheet_names)
    total_parts = math.ceil(total_sheets / SHEETS_PER_FILE)

    print(f"共偵測到 {total_sheets} 個工作表。")
    print(
        f"將依照每 {SHEETS_PER_FILE} 個工作表進行分割，預計產出 {total_parts} 份 Markdown 檔案。\n"
    )

    # 分批處理
    for part_idx in range(total_parts):
        start_idx = part_idx * SHEETS_PER_FILE
        end_idx = min(start_idx + SHEETS_PER_FILE, total_sheets)
        current_chunk_names = all_sheet_names[start_idx:end_idx]

        # 輸出檔名例如：檔名_part01_(工作表_1-10).md
        part_num_str = f"part{part_idx + 1:02d}"
        range_str = f"工作表_{start_idx + 1}-{end_idx}"
        output_path = f"{base_name}_{part_num_str}_({range_str}).md"

        print(
            f"📦 正在輸出 [{part_idx + 1}/{total_parts}]：{os.path.basename(output_path)}"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            # 寫入分卷標頭資訊
            f.write(
                f"# 數據彙整文件: {excel_filename} (第 {part_idx + 1}/{total_parts} 部分)\n\n"
            )
            f.write(
                f"> **本檔案範圍**：第 {start_idx + 1} 至第 {end_idx} 個工作表（全活頁簿共 {total_sheets} 個工作表）。\n\n"
            )

            # 寫入這份檔案專屬的目錄
            f.write("## 本檔案包含之工作表目錄\n")
            for local_i, name in enumerate(current_chunk_names, start=1):
                global_i = start_idx + local_i
                f.write(f"- 【工作表 {global_i}】`{name}`\n")
            f.write("\n---\n\n")

            # 寫入表格內容
            for local_i, sheet_name in enumerate(current_chunk_names, start=1):
                global_i = start_idx + local_i
                df = sheets[sheet_name]
                df_clean = clean_dataframe(df)

                f.write(f"## 【工作表 {global_i}】: {sheet_name}\n\n")

                if df_clean.empty:
                    f.write("*（此工作表為空白，無有效數據）*\n\n---\n\n")
                    continue

                rows, cols = df_clean.shape
                f.write(f"- **數據規模**：{rows} 列 × {cols} 欄\n\n")

                try:
                    md_table = df_clean.to_markdown(index=False)
                    f.write(md_table)
                except ImportError:
                    # tabulate 未安裝時自動降級輸出 CSV
                    csv_text = df_clean.to_csv(index=False)
                    f.write("```csv\n" + csv_text + "\n```")

                f.write("\n\n---\n\n")

    print("\n" + "=" * 45)
    print(" 全部檔案切割與轉換完成！")
    print(f"檔案皆已儲存在原始 Excel 的相同資料夾內。")
    print("=" * 45)


if __name__ == "__main__":
    excel_to_chunked_markdown()