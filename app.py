import io
import json
import os
import shutil
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="大地工程經費初估與單價資料庫",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 檔案路徑與版本
# ==========================================
DB_FILE = "shared_cost_db.csv"
HISTORY_FILE = "shared_history.csv"  # 實際為 JSON Lines，沿用舊檔名以相容既有紀錄
VERSION_FILE = "db_version.txt"
BACKUP_DIR = "backups"
CURRENT_VERSION = "v10_restored_and_hardened"  # 只有「預設資料庫內容」改動時才需要更改

REQUIRED_COLS = ["主工項", "細項名稱", "單位", "單價(元)"]
ALL_COLS = ["主工項", "細項名稱", "單位", "單價(元)", "備註", "資料來源"]
SRC_ORIG = "沿用原表"      # 沿用你原本表格中的數值
SRC_NEW = "新增待核"       # 本次新增或調整的數值，務必核對
SRC_USER = "使用者新增"    # 同仁在系統中自行新增
DEFAULT_SOURCES = (SRC_ORIG, SRC_NEW)

# ==========================================
# 預設資料庫 (所有單價皆為概估值，使用前請核對 PCCES / 標案資料)
# ==========================================
DEFAULT_DB = []
NEW = "new"  # 在 tuple 第 5 欄標註為「新增待核」


def add(major, rows):
    for r in rows:
        sub, unit, price, note = r[:4]
        src = SRC_NEW if len(r) > 4 else SRC_ORIG
        DEFAULT_DB.append({
            "主工項": major, "細項名稱": sub, "單位": unit,
            "單價(元)": price, "備註": note, "資料來源": src,
        })


# --- 前期調查、測量與監測 ---
add("前期調查、測量與監測儀器", [
    ("岩心鑽探及試驗 (含SPT及室內試驗)", "m", 2500, "依深度計價"),
    ("鑽探機具動員與作業平台", "孔", 30000, "山區孔位另計"),
    ("地電阻探測 (2D/3D)", "m", 600, "地下水及滑動面研判"),
    ("空拍地形及LiDAR測量", "公頃", 15000, "基本面積起算"),
    ("落石能量分析與模擬 (2D/3D)", "式", 180000, "設計階段模擬計算"),
    ("傾斜管設置 (含套管與保護蓋)", "m", 1800, "監測深部滑動"),
    ("地下水位觀測井設置", "m", 2200, "含透水管及濾料"),
    ("地表伸縮計安裝", "組", 35000, "裂縫位移監測"),
    ("雨量計安裝", "組", 45000, "含資料記錄器"),
    ("GNSS 測站安裝", "組", 280000, "含基座與電源"),
    ("表面傾斜計安裝", "組", 60000, "結構物或坡面傾斜監測"),
    ("監測資料傳輸與太陽能供電系統", "套", 80000, "無市電區域"),
    ("鄰房現況鑑定 (施工前/後)", "戶", 15000, "市區邊坡必備"),
    ("生態檢核作業費", "式", 150000, "公共工程必備程序"),
])

# --- 假設與開場工程 ---
add("假設與開場工程", [
    ("機具動員與復員", "式", 150000, "依規模調整"),
    ("臨時水電設施與發電機租用", "月", 35000, "無市電區域必需"),
    ("施工圍籬、紐澤西護欄及告示牌", "m", 1200, "安全阻隔"),
    ("臨時沉砂池與施工期逕流廢水處理", "式", 180000, "水保法規要求"),
    ("河川/溪溝臨時導流與圍堰", "m", 4500, "擋水設施"),
    ("施工期全天候抽水機具作業", "日", 3500, "地下水位高區域"),
    ("山區單軌車或索道運搬設備", "m", 1500, "無便道物料運輸"),
    ("樹木砍伐與林地障礙物清除", "公頃", 250000, "開闢作業帶"),
    ("施工臨時便道 (山區土方開挖與夯實)", "m", 1500, "依便道長度計價"),
    ("鋪設鋼鈑便道 (含租金與吊放)", "m²", 800, "軟弱地盤通行"),
    ("土方合法外運棄置 (B1/B2)", "m³", 850, "含棄土證明"),
    ("劣質土/淤泥環保外運", "m³", 1800, "特殊處置場"),
    ("洗車設備及環保設施維護", "式", 150000, "全工期"),
    ("交通維持計畫及設施", "式", 200000, "含交維審查及交管人員"),
])

