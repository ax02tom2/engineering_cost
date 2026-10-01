import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(
    page_title="大地工程經費初估與單價資料庫",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 資料庫檔案路徑 (用於多人共享與永久儲存)
# ==========================================
DB_FILE = 'shared_cost_db.csv'
HISTORY_FILE = 'shared_history.csv'
VERSION_KEY = 'db_version_5' # 更改這個變數名稱可以強制重置資料庫

# 初始專業預設資料庫 (全尺寸、全細項補齊 + 新增微型樁、加勁擋土牆等)
DEFAULT_DB = [
    # --- 【大口徑集水井 (內徑 3.5m 深井)】 ---
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "井口護頂RC與導溝", "單位": "座", "單價(元)": 150000, "備註": "含開挖、配筋與澆置"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "井筒土方人工/機具開挖", "單位": "m³", "單價(元)": 1800, "備註": "含局限空間吊搬運與抽水"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "鋼襯鐵/RC波形鋼板環片組立", "單位": "m", "單價(元)": 85000, "備註": "依深度計價"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "環片背填灌漿 (固結/止水)", "單位": "式", "單價(元)": 120000, "備註": "防止井外土砂流失"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "輻射排水管-機具鑽孔", "單位": "m", "單價(元)": 1200, "備註": "水平鑽掘"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "輻射排水管-PVC管及不織布包覆", "單位": "m", "單價(元)": 600, "備註": "含湧水引導處理"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "井內不鏽鋼爬梯 (含防墜落設施)", "單位": "m", "單價(元)": 3500, "備註": "SUS304"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "局限空間通風與照明設備", "單位": "月", "單價(元)": 45000, "備註": "工安規定必需項目"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "底部封底混凝土 (3000psi)", "單位": "m³", "單價(元)": 3500, "備註": "含抗揚壓設計"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "頂部格柵安全蓋板 (重型)", "單位": "座", "單價(元)": 65000, "備註": "鍍鋅鋼格柵"},

    # --- 【大口徑集水井 (內徑 4.5m 深井)】 ---
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "井口護頂RC與導溝", "單位": "座", "單價(元)": 180000, "備註": "含開挖、配筋與澆置"},
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "井筒土方人工/機具開挖", "單位": "m³", "單價(元)": 1800, "備註": "含局限空間吊搬運與抽水"},
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "鋼襯鐵/RC波形鋼板環片組立", "單位": "m", "單價(元)": 115000, "備註": "依深度計價"},
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "環片背填灌漿 (固結/止水)", "單位": "式", "單價(元)": 150000, "備註": "防止井外土砂流失"},
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "輻射排水管-機具鑽孔", "單位": "m", "單價(元)": 1200, "備註": "水平鑽掘"},
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "輻射排水管-PVC管及不織布包覆", "單位": "m", "單價(元)": 600, "備註": "含湧水引導處理"},
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "井內不鏽鋼爬梯 (含防墜落設施)", "單位": "m", "單價(元)": 3500, "備註": "SUS304"},
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "局限空間通風與照明設備", "單位": "月", "單價(元)": 50000, "備註": "工安規定必需項目"},
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "底部封底混凝土 (3000psi)", "單位": "m³", "單價(元)": 3500, "備註": "含抗揚壓設計"},
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "頂部格柵安全蓋板 (重型)", "單位": "座", "單價(元)": 85000, "備註": "鍍鋅鋼格柵"},
    
    # --- 【大口徑集水井 (內徑 6.0m 深井)】 ---
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "井口護頂RC與導溝", "單位": "座", "單價(元)": 220000, "備註": "含開挖、配筋與澆置"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "井筒土方人工/機具開挖", "單位": "m³", "單價(元)": 1800, "備註": "含局限空間吊搬運與抽水"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "鋼襯鐵/RC波形鋼板環片組立", "單位": "m", "單價(元)": 165000, "備註": "依深度計價"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "環片背填灌漿 (固結/止水)", "單位": "式", "單價(元)": 200000, "備註": "防止井外土砂流失"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "輻射排水管-機具鑽孔", "單位": "m", "單價(元)": 1200, "備註": "水平鑽掘"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "輻射排水管-PVC管及不織布包覆", "單位": "m", "單價(元)": 600, "備註": "含湧水引導處理"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "井內不鏽鋼爬梯 (含防墜落設施)", "單位": "m", "單價(元)": 3500, "備註": "SUS304"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "局限空間通風與照明設備", "單位": "月", "單價(元)": 60000, "備註": "工安規定必需項目"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "底部封底混凝土 (3000psi)", "單位": "m³", "單價(元)": 3500, "備註": "含抗揚壓設計"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "頂部格柵安全蓋板 (重型)", "單位": "座", "單價(元)": 120000, "備註": "鍍鋅鋼格柵"},
    
    # --- 【集水井工程 (中小型)】 ---
    {"主工項": "集水井工程 (中小型)", "細項名稱": "小型集水井 (內徑 0.6m x 0.6m)", "單位": "座", "單價(元)": 8000, "備註": "含格柵蓋板及底部跌水"},
    {"主工項": "集水井工程 (中小型)", "細項名稱": "中型集水井 (內徑 1.0m x 1.0m)", "單位": "座", "單價(元)": 18000, "備註": "含格柵蓋板及底部跌水"},
    {"主工項": "集水井工程 (中小型)", "細項名稱": "圓型預鑄集水井 (內徑 Ø1.0m)", "單位": "座", "單價(元)": 15000, "備註": "含吊裝與接管"},

    # --- 【預力地錨工程 (永久性 30噸)】 ---
    {"主工項": "預力地錨工程 (永久性 30噸)", "細項名稱": "套管鑽孔 (土壤/卵礫石/岩盤)", "單位": "m", "單價(元)": 1200, "備註": "依現地地質調整"},
    {"主工項": "預力地錨工程 (永久性 30噸)", "細項名稱": "鋼絞線及防蝕套管組裝", "單位": "m", "單價(元)": 750, "備註": "含PE套管與防鏽油脂"},
    {"主工項": "預力地錨工程 (永久性 30噸)", "細項名稱": "高壓水泥漿灌注", "單位": "m", "單價(元)": 350, "備註": "純水泥漿 W/C=0.45"},
    {"主工項": "預力地錨工程 (永久性 30噸)", "細項名稱": "錨頭組件 (錨具、夾片、承壓鋼墊板)", "單位": "組", "單價(元)": 6500, "備註": "含防蝕罩"},
    {"主工項": "預力地錨工程 (永久性 30噸)", "細項名稱": "地錨張拉、鎖定及試驗", "單位": "孔", "單價(元)": 4500, "備註": "含潛變試驗與驗收"},
    
    # --- 【預力地錨工程 (永久性 60噸)】 ---
    {"主工項": "預力地錨工程 (永久性 60噸)", "細項名稱": "套管鑽孔 (土壤/卵礫石/岩盤)", "單位": "m", "單價(元)": 1600, "備註": "依現地地質調整"},
    {"主工項": "預力地錨工程 (永久性 60噸)", "細項名稱": "鋼絞線及防蝕套管組裝", "單位": "m", "單價(元)": 950, "備註": "含PE套管與防鏽油脂"},
    {"主工項": "預力地錨工程 (永久性 60噸)", "細項名稱": "高壓水泥漿灌注", "單位": "m", "單價(元)": 450, "備註": "純水泥漿 W/C=0.45"},
    {"主工項": "預力地錨工程 (永久性 60噸)", "細項名稱": "錨頭組件 (錨具、夾片、承壓鋼墊板)", "單位": "組", "單價(元)": 8500, "備註": "含防蝕罩"},
    {"主工項": "預力地錨工程 (永久性 60噸)", "細項名稱": "地錨張拉、鎖定及試驗", "單位": "孔", "單價(元)": 5500, "備註": "含潛變試驗與驗收"},
    {"主工項": "預力地錨工程 (永久性 60噸)", "細項名稱": "地錨荷重計 (Load Cell) 監測安裝", "單位": "組", "單價(元)": 35000, "備註": "長期監測用(選配)"},

    # --- 【微型樁工程】 ---
    {"主工項": "微型樁工程 (Type A - 僅鋼管)", "細項名稱": "微型樁鑽孔 (內徑 Ø150mm)", "單位": "m", "單價(元)": 850, "備註": "土壤或劣質岩盤"},
    {"主工項": "微型樁工程 (Type A - 僅鋼管)", "細項名稱": "無縫鋼管置入及灌漿", "單位": "m", "單價(元)": 1200, "備註": "厚度依設計"},
    {"主工項": "微型樁工程 (Type B - 鋼管+鋼筋)", "細項名稱": "微型樁鑽孔 (內徑 Ø200mm)", "單位": "m", "單價(元)": 1100, "備註": "較大管徑"},
    {"主工項": "微型樁工程 (Type B - 鋼管+鋼筋)", "細項名稱": "鋼管及主鋼筋置入與灌漿", "單位": "m", "單價(元)": 1600, "備註": "增加抗彎能力"},
    {"主工項": "微型樁工程 (Type B - 鋼管+鋼筋)", "細項名稱": "微型樁樁帽 (RC樁帽)", "單位": "座", "單價(元)": 3500, "備註": "單獨施作或與護坡結合"},

    # --- 【抗滑樁工程 (內徑 Ø1.0m)】 ---
    {"主工項": "抗滑樁工程 (全套管機 內徑 Ø1.0m)", "細項名稱": "全套管機具鑽掘及拔管", "單位": "m", "單價(元)": 6500, "備註": "不含遇岩盤加價"},
    {"主工項": "抗滑樁工程 (全套管機 內徑 Ø1.0m)", "細項名稱": "超音波完整性檢測 (Koden test)", "單位": "孔", "單價(元)": 10000, "備註": "確認鑽孔垂直度"},
    {"主工項": "抗滑樁工程 (全套管機 內徑 Ø1.0m)", "細項名稱": "鋼筋籠組立、吊放與續接", "單位": "噸", "單價(元)": 38000, "備註": "含銲接或續接器"},
    {"主工項": "抗滑樁工程 (全套管機 內徑 Ø1.0m)", "細項名稱": "特密管水中混凝土澆置", "單位": "m³", "單價(元)": 3200, "備註": "坍度較大之混凝土"},
    {"主工項": "抗滑樁工程 (全套管機 內徑 Ø1.0m)", "細項名稱": "劣質土與泥水沉澱外運處理", "單位": "m³", "單價(元)": 1500, "備註": "含環保處理費"},

    # --- 【抗滑樁工程 (內徑 Ø1.5m)】 ---
    {"主工項": "抗滑樁工程 (全套管機 內徑 Ø1.5m)", "細項名稱": "全套管機具鑽掘及拔管", "單位": "m", "單價(元)": 9500, "備註": "不含遇岩盤加價"},
    {"主工項": "抗滑樁工程 (全套管機 內徑 Ø1.5m)", "細項名稱": "超音波完整性檢測 (Koden test)", "單位": "孔", "單價(元)": 12000, "備註": "確認鑽孔垂直度"},
    {"主工項": "抗滑樁工程 (全套管機 內徑 Ø1.5m)", "細項名稱": "鋼筋籠組立、吊放與續接", "單位": "噸", "單價(元)": 38000, "備註": "含銲接或續接器"},
    {"主工項": "抗滑樁工程 (全套管機 內徑 Ø1.5m)", "細項名稱": "特密管水中混凝土澆置", "單位": "m³", "單價(元)": 3500, "備註": "坍度較大之混凝土"},
    {"主工項": "抗滑樁工程 (全套管機 內徑 Ø1.5m)", "細項名稱": "劣質土與泥水沉澱外運處理", "單位": "m³", "單價(元)": 1800, "備註": "含環保處理費"},

    # --- 【擋土牆工程】 ---
    {"主工項": "懸臂式 RC擋土牆 (H=2.0m)", "細項名稱": "基礎開挖與夯實", "單位": "m³", "單價(元)": 350, "備註": "含排水處理"},
    {"主工項": "懸臂式 RC擋土牆 (H=2.0m)", "細項名稱": "基礎墊層PC (厚10cm)", "單位": "m²", "單價(元)": 350, "備註": "140kgf/cm²"},
    {"主工項": "懸臂式 RC擋土牆 (H=2.0m)", "細項名稱": "鋼筋組立 (含基礎與牆身)", "單位": "噸", "單價(元)": 32000, "備註": "含加工及綁紮"},
    {"主工項": "懸臂式 RC擋土牆 (H=2.0m)", "細項名稱": "清水模板組立及拆除", "單位": "m²", "單價(元)": 850, "備註": "牆面及基礎"},
    {"主工項": "懸臂式 RC擋土牆 (H=2.0m)", "細項名稱": "混凝土澆置 (210kgf/cm²)", "單位": "m³", "單價(元)": 2800, "備註": "含搗實及養護"},
    {"主工項": "懸臂式 RC擋土牆 (H=2.0m)", "細項名稱": "牆背級配透水回填及排水管", "單位": "m", "單價(元)": 1200, "備註": "防止水壓累積"},
    {"主工項": "懸臂式 RC擋土牆 (H=2.0m)", "細項名稱": "伸縮縫及止水帶設置", "單位": "m", "單價(元)": 450, "備註": "每隔一定距離設置"},
    
    {"主工項": "懸臂式 RC擋土牆 (H=4.0m)", "細項名稱": "基礎開挖與夯實", "單位": "m³", "單價(元)": 350, "備註": "含排水處理"},
    {"主工項": "懸臂式 RC擋土牆 (H=4.0m)", "細項名稱": "基礎墊層PC (厚10cm)", "單位": "m²", "單價(元)": 350, "備註": "140kgf/cm²"},
    {"主工項": "懸臂式 RC擋土牆 (H=4.0m)", "細項名稱": "鋼筋組立 (含基礎與牆身)", "單位": "噸", "單價(元)": 32000, "備註": "含加工及綁紮"},
    {"主工項": "懸臂式 RC擋土牆 (H=4.0m)", "細項名稱": "清水模板組立及拆除", "單位": "m²", "單價(元)": 850, "備註": "牆面及基礎"},
    {"主工項": "懸臂式 RC擋土牆 (H=4.0m)", "細項名稱": "混凝土澆置 (210kgf/cm²)", "單位": "m³", "單價(元)": 2800, "備註": "含搗實及養護"},
    {"主工項": "懸臂式 RC擋土牆 (H=4.0m)", "細項名稱": "牆背級配透水回填及排水管", "單位": "m", "單價(元)": 1200, "備註": "防止水壓累積"},
    {"主工項": "懸臂式 RC擋土牆 (H=4.0m)", "細項名稱": "伸縮縫及止水帶設置", "單位": "m", "單價(元)": 450, "備註": "每隔一定距離設置"},

    # --- 【加勁擋土牆工程】 ---
    {"主工項": "加勁擋土牆工程 (包被式)", "細項名稱": "基礎開挖與整平", "單位": "m³", "單價(元)": 350, "備註": "土方開挖"},
    {"主工項": "加勁擋土牆工程 (包被式)", "細項名稱": "地工合成材 (加勁格網) 鋪設", "單位": "m²", "單價(元)": 450, "備註": "依設計張力"},
    {"主工項": "加勁擋土牆工程 (包被式)", "細項名稱": "包被式袋體組立與植生", "單位": "m²", "單價(元)": 1200, "備註": "牆面面積"},
    {"主工項": "加勁擋土牆工程 (包被式)", "細項名稱": "牆體粒料回填與夯實", "單位": "m³", "單價(元)": 650, "備註": "分層滾壓"},
    
    {"主工項": "加勁擋土牆工程 (面板式)", "細項名稱": "預鑄混凝土面板組立", "單位": "m²", "單價(元)": 3500, "備註": "含連接件"},
    {"主工項": "加勁擋土牆工程 (面板式)", "細項名稱": "加勁帶/金屬網鋪設", "單位": "m", "單價(元)": 600, "備註": "依長度計價"},
    {"主工項": "加勁擋土牆工程 (面板式)", "細項名稱": "牆體粒料回填與夯實", "單位": "m³", "單價(元)": 650, "備註": "分層滾壓"},

    # --- 【重力式/蛇籠擋土牆】 ---
    {"主工項": "重力式/石籠擋土牆工程", "細項名稱": "重力式混凝土擋土牆 (H=2.0m)", "單位": "m", "單價(元)": 12000, "備註": "含開挖及無筋混凝土"},
    {"主工項": "重力式/石籠擋土牆工程", "細項名稱": "蛇籠/石籠組立 (2.0x1.0x1.0m)", "單位": "只", "單價(元)": 3500, "備註": "含鍍鋅鐵絲網、塊石及編布"},
    {"主工項": "重力式/石籠擋土牆工程", "細項名稱": "箱型石籠組立 (防蝕型)", "單位": "只", "單價(元)": 4800, "備註": "包覆PVC防蝕網"},

    # --- 【防落石網與坡面工程】 ---
    {"主工項": "高強度防落石網 (被動式 500kJ)", "細項名稱": "端部與中間基座微型樁", "單位": "支", "單價(元)": 12000, "備註": "含鑽孔灌漿固定"},
    {"主工項": "高強度防落石網 (被動式 500kJ)", "細項名稱": "高強度鋼柱及緩衝鋼纜", "單位": "組", "單價(元)": 55000, "備註": "吸收落石能量"},
    {"主工項": "高強度防落石網 (被動式 500kJ)", "細項名稱": "攔截主網與牽引索組立", "單位": "m", "單價(元)": 25000, "備註": "依攔截長度計價"},

    {"主工項": "高強度防落石網 (被動式 1000kJ)", "細項名稱": "端部與中間基座微型樁", "單位": "支", "單價(元)": 15000, "備註": "含鑽孔灌漿固定"},
    {"主工項": "高強度防落石網 (被動式 1000kJ)", "細項名稱": "高強度鋼柱及緩衝鋼纜", "單位": "組", "單價(元)": 85000, "備註": "吸收落石能量"},
    {"主工項": "高強度防落石網 (被動式 1000kJ)", "細項名稱": "攔截主網與牽引索組立", "單位": "m", "單價(元)": 45000, "備註": "依攔截長度計價"},
    
    {"主工項": "坡面防護與植生工程", "細項名稱": "掛網噴凝土護坡 (厚 10cm)", "單位": "m²", "單價(元)": 950, "備註": "含點焊鋼絲網及配比噴槍澆置"},
    {"主工項": "坡面防護與植生工程", "細項名稱": "掛網噴凝土護坡 (厚 15cm)", "單位": "m²", "單價(元)": 1300, "備註": "雙層鋼絲網"},
    {"主工項": "坡面防護與植生工程", "細項名稱": "主動式防落石網 (菱形網+打設岩栓)", "單位": "m²", "單價(元)": 1200, "備註": "緊貼坡面"},
    {"主工項": "坡面防護與植生工程", "細項名稱": "坡面噴植草籽植生", "單位": "m²", "單價(元)": 250, "備註": "含客土及養護"},
    {"主工項": "坡面防護與植生工程", "細項名稱": "打設岩栓 (L=3m, Ø25mm)", "單位": "支", "單價(元)": 2500, "備註": "坡面穩定加固"},

    # --- 【集水管與截水溝工程】 ---
    {"主工項": "常規集水管與截水溝", "細項名稱": "橫向集水管 (PVC透水管 內徑 Ø50mm)", "單位": "m", "單價(元)": 850, "備註": "含鑽孔與不織布包覆"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "橫向集水管 (PVC透水管 內徑 Ø100mm)", "單位": "m", "單價(元)": 1200, "備註": "含鑽孔與不織布包覆"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "橫向集水管 (HDPE波紋管 內徑 Ø100mm)", "單位": "m", "單價(元)": 1400, "備註": "高抗壓，含鑽孔"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "橫向集水管 (HDPE波紋管 內徑 Ø150mm)", "單位": "m", "單價(元)": 1800, "備註": "高抗壓，含鑽孔"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "橫向集水管 (不鏽鋼透水管 內徑 Ø50mm)", "單位": "m", "單價(元)": 2200, "備註": "抗鏽蝕設計"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "坡面U型截水溝 (W30cm x H30cm)", "單位": "m", "單價(元)": 1500, "備註": "現場澆置"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "坡面U型截水溝 (W60cm x H60cm)", "單位": "m", "單價(元)": 2800, "備註": "現場澆置"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "山區跌水工 (RC階梯式)", "單位": "座", "單價(元)": 15000, "備註": "依設計高差調整"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "盲溝 (包含碎石級配及透水管)", "單位": "m", "單價(元)": 1800, "備註": "寬60cm 深60cm 斷面"},
    
    # --- 【雜項工程】 ---
    {"主工項": "假設與雜項工程", "細項名稱": "施工臨時便道 (山區土方開挖與夯實)", "單位": "m", "單價(元)": 1500, "備註": "依便道長度計價"},
    {"主工項": "假設與雜項工程", "細項名稱": "鋪設鋼鈑便道 (含租金與吊放)", "單位": "m²", "單價(元)": 800, "備註": "軟弱地盤通行"},
    {"主工項": "假設與雜項工程", "細項名稱": "土方合法外運棄置 (B1/B2)", "單位": "m³", "單價(元)": 850, "備註": "含棄土證明"},
    {"主工項": "假設與雜項工程", "細項名稱": "劣質土/淤泥環保外運", "單位": "m³", "單價(元)": 1800, "備註": "特殊處置場"},
    {"主工項": "假設與雜項工程", "細項名稱": "洗車設備及環保設施維護", "單位": "式", "單價(元)": 150000, "備註": "全工期"},
    {"主工項": "假設與雜項工程", "細項名稱": "交通維持計畫及設施", "單位": "式", "單價(元)": 200000, "備註": "含交維審查及交管人員"}
]