# --- 大口徑集水井 (3.5 / 4.5 / 6.0m) ---
# (細項, 單位, (3.5m, 4.5m, 6.0m), 備註, 3.5m是否新增, 4.5/6.0m是否新增)
WELL_ITEMS = [
    ("井口護頂RC與導溝", "座", (150000, 180000, 220000), "含開挖、配筋與澆置", False, False),
    ("井筒土方人工/機具開挖", "m³", (2200, 2600, 3200), "含局限空間吊搬運與抽水", False, False),
    ("遇岩盤或孤石破碎開挖加價", "m³", (1800, 2200, 2800), "增加鑿岩費用", False, True),
    ("鋼襯鐵/波形鋼板環片組立", "m", (85000, 115000, 165000), "依深度計價", False, False),
    ("鋼環片防蝕塗裝及接縫止水條", "m", (6500, 8500, 11000), "防鏽與防砂流失", False, True),
    ("環片背填灌漿 (固結/止水)", "m", (4500, 6000, 8000), "依深度計量", False, True),
    ("輻射管孔口管、止水閥與防護", "處", (15000, 15000, 15000), "控制湧水及後續維護", False, True),
    ("輻射排水管-機具鑽孔", "m", (1200, 1200, 1200), "水平鑽掘", False, False),
    ("輻射排水管-PVC管及不織布包覆", "m", (600, 600, 600), "含湧水引導處理", False, False),
    ("井底濾層或透水碎石墊層", "m³", (2800, 2800, 2800), "底部防淘刷湧砂", False, True),
    ("底部封底混凝土 (3000psi)", "m³", (4500, 4500, 4500), "含抗揚壓設計", False, False),
    ("井內揚水/排水豎管 (PVC/HDPE)", "m", (1200, 1500, 1500), "將井底積水向上抽排", False, False),
    ("沉水式抽水機與自動控制盤", "組", (85000, 120000, 120000), "含安裝配線", False, False),
    ("出水管線至坡外之導排水與消能工", "m", (2500, 3000, 3500), "接續至外部水路", False, True),
    ("井內不鏽鋼爬梯 (含防墜落設施)", "m", (3500, 3500, 3500), "SUS304", False, False),
    ("局限空間通風、照明及氣體偵測設備", "月", (55000, 60000, 70000), "工安規定必需項目", False, True),
    ("井口吊運設備(三腳架/卷揚機)及圍籬", "式", (85000, 110000, 150000), "設備設置", False, True),
    ("頂部格柵安全蓋板 (重型)", "座", (65000, 85000, 120000), "鍍鋅鋼格柵", False, False),
    ("井內水位計與觀測設備", "組", (35000, 35000, 35000), "監測井內水位", True, True),
]
for i, dia in enumerate((3.5, 4.5, 6.0)):
    add(f"大口徑集水井 (內徑 {dia}m 深井)", [
        (s, u, p[i], n, NEW) if (n35 if i == 0 else nlg) else (s, u, p[i], n)
        for s, u, p, n, n35, nlg in WELL_ITEMS
    ])

add("集水井工程 (中小型)", [
    ("小型集水井 (內徑 0.6m x 0.6m)", "座", 8000, "含格柵蓋板及底部跌水"),
    ("中型集水井 (內徑 1.0m x 1.0m)", "座", 18000, "含格柵蓋板及底部跌水"),
    ("圓型預鑄集水井 (內徑 Ø1.0m)", "座", 15000, "含吊裝與接管"),
])

# --- 預力地錨 (30 / 60 / 100 噸) ---
ANCHOR_ITEMS = [
    ("坡面施工架組立與拆除", "m²", (450, 450, 450), "高處鑽孔張拉作業必備", False),
    ("套管鑽孔 (自由段與錨定段)", "m", (1500, 1600, 2200), "依現地地質調整", False),
    ("斜向鑽孔或遇岩盤加價", "m", (850, 850, 1200), "鑽機傾斜或鑽岩", True),
    ("鋼絞線及防蝕套管組裝", "m", (750, 1100, 1800), "含PE管、間隔器與預留1m張拉段", False),
    ("洗孔、排氣管與一次灌漿", "m", (450, 450, 600), "全孔灌漿", True),
    ("錨定段二次高壓灌漿", "m", (650, 650, 850), "提升握裹力", True),
    ("地錨承壓座 (RC座/格樑節點)", "座", (6500, 8000, 12000), "提供張拉反力面", True),
    ("錨頭組件 (錨具/承壓鋼墊板/防鏽油脂)", "組", (6500, 8500, 15000), "含防蝕罩", True),
    ("地錨張拉、鎖定及防蝕封蓋混凝土", "孔", (5500, 6500, 9000), "含封頭防護", True),
    ("驗收試驗", "孔", (3500, 4500, 6500), "每孔驗收張拉", True),
    ("基本試驗與適用性試驗", "組", (60000, 80000, 120000), "試驗錨數量依規範另計", True),
    ("地錨荷重計 (Load Cell) 監測安裝", "組", (35000, 35000, 35000), "長期監測用(選配)", False),
]
for i, ton in enumerate((30, 60, 100)):
    add(f"預力地錨工程 (永久性 {ton}噸)", [
        (s, u, p[i], n, NEW) if flag else (s, u, p[i], n)
        for s, u, p, n, flag in ANCHOR_ITEMS
    ])

# --- 土釘與格樑 ---
add("土釘與邊坡地樑工程 (RC格樑)", [
    ("打設自鑽式岩栓/土釘 (L=3~6m)", "m", 1800, "含鑽孔、套管及灌漿"),
    ("土釘灌漿材料 (水泥漿體)", "m³", 3500, "連動孔徑與孔距"),
    ("RC 承壓座 / 格子樑 (節點含開挖)", "m", 4500, "提供地錨或土釘反力"),
    ("格樑內植生包/椰纖網", "m²", 450, "格框內綠化"),
])

# --- 微型樁 ---
add("微型樁工程 (Type A - 僅鋼管)", [
    ("山坡作業平台、機具進場與整地", "式", 180000, "機具爬坡與架設"),
    ("空鑽段 (無鋼管保護段之引孔)", "m", 550, "樁頂上方之引孔"),
    ("微型樁實鑽孔 (內徑 Ø150mm)", "m", 1100, "含斜樁鑽孔加價"),
    ("無縫鋼管置入及灌漿 (含螺紋續接/防蝕)", "m", 1500, "厚度依設計，含接頭"),
    ("廢漿處理與排土清運", "m³", 1800, "原為式，改依數量計價"),
    ("RC樁帽", "座", 3500, "單獨施作或與護坡結合"),
    ("試驗樁與載重試驗", "組", 85000, "拉拔試驗"),
])
add("微型樁工程 (Type B - 鋼管+鋼筋)", [
    ("山坡作業平台、機具進場與整地", "式", 180000, "機具爬坡與架設"),
    ("空鑽段 (無鋼管保護段之引孔)", "m", 550, "樁頂上方之引孔"),
    ("微型樁實鑽孔 (內徑 Ø200mm)", "m", 1400, "含斜樁鑽孔加價"),
    ("無縫鋼管置入 (含螺紋續接/防蝕)", "m", 1500, "厚度依設計，含接頭"),
    ("主鋼筋置入與純水泥漿體灌漿", "m", 850, "增加抗彎能力"),
    ("廢漿處理與排土清運", "m³", 1800, "原為式，改依數量計價"),
    ("微型樁RC樁帽", "座", 3500, "單獨施作或與護坡結合"),
    ("連結地樑", "m", 5500, "群樁整合"),
    ("試驗樁與載重試驗", "組", 85000, "拉拔試驗"),
])

# --- 抗滑樁 (Ø1.0 / Ø1.5 / Ø2.0) ---
add("抗滑樁共通項目 (多口徑共用，整案只計一次)", [
    ("全套管鑽機組裝、拆卸與動員", "式", 350000, "重車運輸與組裝"),
    ("山坡作業平台與整地", "式", 180000, "機具爬坡與架設"),
    ("導溝/導牆與樁位施工測量", "m", 3500, "確保定位準確"),
    ("RC 樁帽或抗滑樁連結梁", "m", 12000, "整體抗滑剛性"),
    ("樁體預埋傾斜管與應變計", "組", 85000, "長期變形監測"),
])
PILE_ITEMS = [
    ("全套管機具鑽掘及鋼套管打拔", "m", (6500, 9500, 15000), "不含遇岩盤加價", False),
    ("入岩或嵌岩鑽掘加價", "m", (4500, 6500, 10000), "鑿岩破壞機具耗損", True),
    ("超音波孔壁垂直度檢測 (Koden test)", "孔", (10000, 12000, 15000), "確認鑽孔垂直度", True),
    ("預埋聲測管(CSL)及樁身完整性檢測", "孔", (15000, 18000, 22000), "確認混凝土無斷樁", True),
    ("鋼筋籠組立、吊放與續接器接合", "噸", (38000, 38000, 38000), "含搭接或續接器", False),
    ("特密管水中混凝土澆置 (坍度>20cm)", "m³", (4200, 4200, 4200), "高流動性混凝土", False),
    ("樁頭劣質混凝土敲除 (打石)", "座", (5000, 6500, 8500), "確保樁頭接合品質", True),
    ("劣質泥水沉澱與環保外運", "m³", (1800, 1800, 1800), "廢漿處理", False),
]
for i, dia in enumerate(("1.0", "1.5", "2.0")):
    add(f"抗滑樁工程 (全套管機 內徑 Ø{dia}m)", [
        (s, u, p[i], n, NEW) if flag else (s, u, p[i], n)
        for s, u, p, n, flag in PILE_ITEMS
    ])

# --- RC 擋土牆 ---
add("RC擋土牆工程 (懸臂/扶壁式)", [
    ("基礎開挖、臨時擋土及安全支撐", "m³", 850, "確保開挖面穩定"),
    ("基礎地盤置換或碎石級配處理", "m³", 1200, "承載力確認與地盤改良"),
    ("基礎墊層PC (厚10cm)", "m²", 450, "打底"),
    ("鋼筋組立 (含基礎與牆身)", "噸", 32000, "含加工及綁紮"),
    ("內外牆清水模板組立及拆除", "m²", 850, "牆面及基礎"),
    ("外牆施工架組立及拆除", "m²", 280, "人員施工踩踏用"),
    ("混凝土澆置 (280kgf/cm²)", "m³", 4000, "含搗實、養護及剪力榫"),
    ("牆身PVC洩水管及地工不織布濾層", "處", 350, "防微粒阻塞排水孔"),
    ("牆背級配透水回填及縱向盲溝", "m", 1500, "防止牆背水壓累積"),
    ("牆背一般土方回填與夯實", "m³", 450, "利用原土回填"),
    ("伸縮縫、填縫版及止水帶設置", "m", 650, "防滲漏開裂"),
    ("牆頂RC壓頂處理與防護欄杆", "m", 2800, "防墜落"),
])

# --- 加勁擋土牆 ---
add("加勁擋土牆工程", [
    ("基礎開挖與地盤處理", "m³", 650, "土方開挖"),
    ("底部RC基礎墊座 (Leveling Pad)", "m", 1500, "提供牆面基礎平整度"),
    ("地工合成材 (加勁格網) 鋪設", "m²", 450, "依設計張力"),
    ("加勁帶/金屬網鋪設", "m", 600, "面板式依長度計價"),
    ("預鑄混凝土面板 / 砌塊式(Block) 面板", "m²", 4500, "含面板填縫及伸縮縫"),
    ("包被式袋體組立與植生", "m²", 1200, "柔性牆面面積"),
    ("牆後透水排水層及洩水管", "m²", 650, "加勁牆排水極重要"),
    ("外購粒料回填料源及運輸費", "m³", 850, "提供良好摩擦力"),
    ("牆體粒料回填與分層滾壓夯實", "m³", 550, "壓實度試驗"),
    ("牆頂壓頂RC與護欄", "m", 3500, "頂部收邊"),
])

# --- 重力式 / 石籠 ---
add("重力式/石籠擋土牆工程", [
    ("石籠基礎整平、墊層與隔離不織布", "m²", 850, "防底部淘刷流失"),
    ("重力式擋土牆基礎開挖與PC墊層", "m", 2500, "重力牆底層"),
    ("重力式無筋混凝土擋土牆 (H=2.0m~3.0m)", "m³", 3800, "含模板與澆置"),
    ("牆身PVC洩水管 (含不織布)", "處", 250, "排水減壓"),
    ("蛇籠/石籠組立 (2.0x1.0x1.0m)", "只", 3500, "含鍍鋅鐵絲網、塊石及編布 (護岸亦用此項)"),
    ("箱型石籠組立 (防蝕型)", "只", 4800, "包覆PVC防蝕網"),
])