# ★ 資料庫強迫重置機制 ★
if 'db_version' not in st.session_state or st.session_state['db_version'] != VERSION_KEY:
    df = pd.DataFrame(DEFAULT_DB)
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    st.session_state['db_version'] = VERSION_KEY

# 讀取共用資料庫
def load_db():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['單價(元)'] = df['單價(元)'].astype(int)
        return df
    else:
        df = pd.DataFrame(DEFAULT_DB)
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        return df

# 儲存共用資料庫
def save_db(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# 讀取共用歷史紀錄
def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_json(HISTORY_FILE, orient='records', lines=True).to_dict('records') if os.path.getsize(HISTORY_FILE) > 0 else []
    else:
        return []

# 儲存共用歷史紀錄
def save_history(history_list):
    if history_list:
        pd.DataFrame(history_list).to_json(HISTORY_FILE, orient='records', lines=True, force_ascii=False)
    else:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)

# 載入資料至 session state
if 'cost_db' not in st.session_state:
    st.session_state['cost_db'] = load_db()
if 'history' not in st.session_state:
    st.session_state['history'] = load_history()

# ==========================================
# 介面設計開始
# ==========================================
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stExpander { border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;}
        .metric-card { background-color: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 6px solid #0056b3; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;}
        .align-text { margin-top: 28px; font-size: 16px; line-height: 1.5; }
        .price-text { color: #4CAF50; font-weight: 700; font-size: 16px; }
        .total-text { color: #333333; font-weight: 700; font-size: 16px; }
        hr { margin: 1em 0; border: 0; height: 1px; background: #eaedf0; }
    </style>
""", unsafe_allow_html=True)

st.title("⛰️ 大地工程經費初估與雲端共享資料庫")

with st.sidebar:
    st.header("功能導覽")
    tab = st.radio("", ["📊 專案經費初估", "📚 共享單價資料庫管理", "📁 共享歷史估算紀錄"])
    st.markdown("---")
    
    st.markdown("#### 🔄 強制同步最新資料庫")
    st.caption("使用時機：點擊此按鈕即可抓取伺服器上最新的資料。")
    if st.button("立即同步更新", use_container_width=True):
        st.session_state['cost_db'] = load_db()
        st.session_state['history'] = load_history()
        st.rerun()

# ==========================================
# TAB 1: 專案經費初估
# ==========================================
if tab == "📊 專案經費初估":
    db = load_db()
    
    st.subheader("1. 專案名稱與工程項目設定")
    project_name = st.text_input("專案名稱", "某坡地穩定與水保改善工程")
    
    all_major_items = db['主工項'].unique().tolist()
    selected_majors = st.multiselect(
        "請選擇本次工程涵蓋的主項目 (可複選)：", 
        options=all_major_items,
        placeholder="點擊展開，例如：大口徑集水井、抗滑樁..."
    )
    
    selected_details = []
    
    if selected_majors:
        st.markdown("#### 📝 細項數量與單價設定")
        st.caption("請填寫數量。參考價已精準對齊，若需微調單價請修改「自訂單價」。")
        
        for major in selected_majors:
            with st.expander(f"📂 {major}", expanded=True):
                sub_items = db[db['主工項'] == major]
                
                for idx, row in sub_items.iterrows():
                    sub_name = row['細項名稱']
                    unit = row['單位']
                    default_price = int(row['單價(元)'])
                    
                    st.markdown(f"**{sub_name}** <span style='color:gray; font-size:13px;'>({row['備註']})</span>", unsafe_allow_html=True)
                    
                    c_qty, c_ref, c_custom, c_total = st.columns([1, 1, 1, 1])
                    
                    with c_qty:
                        qty = st.number_input(f"數量 ({unit})", value=0.0, step=10.0, key=f"qty_{major}_{idx}")
                    with c_ref:
                        st.markdown(f"<div class='align-text'>參考價：<span class='price-text'>NT$ {default_price:,}</span></div>", unsafe_allow_html=True)
                    with c_custom:
                        custom_val = st.text_input(f"自訂單價(可選)", value=str(default_price), key=f"prc_{major}_{idx}")
                        try:
                            prc = int(custom_val.replace(',', ''))
                        except ValueError:
                            prc = default_price
                    with c_total:
                        subtotal = int(qty * prc)
                        st.markdown(f"<div class='align-text'>小計：<span class='total-text'>NT$ {subtotal:,}</span></div>", unsafe_allow_html=True)
                        
                    st.markdown("<hr>", unsafe_allow_html=True)
                    
                    if qty > 0:
                        selected_details.append({
                            "主工項": major,
                            "細項名稱": sub_name,
                            "數量": qty,
                            "單位": unit,
                            "單價(元)": prc,
                            "複價": subtotal
                        })

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("2. 間接費用費率設定 (%)")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        misc_pct = st.number_input("雜項工程費率", value=15.0, step=0.5)
    with col_m2:
        management_pct = st.number_input("管理及利潤率", value=10.0, step=0.5)
    with col_m3:
        tax_pct = st.number_input("營業稅率", value=5.0, step=0.5)

    st.markdown("---")
    
    st.subheader("📊 3. 估算結果分析與明細")
    if len(selected_details) > 0:
        df_selected = pd.DataFrame(selected_details)
        direct_cost = df_selected['複價'].sum()
        
        misc_cost = int(direct_cost * (misc_pct / 100))
        subtotal_1 = direct_cost + misc_cost
        management_cost = int(subtotal_1 * (management_pct / 100))
        subtotal_2 = subtotal_1 + management_cost
        tax_cost = int(subtotal_2 * (tax_pct / 100))
        total_cost = subtotal_2 + tax_cost
        
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin:0; color:#555; font-size:16px;">總經費初估 (含稅)</p>
            <h1 style="margin:0; color:#0056b3; font-size:36px; padding-top:5px;">NT$ {total_cost:,}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        res_col1, res_col2 = st.columns([1.5, 1])
        
        with res_col1:
            st.write("##### 📝 直接工程費完整明細")
            st.dataframe(df_selected.style.format({"數量": "{:,.1f}", "單價(元)": "{:,.0f}", "複價": "{:,.0f}"}), use_container_width=True, hide_index=True)
            
            st.write("##### 📊 經費結構摘要")
            summary_table = pd.DataFrame({
                "費用項目": ["一、直接工程費", f"二、雜項工程 ({misc_pct}%)", f"三、工程管理及利潤 ({management_pct}%)", f"四、營業稅 ({tax_pct}%)", "總計"],
                "金額 (NT$)": [direct_cost, misc_cost, management_cost, tax_cost, total_cost]
            })
            st.dataframe(summary_table.style.format({"金額 (NT$)": "{:,.0f}"}), use_container_width=True, hide_index=True)
            
        with res_col2:
            st.write("##### 📈 經費佔比視覺化")
            chart_data = pd.DataFrame({
                "費用類別": ["直接工程", "雜項工程", "管理及利潤", "營業稅"],
                "金額": [direct_cost, misc_cost, management_cost, tax_cost]
            })
            chart = alt.Chart(chart_data).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X('金額:Q', title='金額 (NT$)', axis=alt.Axis(format='d')),
                y=alt.Y('費用類別:N', sort='-x', title=''),
                color=alt.Color('費用類別:N', legend=None),
                tooltip=['費用類別', alt.Tooltip('金額:Q', format=',d')]
            ).properties(height=350).configure_view(strokeWidth=0)
            
            st.altair_chart(chart, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 將專案發佈至共享歷史紀錄", type="primary", use_container_width=True):
                current_history = load_history()
                record = {
                    "專案名稱": project_name,
                    "直接工程費": direct_cost,
                    "雜項費": misc_cost,
                    "管理費": management_cost,
                    "營業稅": tax_cost,
                    "總經費": total_cost,
                    "時間": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "細項明細": df_selected.to_dict('records')
                }
                current_history.append(record)
                save_history(current_history)
                st.session_state['history'] = current_history
                st.success("儲存成功！所有同仁皆可於「共享歷史估算紀錄」查看此專案。")
    else:
        st.info("👈 請先於上方區塊勾選工項並填寫大於 0 的數量。")

# ==========================================
# TAB 2: 共享單價資料庫管理
# ==========================================
elif tab == "📚 共享單價資料庫管理":
    st.header("📚 共享單價資料庫管理")
    
    db = load_db()
    
    c_dl, c_up = st.columns([1, 1], gap="large")
    with c_dl:
        st.markdown("#### ⬇️ 步驟 1: 下載目前共用資料庫")
        st.caption("任何人下載修改後重新上傳，將覆蓋所有人的資料庫。")
        csv_db = db.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載 CSV 模板", data=csv_db, file_name="geotech_database_shared.csv", mime="text/csv")
    
    with c_up:
        st.markdown("#### ⬆️ 步驟 2: 匯入最新單價表")
        st.caption("上傳後，所有同仁的選單將立即更新為最新單價。")
        uploaded_file = st.file_uploader("上傳更新後的 CSV 檔案", type=["csv"], label_visibility="collapsed")
        if uploaded_file is not None:
            try:
                new_db = pd.read_csv(uploaded_file)
                if set(['主工項', '細項名稱', '單位', '單價(元)']).issubset(new_db.columns):
                    save_db(new_db)
                    st.session_state['cost_db'] = new_db
                    st.success("✅ 共用資料庫已全面更新！")
                    st.rerun()
                else:
                    st.error("欄位格式錯誤！")
            except Exception as e:
                st.error(f"檔案讀取失敗: {e}")

    st.markdown("---")
    st.markdown("#### 🔍 目前資料庫檢視與單筆新增")
    
    search_query = st.text_input("🔍 搜尋工項名稱", "", placeholder="例如：集水井")
    display_db = db[db['主工項'].str.contains(search_query, case=False) | db['細項名稱'].str.contains(search_query, case=False)] if search_query else db
    st.dataframe(display_db.style.format({"單價(元)": "{:,.0f}"}), use_container_width=True, hide_index=True)
    
    with st.expander("➕ 人工單筆新增細項規格 (立即同步)"):
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_major = st.text_input("主工項名稱", placeholder="輸入新類別或現有類別")
                new_sub = st.text_input("細項名稱與規格")
                new_unit = st.text_input("單位")
            with c2:
                new_price = st.text_input("單價 (元)", value="1000")
                new_note = st.text_input("備註說明")
                
            if st.form_submit_button("確認新增"):
                try:
                    parsed_price = int(new_price.replace(',', ''))
                    if new_major and new_sub:
                        new_row = pd.DataFrame([{"主工項": new_major, "細項名稱": new_sub, "單位": new_unit, "單價(元)": parsed_price, "備註": new_note}])
                        current_db = load_db()
                        updated_db = pd.concat([current_db, new_row], ignore_index=True)
                        save_db(updated_db)
                        st.session_state['cost_db'] = updated_db
                        st.success("新增成功！其他同仁重新整理網頁即可看到。")
                        st.rerun()
                except ValueError:
                    st.error("單價請輸入有效數字！")

# ==========================================
# TAB 3: 共享歷史估算紀錄
# ==========================================
elif tab == "📁 共享歷史估算紀錄":
    st.header("📁 共享歷史估算紀錄與匯出")
    st.markdown("點擊專案卡片可檢視所有人儲存的詳細工程與預算明細。")
    
    history_data = load_history()
    
    if len(history_data) > 0:
        all_export_data = []
        
        for record in reversed(history_data):
            with st.expander(f"📌 [{record['時間']}] {record['專案名稱']} ─ 總經費: NT$ {record['總經費']:,}"):
                
                st.markdown("##### 📊 專案費用總結")
                summary_cols = st.columns(5)
                summary_cols[0].metric("直接工程費", f"NT$ {record['直接工程費']:,}")
                summary_cols[1].metric("雜項費", f"NT$ {record['雜項費']:,}")
                summary_cols[2].metric("管理費", f"NT$ {record['管理費']:,}")
                summary_cols[3].metric("營業稅", f"NT$ {record['營業稅']:,}")
                summary_cols[4].metric("總經費", f"NT$ {record['總經費']:,}")
                
                st.markdown("##### 📝 專案工程細項明細")
                if "細項明細" in record and record["細項明細"]:
                    detail_df = pd.DataFrame(record["細項明細"])
                    st.dataframe(
                        detail_df.style.format({"數量": "{:,.1f}", "單價(元)": "{:,.0f}", "複價": "{:,.0f}"}),
                        use_container_width=True, hide_index=True
                    )
                    
                    for row in record["細項明細"]:
                        row_export = row.copy()
                        row_export['專案名稱'] = record['專案名稱']
                        row_export['估算時間'] = record['時間']
                        all_export_data.append(row_export)
                else:
                    st.warning("舊版紀錄未儲存明細。")

        st.markdown("---")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn1:
            history_summary_df = pd.DataFrame(history_data).drop(columns=['細項明細'], errors='ignore')
            csv_summary = history_summary_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 下載歷史紀錄 (僅總表 CSV)", data=csv_summary, file_name="history_summary.csv", mime="text/csv", use_container_width=True)
            
        with col_btn2:
            if all_export_data:
                export_df = pd.DataFrame(all_export_data)
                cols = ['專案名稱', '估算時間'] + [c for c in export_df.columns if c not in ['專案名稱', '估算時間']]
                export_df = export_df[cols]
                csv_details = export_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下載歷史紀錄 (含所有細項明細 CSV)", data=csv_details, file_name="history_full_details.csv", mime="text/csv", use_container_width=True)
        
        with col_btn3:
            if st.button("🗑 清空所有團隊紀錄 (危險操作)", use_container_width=True):
                save_history([])
                st.session_state['history'] = []
                st.rerun()
                
    else:
        st.info("目前尚無團隊估算紀錄。")

# ==========================================
# 網頁下方資料來源備註 (Footer)
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 13px;'>
        📌 <b>資料來源與免責聲明備註：</b><br>
        1. 本系統工項（含懸臂/重力擋土牆、主被動防落石網、各尺寸大口徑集水井、各管徑集水管及預力地錨等）之拆分邏輯與預設參考單價，係參考<b>行政院公共工程委員會 (PCCES) 價格資料庫編碼規則</b>及近期國內大地工程招標公開行情編製。<br>
        2. 工程造價會因現地地質條件（如卵礫石層、岩盤硬度）、施工動線難易度與物價波動而有顯著差異。表中單價僅供基準參考。<br>
        3. 本系統提供之數據與試算結果僅供<b>專案初期經費編列、可行性評估參考</b>，不具備法律或合約約束力。正式經費應依正式地質鑽探報告、詳細設計圖說及預算書為準。
    </div>
    """,
    unsafe_allow_html=True
)