# --- 被動式防落石網 ---
# (細項, 單位, (500kJ, 1000kJ), 備註, 500kJ新增, 1000kJ新增)
PASSIVE_ITEMS = [
    ("坡面雜木清除與危石整修", "m²", (150, 150), "施作前置作業", False, False),
    ("高山特殊吊運 (索道或直升機代金)", "式", (400000, 500000), "無便道區域必備(視情況選用)", True, False),
    ("鋼柱RC基礎與底板固定", "座", (20000, 25000), "柱底支撐", True, False),
    ("上拉錨索與錨碇微型樁", "組", (35000, 45000), "吸收衝擊拉力關鍵", True, False),
    ("高強度鋼柱及緩衝消能元件", "組", (55000, 85000), "吸收落石能量", False, False),
    ("攔截主網與牽引索組立", "m²", (4500, 5500), "依攔截面積計價", True, False),
    ("內襯菱形次網", "m²", (450, 450), "攔截小型落石", False, False),
]
for i, kj in enumerate(("500kJ", "1000kJ")):
    add(f"高強度防落石網 (被動式 {kj})", [
        (s, u, p[i], n, NEW) if (n5 if i == 0 else n10) else (s, u, p[i], n)
        for s, u, p, n, n5, n10 in PASSIVE_ITEMS
    ])

add("主動式防落石網與坡面防護工程", [
    ("坡面懸吊式施工架組立及拆除", "m²", 650, "陡坡施工作業面"),
    ("主動式防落石網 (菱形網+打設岩栓)", "m²", 1200, "緊貼坡面"),
    ("鋼索格網(加壓型)與岩栓錨碇", "m²", 3800, "緊貼坡面提供圍束力"),
    ("打設岩栓 (L=3m, Ø25mm)", "支", 2500, "坡面穩定加固"),
    ("鋪設植生網 (地工網/椰纖網)", "m²", 180, "防止沖刷及保水"),
    ("坡面噴植草籽植生", "m²", 250, "含客土及養護"),
])
add("掛網噴凝土護坡", [
    ("坡面懸吊式施工架組立及拆除", "m²", 650, "陡坡施工作業面"),
    ("鋪設雙層鋼絲網", "m²", 350, "補強網"),
    ("噴凝土澆置 (厚10cm)", "m²", 1000, "含配比與養護 (鋼絲網另計)"),
    ("噴凝土澆置 (厚15cm)", "m²", 1400, "含配比與養護 (鋼絲網另計)"),
    ("洩水孔與背填排水管", "處", 450, "防止水壓將噴凝土頂破"),
])
add("落石輔助設施與邊坡土方整治", [
    ("落石攔石溝/攔石牆構築", "m", 12000, "RC構造防護槽"),
    ("坡面削坡減載與土方挖填", "m³", 450, "降低邊坡載重"),
    ("坡趾壓腳土石方堆置", "m³", 550, "抵抗滑動剪力"),
])

# --- 護岸及坡趾 ---
add("護岸及坡趾保護工程", [
    ("河川導流、圍堰與施工期抽水", "式", 450000, "水中施工必備"),
    ("基礎拋塊石護趾 (D=30~50cm)", "m³", 1800, "拋石防淘刷深"),
    ("基礎固床工 (RC構造)", "m³", 4500, "含模板、鋼筋及抗沖刷設計"),
    ("重力式RC護岸擋土牆 (H=3.0m)", "m", 32000, "含基礎開挖、鋼筋、模板、澆置"),
    ("護岸護坦、排水孔與預鑄塊", "m²", 2800, "消能與坡趾防護"),
    ("打設鋼板樁護趾 (Type IV, 永久留置)", "m", 15000, "請核對計價單位為樁長或牆長"),
    ("坡面砌塊石 (乾砌, 厚40cm)", "m²", 1800, "含背填碎石墊層"),
    ("坡面砌塊石 (漿砌, 厚40cm)", "m²", 2500, "含水泥砂漿填縫及背填"),
    ("雷諾墊護坡 (厚0.3m)", "m²", 1500, "柔性抗淘刷鋪面"),
])

# --- 排水 ---
add("常規集水管與截水溝", [
    ("橫向集水管 (PVC透水管 內徑 Ø50mm)", "m", 850, "含鑽孔與不織布包覆"),
    ("橫向集水管 (PVC透水管 內徑 Ø100mm)", "m", 1200, "含鑽孔與不織布包覆"),
    ("橫向集水管 (HDPE波紋管 內徑 Ø100mm)", "m", 1400, "高抗壓，含鑽孔"),
    ("橫向集水管 (HDPE波紋管 內徑 Ø150mm)", "m", 1800, "高抗壓，含鑽孔"),
    ("橫向集水管 (不鏽鋼透水管 內徑 Ø50mm)", "m", 2200, "抗鏽蝕設計"),
    ("坡面排水廊道開挖與支撐", "m", 45000, "大規模崩塌地排水主力"),
    ("深層滲井鑽掘與過濾材料回填", "m", 8500, "引導淺層水至深層地層"),
    ("坡面U型截水溝 (W30cm x H30cm)", "m", 1500, "現場澆置"),
    ("坡面U型截水溝 (W60cm x H60cm)", "m", 3200, "現場澆置"),
    ("RC 陰井 / 集水井 (含鑄鐵格柵)", "座", 8000, "統一常規尺寸單價"),
    ("山區跌水工 (RC階梯式)", "座", 18000, "依設計高差調整"),
    ("地下盲溝 (包含碎石級配及透水管)", "m", 2200, "截斷地下水路"),
])
add("水平排水孔工程", [
    ("水平排水孔鑽孔 (L=30~60m)", "m", 2200, "長距離水平鑽掘"),
    ("水平排水管 (透水管含不織布)", "m", 800, "PVC或不鏽鋼依設計"),
    ("孔口保護與集水設施", "處", 8000, "含出水導排"),
    ("機具動員與作業平台", "式", 150000, "山區平台整備"),
])


# ==========================================
# 資料處理函式
# ==========================================
def atomic_write_csv(df, path):
    tmp = path + ".tmp"
    df.to_csv(tmp, index=False, encoding="utf-8-sig")
    os.replace(tmp, path)


def backup_file(path, tag):
    """覆蓋或清空共享檔案前，先備份一份帶時間戳的舊檔"""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(path, os.path.join(BACKUP_DIR, f"{tag}_{ts}_{os.path.basename(path)}"))


def normalize_db(df):
    """驗證並整理資料庫；格式有誤時丟出 ValueError，不會讓整個 App 當掉"""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError("缺少必要欄位：" + "、".join(missing))
    if "備註" not in df.columns:
        df["備註"] = ""
    if "資料來源" not in df.columns:
        df["資料來源"] = SRC_USER
    df = df[ALL_COLS].copy()
    for c in ["主工項", "細項名稱", "單位", "備註", "資料來源"]:
        df[c] = df[c].fillna("").astype(str).str.strip()
    df.loc[df["資料來源"] == "", "資料來源"] = SRC_USER
    price = pd.to_numeric(
        df["單價(元)"].astype(str).str.replace(",", "", regex=False), errors="coerce"
    )
    bad = df[price.isna() | (df["主工項"] == "") | (df["細項名稱"] == "")]
    if len(bad) > 0:
        raise ValueError(
            f"有 {len(bad)} 列的主工項、細項名稱或單價無效 (第一筆在檔案第 {bad.index[0] + 2} 列)"
        )
    df["單價(元)"] = price.round().astype(int)
    df = df.drop_duplicates(subset=["主工項", "細項名稱"], keep="last").reset_index(drop=True)
    return df


DEFAULT_DF = normalize_db(pd.DataFrame(DEFAULT_DB))


def initialize_database():
    """版本不同時才重建資料庫；重建前先備份，並保留同仁自行新增的項目"""
    stored = None
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            stored = f.read().strip()
    if os.path.exists(DB_FILE) and stored == CURRENT_VERSION:
        return

    new_df = DEFAULT_DF.copy()
    if os.path.exists(DB_FILE):
        backup_file(DB_FILE, "before_upgrade")
        try:
            raw = pd.read_csv(DB_FILE, encoding="utf-8-sig")
            if "資料來源" in raw.columns:  # 舊版(v8/v9)沒有此欄，整批視為預設資料而不保留
                old = normalize_db(raw)
                keep = old[~old["資料來源"].isin(DEFAULT_SOURCES)]
                keys = set(zip(new_df["主工項"], new_df["細項名稱"]))
                mask = [(a, b) not in keys for a, b in zip(keep["主工項"], keep["細項名稱"])]
                new_df = pd.concat([new_df, keep[mask]], ignore_index=True)
        except Exception:
            pass
    atomic_write_csv(new_df, DB_FILE)
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(CURRENT_VERSION)


def load_db():
    try:
        return normalize_db(pd.read_csv(DB_FILE, encoding="utf-8-sig"))
    except Exception as e:
        st.error(f"共用資料庫讀取失敗，暫時使用內建預設值：{e}")
        return DEFAULT_DF.copy()


def save_db(df):
    atomic_write_csv(df, DB_FILE)


def read_uploaded_csv(uploaded):
    data = uploaded.getvalue()
    last_err = None
    for enc in ("utf-8-sig", "cp950"):
        try:
            return pd.read_csv(io.BytesIO(data), encoding=enc)
        except UnicodeDecodeError as e:
            last_err = e
    raise ValueError(f"無法判讀檔案編碼 (請存成 UTF-8 CSV)：{last_err}")


def _json_default(o):
    if hasattr(o, "item"):
        return o.item()
    return str(o)


def load_history():
    if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
        return []
    records = []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def save_history(history_list):
    if history_list:
        tmp = HISTORY_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for r in history_list:
                f.write(json.dumps(r, ensure_ascii=False, default=_json_default) + "\n")
        os.replace(tmp, HISTORY_FILE)
    elif os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


def rec_get(rec, *keys, default=0):
    for k in keys:
        if k in rec and rec[k] is not None:
            return rec[k]
    return default


def _clear_history():
    backup_file(HISTORY_FILE, "before_clear")
    save_history([])
    st.session_state["confirm_clear"] = False
    st.session_state["flash"] = "已清空團隊紀錄 (舊檔已備份於 backups 資料夾)。"


# ==========================================
# 初始化與狀態保留
# ==========================================
initialize_database()

# 切換分頁時 Streamlit 會丟棄未渲染元件的狀態，這裡每次執行都重新寫回，
# 避免已填的數量、自訂單價與費率在切換頁面後歸零。
PERSIST_PREFIXES = ("qty_", "prc_", "rate_", "majors", "project_name", "cont_in_tax")
for _k in list(st.session_state.keys()):
    if isinstance(_k, str) and _k.startswith(PERSIST_PREFIXES):
        st.session_state[_k] = st.session_state[_k]

COUNT_UNITS = {"式", "座", "組", "孔", "處", "只", "支", "戶", "測線", "月", "日", "公頃", "套"}

# ==========================================
# 介面
# ==========================================
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stExpander { border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;}
        .metric-card { background-color: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 6px solid #0056b3; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;}
        .align-text { margin-top: 28px; font-size: 16px; line-height: 1.5; }
        .price-text { color: #4CAF50; font-weight: 700; font-size: 16px; }
        .total-text { color: #333333; font-weight: 700; font-size: 16px; }
        .tag-new { color: #b45309; font-size: 12px; border: 1px solid #b45309; border-radius: 4px; padding: 0 4px; margin-left: 6px; }
        hr { margin: 1em 0; border: 0; height: 1px; background: #eaedf0; }
    </style>
""", unsafe_allow_html=True)

st.title("⛰️ 大地工程經費初估與雲端共享資料庫")

with st.sidebar:
    st.header("功能導覽")
    tab = st.radio(
        "功能", ["📊 專案經費初估", "📚 共享單價資料庫管理", "📁 共享歷史估算紀錄"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("#### 🔄 強制同步最新資料庫")
    st.caption("點擊此按鈕即可重新讀取伺服器上最新的資料。")
    if st.button("立即同步更新", use_container_width=True):
        st.rerun()
    st.markdown("---")
    st.caption(
        "⚠️ 資料存放於伺服器本機檔案。若部署在 Streamlit Community Cloud，"
        "重啟後檔案會重置，請定期於「資料庫管理」下載備份。"
    )

flash = st.session_state.pop("flash", None)
if flash:
    st.success(flash)

# ==========================================
# TAB 1: 專案經費初估
# ==========================================
if tab == "📊 專案經費初估":
    db = load_db()

    st.subheader("1. 專案名稱與工程項目設定")
    st.session_state.setdefault("project_name", "某坡地穩定與水保改善工程")
    project_name = st.text_input("專案名稱", key="project_name")

    all_major_items = db["主工項"].drop_duplicates().tolist()
    if "majors" in st.session_state:  # 資料庫更新後，移除已不存在的選項
        st.session_state["majors"] = [m for m in st.session_state["majors"] if m in all_major_items]
    selected_majors = st.multiselect(
        "請選擇本次工程涵蓋的主項目 (可複選)：",
        options=all_major_items,
        key="majors",
        placeholder="點擊展開，例如：大口徑集水井、抗滑樁...",
    )

    selected_details = []

    if selected_majors:
        st.markdown("#### 📝 細項數量與單價設定")
        st.caption("請填寫數量。若需微調單價請修改「自訂單價」；標示「新增待核」者為概估值，請務必核對。")

        for major in selected_majors:
            with st.expander(f"📂 {major}", expanded=True):
                sub_items = db[db["主工項"] == major]

                for _, row in sub_items.iterrows():
                    sub_name = row["細項名稱"]
                    unit = row["單位"]
                    default_price = int(row["單價(元)"])
                    note = row["備註"]
                    tag = f"<span class='tag-new'>{row['資料來源']}</span>" if row["資料來源"] == SRC_NEW else ""

                    qkey = f"qty_{major}|{sub_name}"
                    pkey = f"prc_{major}|{sub_name}"
                    st.session_state.setdefault(pkey, str(default_price))

                    st.markdown(
                        f"**{sub_name}** <span style='color:gray; font-size:13px;'>({note})</span>{tag}",
                        unsafe_allow_html=True,
                    )
                    c_qty, c_ref, c_custom, c_total = st.columns([1, 1, 1, 1])

                    with c_qty:
                        step = 1.0 if unit in COUNT_UNITS else 10.0
                        qty = st.number_input(
                            f"數量 ({unit})", min_value=0.0, step=step, format="%.1f", key=qkey
                        )
                    with c_ref:
                        st.markdown(
                            f"<div class='align-text'>參考價：<span class='price-text'>NT$ {default_price:,}</span></div>",
                            unsafe_allow_html=True,
                        )
                    with c_custom:
                        custom_val = st.text_input("自訂單價(可選)", key=pkey)
                        try:
                            prc = int(float(custom_val.replace(",", "")))
                        except ValueError:
                            prc = default_price
                    with c_total:
                        subtotal = int(qty * prc)
                        st.markdown(
                            f"<div class='align-text'>小計：<span class='total-text'>NT$ {subtotal:,}</span></div>",
                            unsafe_allow_html=True,
                        )

                    st.markdown("<hr>", unsafe_allow_html=True)

                    if qty > 0:
                        selected_details.append({
                            "主工項": major,
                            "細項名稱": sub_name,
                            "數量": qty,
                            "單位": unit,
                            "單價(元)": prc,
                            "複價": subtotal,
                        })

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("2. 間接費用費率設定 (%)")
    st.caption("附屬費用以直接工程費計；依各機關編列規定調整。預備費、設計監造費是否計入營業稅，請依機關規定確認。")

    RATE_DEFAULTS = {
        "rate_osh": 1.5, "rate_qc": 1.0, "rate_env": 0.5, "rate_ins": 0.5, "rate_air": 0.0,
        "rate_mgmt": 10.0, "rate_adj": 0.0, "rate_cont": 5.0, "rate_tax": 5.0, "rate_design": 0.0,
    }
    for _k, _v in RATE_DEFAULTS.items():
        st.session_state.setdefault(_k, _v)

    r1 = st.columns(5)
    osh_pct = r1[0].number_input("勞安衛生費 (%)", step=0.1, key="rate_osh")
    qc_pct = r1[1].number_input("品質管理費 (%)", step=0.1, key="rate_qc")
    env_pct = r1[2].number_input("環境保護費 (%)", step=0.1, key="rate_env")
    ins_pct = r1[3].number_input("營造保險費 (%)", step=0.1, key="rate_ins")
    air_pct = r1[4].number_input("空污費 (%)", step=0.1, key="rate_air", help="依地方環保局公式另行計算者，可先以費率概估")
    r2 = st.columns(5)
    mgmt_pct = r2[0].number_input("包商利潤與管理費 (%)", step=0.5, key="rate_mgmt")
    adj_pct = r2[1].number_input("物價調整費 (%)", step=0.5, key="rate_adj")
    cont_pct = r2[2].number_input("工程預備費 (%)", step=0.5, key="rate_cont")
    tax_pct = r2[3].number_input("營業稅率 (%)", step=0.5, key="rate_tax")
    design_pct = r2[4].number_input("設計監造費 (%)", step=0.5, key="rate_design", help="以承包工程費(未稅)為基礎，預設不計")
    st.session_state.setdefault("cont_in_tax", False)
    cont_in_tax = st.checkbox("預備費計入營業稅基礎 (預設：預備費另列於稅後)", key="cont_in_tax")

    st.markdown("---")

    st.subheader("📊 3. 估算結果分析與明細")
    if len(selected_details) > 0:
        df_selected = pd.DataFrame(selected_details)
        direct_cost = int(df_selected["複價"].sum())

        attach_cost = int(direct_cost * (osh_pct + qc_pct + env_pct + ins_pct + air_pct) / 100)
        sub1 = direct_cost + attach_cost
        mgmt_cost = int(sub1 * mgmt_pct / 100)
        sub2 = sub1 + mgmt_cost
        adj_cost = int(sub2 * adj_pct / 100)
        sub3 = sub2 + adj_cost  # 承包工程費 (未稅)
        cont_cost = int(sub3 * cont_pct / 100)

        if cont_in_tax:
            tax_cost = int((sub3 + cont_cost) * tax_pct / 100)
            contract_total = sub3 + cont_cost + tax_cost
        else:
            tax_cost = int(sub3 * tax_pct / 100)
            contract_total = sub3 + tax_cost + cont_cost
        design_cost = int(sub3 * design_pct / 100)
        total_cost = contract_total + design_cost

        parts = [
            ("直接工程費", direct_cost),
            ("勞安/品管/環保/保險/空污", attach_cost),
            (f"包商利潤與管理費 ({mgmt_pct}%)", mgmt_cost),
            (f"物價調整費 ({adj_pct}%)", adj_cost),
        ]
        if cont_in_tax:
            parts += [(f"工程預備費 ({cont_pct}%)", cont_cost), (f"營業稅 ({tax_pct}%)", tax_cost)]
        else:
            parts += [(f"營業稅 ({tax_pct}%)", tax_cost), (f"工程預備費 ({cont_pct}%)", cont_cost)]
        parts.append((f"設計監造費 ({design_pct}%)", design_cost))

        st.markdown(f"""
        <div class="metric-card">
            <p style="margin:0; color:#555; font-size:16px;">總經費初估</p>
            <h1 style="margin:0; color:#0056b3; font-size:36px; padding-top:5px;">NT$ {total_cost:,}</h1>
        </div>
        """, unsafe_allow_html=True)

        res_col1, res_col2 = st.columns([1.5, 1])

        with res_col1:
            st.write("##### 📝 直接工程費完整明細")
            st.dataframe(
                df_selected.style.format({"數量": "{:,.1f}", "單價(元)": "{:,.0f}", "複價": "{:,.0f}"}),
                use_container_width=True, hide_index=True,
            )
            st.download_button(
                "📥 下載本次估算明細 (CSV)",
                data=df_selected.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"{project_name}_估算明細.csv",
                mime="text/csv",
            )

            st.write("##### 📊 各主工項小計")
            by_major = df_selected.groupby("主工項", sort=False)["複價"].sum().reset_index()
            st.dataframe(by_major.style.format({"複價": "{:,.0f}"}), use_container_width=True, hide_index=True)

            st.write("##### 📊 經費結構摘要")
            summary_table = pd.DataFrame({
                "費用項目": [p[0] for p in parts] + ["總計"],
                "金額 (NT$)": [p[1] for p in parts] + [total_cost],
            })
            st.dataframe(summary_table.style.format({"金額 (NT$)": "{:,.0f}"}), use_container_width=True, hide_index=True)

        with res_col2:
            st.write("##### 📈 經費佔比視覺化")
            chart_data = pd.DataFrame(
                [{"費用類別": n, "金額": a} for n, a in parts if a > 0]
            )
            chart = alt.Chart(chart_data).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("金額:Q", title="金額 (NT$)", axis=alt.Axis(format="d")),
                y=alt.Y("費用類別:N", sort="-x", title=""),
                color=alt.Color("費用類別:N", legend=None),
                tooltip=["費用類別", alt.Tooltip("金額:Q", format=",d")],
            ).properties(height=350).configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 將專案發佈至共享歷史紀錄", type="primary", use_container_width=True):
                current_history = load_history()
                record = {
                    "專案名稱": project_name,
                    "直接工程費": direct_cost,
                    "附屬費用": attach_cost,
                    "管理費": mgmt_cost,
                    "物價調整費": adj_cost,
                    "預備費": cont_cost,
                    "營業稅": tax_cost,
                    "設計監造費": design_cost,
                    "總經費": total_cost,
                    "預備費計入稅基": bool(cont_in_tax),
                    "時間": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "細項明細": df_selected.to_dict("records"),
                }
                current_history.append(record)
                save_history(current_history)
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
        st.caption("任何人下載修改後重新上傳，將覆蓋所有人的資料庫 (覆蓋前系統會自動備份舊檔)。")
        st.download_button(
            "📥 下載 CSV 模板",
            data=db.to_csv(index=False).encode("utf-8-sig"),
            file_name="geotech_database_shared.csv",
            mime="text/csv",
        )

    with c_up:
        st.markdown("#### ⬆️ 步驟 2: 匯入最新單價表")
        st.caption("必要欄位：主工項、細項名稱、單位、單價(元)；備註、資料來源為選填。")
        uploaded_file = st.file_uploader("上傳更新後的 CSV 檔案", type=["csv"], label_visibility="collapsed")
        if uploaded_file is not None:
            try:
                new_db = normalize_db(read_uploaded_csv(uploaded_file))
                st.info(f"檔案檢查通過：共 {len(new_db)} 筆 (目前資料庫 {len(db)} 筆)。確認後將覆蓋所有人的資料庫。")
                if st.button("✅ 確認覆蓋共用資料庫", type="primary"):
                    backup_file(DB_FILE, "before_upload")
                    save_db(new_db)
                    st.session_state["flash"] = "✅ 共用資料庫已全面更新！(舊檔已備份於 backups 資料夾)"
                    st.rerun()
            except Exception as e:
                st.error(f"檔案無法匯入：{e}")

    st.markdown("---")
    st.markdown("#### 🔍 目前資料庫檢視與單筆新增")

    search_query = st.text_input("🔍 搜尋工項名稱", "", placeholder="例如：集水井")
    if search_query:
        mask = (
            db["主工項"].str.contains(search_query, case=False, regex=False)
            | db["細項名稱"].str.contains(search_query, case=False, regex=False)
        )
        display_db = db[mask]
    else:
        display_db = db
    st.caption(f"共 {len(display_db)} 筆。「資料來源」欄：沿用原表＝你原本的數值；新增待核＝本次新增或調整，請核對。")
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
                new_major, new_sub = new_major.strip(), new_sub.strip()
                try:
                    parsed_price = int(float(new_price.replace(",", "")))
                except ValueError:
                    parsed_price = None
                if not new_major or not new_sub:
                    st.error("主工項名稱與細項名稱不可空白！")
                elif parsed_price is None:
                    st.error("單價請輸入有效數字！")
                else:
                    current_db = load_db()
                    exists = ((current_db["主工項"] == new_major) & (current_db["細項名稱"] == new_sub)).any()
                    if exists:
                        st.error("此主工項下已有相同名稱的細項，請改用下載、修改、上傳的方式更新單價。")
                    else:
                        new_row = pd.DataFrame([{
                            "主工項": new_major, "細項名稱": new_sub, "單位": new_unit.strip(),
                            "單價(元)": parsed_price, "備註": new_note.strip(), "資料來源": SRC_USER,
                        }])
                        save_db(pd.concat([current_db, new_row], ignore_index=True))
                        st.session_state["flash"] = "新增成功！其他同仁重新整理網頁即可看到。"
                        st.rerun()

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
            title = f"📌 [{record.get('時間', '')}] {record.get('專案名稱', '(未命名)')} ─ 總經費: NT$ {int(rec_get(record, '總經費')):,}"
            with st.expander(title):
                st.markdown("##### 📊 專案費用總結")
                m1 = st.columns(4)
                m1[0].metric("直接工程費", f"NT$ {int(rec_get(record, '直接工程費')):,}")
                m1[1].metric("附屬費用 (安全/品管/保險)", f"NT$ {int(rec_get(record, '附屬費用', '安全品管等附屬', '雜項費')):,}")
                m1[2].metric("管理費", f"NT$ {int(rec_get(record, '管理費')):,}")
                m1[3].metric("物價調整費", f"NT$ {int(rec_get(record, '物價調整費')):,}")
                m2 = st.columns(4)
                m2[0].metric("預備費", f"NT$ {int(rec_get(record, '預備費')):,}")
                m2[1].metric("營業稅", f"NT$ {int(rec_get(record, '營業稅')):,}")
                m2[2].metric("設計監造費", f"NT$ {int(rec_get(record, '設計監造費')):,}")
                m2[3].metric("總經費", f"NT$ {int(rec_get(record, '總經費')):,}")

                st.markdown("##### 📝 專案工程細項明細")
                if record.get("細項明細"):
                    detail_df = pd.DataFrame(record["細項明細"])
                    st.dataframe(
                        detail_df.style.format({"數量": "{:,.1f}", "單價(元)": "{:,.0f}", "複價": "{:,.0f}"}),
                        use_container_width=True, hide_index=True,
                    )
                    for row in record["細項明細"]:
                        row_export = dict(row)
                        row_export["專案名稱"] = record.get("專案名稱", "")
                        row_export["估算時間"] = record.get("時間", "")
                        all_export_data.append(row_export)
                else:
                    st.warning("舊版紀錄未儲存明細。")

        st.markdown("---")

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

        with col_btn1:
            history_summary_df = pd.DataFrame(history_data).drop(columns=["細項明細"], errors="ignore")
            st.download_button(
                "📥 下載歷史紀錄 (僅總表 CSV)",
                data=history_summary_df.to_csv(index=False).encode("utf-8-sig"),
                file_name="history_summary.csv", mime="text/csv", use_container_width=True,
            )

        with col_btn2:
            if all_export_data:
                export_df = pd.DataFrame(all_export_data)
                cols = ["專案名稱", "估算時間"] + [c for c in export_df.columns if c not in ["專案名稱", "估算時間"]]
                st.download_button(
                    "📥 下載歷史紀錄 (含所有細項明細 CSV)",
                    data=export_df[cols].to_csv(index=False).encode("utf-8-sig"),
                    file_name="history_full_details.csv", mime="text/csv", use_container_width=True,
                )

        with col_btn3:
            st.checkbox("我了解將清空所有同仁的紀錄 (系統會先自動備份)", key="confirm_clear")
            st.button(
                "🗑 清空所有團隊紀錄 (危險操作)",
                use_container_width=True,
                disabled=not st.session_state.get("confirm_clear", False),
                on_click=_clear_history,
            )
    else:
        st.info("目前尚無團隊估算紀錄。")

# ==========================================
# 頁尾備註
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 13px;'>
        📌 <b>資料來源與免責聲明備註：</b><br>
        1. 本系統工項之拆分邏輯參考<b>行政院公共工程委員會 (PCCES) 價格資料庫編碼慣例</b>編製。預設單價為<b>概估參考值</b>，尚未逐項對照最新 PCCES 價格資料庫或標案決標資料，使用前請自行核對。<br>
        2. 工程造價會因現地地質條件（如卵礫石層、岩盤硬度）、施工動線難易度與物價波動而有顯著差異。表中單價僅供基準參考。<br>
        3. 本系統提供之數據與試算結果僅供<b>專案初期經費編列、可行性評估參考</b>，不具備法律或合約約束力。正式經費應依正式地質鑽探報告、詳細設計圖說及預算書為準。
    </div>
    """,
    unsafe_allow_html=True,
)
