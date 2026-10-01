import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(
    page_title="大地工程經費初估與單價資料庫",
    page_icon="⛰️️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 資料庫與版本控制檔案路徑
# ==========================================
DB_FILE = 'shared_cost_db.csv'
HISTORY_FILE = 'shared_history.csv'
VERSION_FILE = 'db_version.txt'
CURRENT_VERSION = 'v9_professional_expansion' # 系統更新版號

# ==========================================
# 初始專業預設資料庫 (全尺寸、全實務細項補齊)
# ==========================================
DEFAULT_DB = [
    # --- 【前期調查、測量與監測儀器】 ---
    {"主工項": "前期調查、測量與監測儀器", "細項名稱": "岩心鑽探及試驗 (含SPT及室內試驗)", "單位": "孔", "單價(元)": 65000, "備註": "依深度30m計估"},
    {"主工項": "前期調查、測量與監測儀器", "細項名稱": "地電阻探測 (2D/3D)", "單位": "測線", "單價(元)": 45000, "備註": "地下水及滑動面研判"},
    {"主工項": "前期調查、測量與監測儀器", "細項名稱": "空拍地形及LiDAR測量", "單位": "公頃", "單價(元)": 15000, "備註": "基本面積起算"},
    {"主工項": "前期調查、測量與監測儀器", "細項名稱": "傾斜管設置 (含套管與保護蓋)", "單位": "m", "單價(元)": 1800, "備註": "監測深部滑動"},
    {"主工項": "前期調查、測量與監測儀器", "細項名稱": "地下水位觀測井設置", "單位": "m", "單價(元)": 2200, "備註": "含透水管及濾料"},
    {"主工項": "前期調查、測量與監測儀器", "細項名稱": "地表伸縮計安裝", "單位": "組", "單價(元)": 35000, "備註": "裂縫位移監測"},
    {"主工項": "前期調查、測量與監測儀器", "細項名稱": "鄰房現況鑑定 (施工前/後)", "單位": "戶", "單價(元)": 15000, "備註": "市區邊坡必備"},
    {"主工項": "前期調查、測量與監測儀器", "細項名稱": "生態檢核作業費", "單位": "式", "單價(元)": 150000, "備註": "公共工程必備程序"},

    # --- 【假設與開場工程】 ---
    {"主工項": "假設與開場工程", "細項名稱": "機具動員與復員", "單位": "式", "單價(元)": 150000, "備註": "依規模調整"},
    {"主工項": "假設與開場工程", "細項名稱": "臨時水電設施與發電機租用", "單位": "月", "單價(元)": 35000, "備註": "無市電區域必需"},
    {"主工項": "假設與開場工程", "細項名稱": "施工圍籬、紐澤西護欄及告示牌", "單位": "m", "單價(元)": 1200, "備註": "安全阻隔"},
    {"主工項": "假設與開場工程", "細項名稱": "臨時沉砂池與施工期逕流廢水處理", "單位": "式", "單價(元)": 180000, "備註": "水保法規要求"},
    {"主工項": "假設與開場工程", "細項名稱": "河川/溪溝臨時導流與圍堰", "單位": "m", "單價(元)": 4500, "備註": "擋水設施"},
    {"主工項": "假設與開場工程", "細項名稱": "施工期全天候抽水機具作業", "單位": "日", "單價(元)": 3500, "備註": "地下水位高區域"},
    {"主工項": "假設與開場工程", "細項名稱": "山區單軌車或索道運搬設備", "單位": "m", "單價(元)": 1500, "備註": "無便道物料運輸"},
    {"主工項": "假設與開場工程", "細項名稱": "樹木砍伐與林地障礙物清除", "單位": "公頃", "單價(元)": 250000, "備註": "開闢作業帶"},
    {"主工項": "假設與開場工程", "細項名稱": "施工臨時便道 (山區土方開挖與夯實)", "單位": "m", "單價(元)": 1500, "備註": "依便道長度計價"},
    {"主工項": "假設與開場工程", "細項名稱": "土方合法外運棄置 (B1/B2)", "單位": "m³", "單價(元)": 850, "備註": "含棄土證明"},

    # --- 【大口徑集水井 (內徑 3.5m 深井)】 ---
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "井口護頂RC與導溝", "單位": "座", "單價(元)": 150000, "備註": "含開挖、配筋與澆置"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "井筒土方人工/機具開挖 (內徑3.5m)", "單位": "m³", "單價(元)": 2200, "備註": "含局限空間吊搬運與抽水"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "遇岩盤或孤石破碎開挖加價", "單位": "m³", "單價(元)": 1800, "備註": "增加鑿岩費用"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "鋼襯鐵/波形鋼板環片組立", "單位": "m", "單價(元)": 85000, "備註": "依深度計價"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "鋼環片防蝕塗裝及接縫止水條", "單位": "m", "單價(元)": 6500, "備註": "防鏽與防砂流失"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "環片背填灌漿 (固結/止水)", "單位": "m", "單價(元)": 4500, "備註": "依深度計量"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "輻射管孔口管、止水閥與防護", "單位": "處", "單價(元)": 15000, "備註": "控制湧水及後續維護"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "輻射排水管-機具鑽孔", "單位": "m", "單價(元)": 1200, "備註": "水平鑽掘"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "輻射排水管-PVC管及不織布包覆", "單位": "m", "單價(元)": 600, "備註": "含湧水引導處理"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "井底濾層或透水碎石墊層", "單位": "m³", "單價(元)": 2800, "備註": "底部防淘刷湧砂"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "底部封底混凝土 (3000psi)", "單位": "m³", "單價(元)": 4500, "備註": "含抗揚壓設計"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "井內揚水/排水豎管 (PVC/HDPE)", "單位": "m", "單價(元)": 1200, "備註": "將井底積水向上抽排用豎管"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "沉水式抽水機與自動控制盤", "單位": "組", "單價(元)": 85000, "備註": "含安裝配線"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "出水管線至坡外之導排水與消能工", "單位": "m", "單價(元)": 2500, "備註": "接續至外部水路"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "井內不鏽鋼爬梯 (含防墜落設施)", "單位": "m", "單價(元)": 3500, "備註": "SUS304"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "局限空間通風、照明及氣體偵測設備", "單位": "月", "單價(元)": 55000, "備註": "工安規定必需項目"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "井口吊運設備(三腳架/卷揚機)及圍籬", "單位": "式", "單價(元)": 85000, "備註": "設備設置"},
    {"主工項": "大口徑集水井 (內徑 3.5m 深井)", "細項名稱": "頂部格柵安全蓋板 (重型)", "單位": "座", "單價(元)": 65000, "備註": "鍍鋅鋼格柵"},

    # --- 【大口徑集水井 (內徑 4.5m / 6.0m 差異部分)】 ---
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "井筒土方人工/機具開挖 (內徑4.5m)", "單位": "m³", "單價(元)": 2600, "備註": "單價較高"},
    {"主工項": "大口徑集水井 (內徑 4.5m 深井)", "細項名稱": "鋼襯鐵/波形鋼板環片組立", "單位": "m", "單價(元)": 115000, "備註": "依深度計價"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "井筒土方人工/機具開挖 (內徑6.0m)", "單位": "m³", "單價(元)": 3200, "備註": "單價較高"},
    {"主工項": "大口徑集水井 (內徑 6.0m 深井)", "細項名稱": "鋼襯鐵/波形鋼板環片組立", "單位": "m", "單價(元)": 165000, "備註": "依深度計價"},
    # (註：實務上4.5m與6.0m其它孔口管、排水、抽水機等細項可直接點選上方3.5m修改數量與單價，為求介面不冗長，此處精簡共用邏輯)

    # --- 【預力地錨工程 (永久性 30噸 / 60噸 / 100噸)】 ---
    {"主工項": "預力地錨工程", "細項名稱": "坡面施工架組立與拆除", "單位": "m²", "單價(元)": 450, "備註": "高處鑽孔張拉作業必備"},
    {"主工項": "預力地錨工程", "細項名稱": "套管鑽孔 (30T~60T 自由段與錨定段)", "單位": "m", "單價(元)": 1500, "備註": "一般土壤/卵礫石"},
    {"主工項": "預力地錨工程", "細項名稱": "套管鑽孔 (100T大孔徑 自由段與錨定段)", "單位": "m", "單價(元)": 2200, "備註": "大噸數孔徑"},
    {"主工項": "預力地錨工程", "細項名稱": "斜向鑽孔或遇岩盤加價", "單位": "m", "單價(元)": 850, "備註": "鑽機傾斜或鑽岩"},
    {"主工項": "預力地錨工程", "細項名稱": "鋼絞線及防蝕套管組裝 (30T, 3~4股)", "單位": "m", "單價(元)": 750, "備註": "含PE管、間隔器與預留1m張拉段"},
    {"主工項": "預力地錨工程", "細項名稱": "鋼絞線及防蝕套管組裝 (60T, 5~7股)", "單位": "m", "單價(元)": 1100, "備註": "含PE管、間隔器與預留1m張拉段"},
    {"主工項": "預力地錨工程", "細項名稱": "鋼絞線及防蝕套管組裝 (100T, 9~12股)", "單位": "m", "單價(元)": 1800, "備註": "含PE管、間隔器與預留1m張拉段"},
    {"主工項": "預力地錨工程", "細項名稱": "洗孔、排氣管與一次灌漿", "單位": "m", "單價(元)": 450, "備註": "全孔灌漿"},
    {"主工項": "預力地錨工程", "細項名稱": "錨定段二次高壓灌漿", "單位": "m", "單價(元)": 650, "備註": "提升握裹力"},
    {"主工項": "預力地錨工程", "細項名稱": "錨頭組件 (錨具/承壓鋼墊板/防鏽油脂)", "單位": "組", "單價(元)": 8500, "備註": "含蓋"},
    {"主工項": "預力地錨工程", "細項名稱": "地錨張拉、鎖定及防蝕封蓋混凝土", "單位": "孔", "單價(元)": 6500, "備註": "含封頭防護"},
    {"主工項": "預力地錨工程", "細項名稱": "基本試驗、適用性試驗與驗收試驗", "單位": "式", "單價(元)": 120000, "備註": "規範要求之檢測"},
    {"主工項": "預力地錨工程", "細項名稱": "地錨荷重計 (Load Cell) 監測安裝", "單位": "組", "單價(元)": 35000, "備註": "長期監測"},

    # --- 【土釘與邊坡地樑工程】 ---
    {"主工項": "土釘與邊坡地樑工程 (RC格樑)", "細項名稱": "打設自鑽式岩栓/土釘 (L=3~6m)", "單位": "m", "單價(元)": 1800, "備註": "含鑽孔、套管及灌漿"},
    {"主工項": "土釘與邊坡地樑工程 (RC格樑)", "細項名稱": "土釘灌漿材料 (水泥漿體)", "單位": "m³", "單價(元)": 3500, "備註": "連動孔徑與孔距"},
    {"主工項": "土釘與邊坡地樑工程 (RC格樑)", "細項名稱": "RC 承壓座 / 格子樑 (節點含開挖)", "單位": "m", "單價(元)": 4500, "備註": "提供地錨或土釘反力"},
    {"主工項": "土釘與邊坡地樑工程 (RC格樑)", "細項名稱": "格樑內植生植生包/椰纖網", "單位": "m²", "單價(元)": 450, "備註": "格框內綠化"},

    # --- 【微型樁工程】 ---
    {"主工項": "微型樁工程", "細項名稱": "山坡作業平台、機具進場與整地", "單位": "式", "單價(元)": 180000, "備註": "機具爬坡與架設"},
    {"主工項": "微型樁工程", "細項名稱": "空鑽段 (無鋼管保護段之引孔)", "單位": "m", "單價(元)": 550, "備註": "樁頂上方之引孔"},
    {"主工項": "微型樁工程", "細項名稱": "微型樁實鑽孔 (內徑 Ø150mm)", "單位": "m", "單價(元)": 1100, "備註": "含斜樁鑽孔加價"},
    {"主工項": "微型樁工程", "細項名稱": "微型樁實鑽孔 (內徑 Ø200mm)", "單位": "m", "單價(元)": 1400, "備註": "含斜樁鑽孔加價"},
    {"主工項": "微型樁工程", "細項名稱": "無縫鋼管/螺紋續接器/防蝕處理", "單位": "m", "單價(元)": 1500, "備註": "厚度依設計，含接頭"},
    {"主工項": "微型樁工程", "細項名稱": "主鋼筋置入與純水泥漿體灌漿", "單位": "m", "單價(元)": 850, "備註": "增加抗彎能力"},
    {"主工項": "微型樁工程", "細項名稱": "廢漿處理與排土清運", "單位": "式", "單價(元)": 65000, "備註": "環保要求"},
    {"主工項": "微型樁工程", "細項名稱": "微型樁RC樁帽或連結地樑", "單位": "m", "單價(元)": 5500, "備註": "群樁整合"},
    {"主工項": "微型樁工程", "細項名稱": "微型樁試驗樁與載重試驗", "單位": "組", "單價(元)": 85000, "備註": "拉拔試驗"},

    # --- 【抗滑樁與排樁工程 (內徑 Ø1.0m, Ø1.5m, Ø2.0m)】 ---
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "全套管鑽機組裝、拆卸與動員", "單位": "式", "單價(元)": 350000, "備註": "重車運輸與組裝"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "導溝/導牆與樁位施工測量", "單位": "m", "單價(元)": 3500, "備註": "確保定位準確"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "全套管機鑽掘及拔管 (內徑 Ø1.5m)", "單位": "m", "單價(元)": 9500, "備註": "一般土層"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "全套管機鑽掘及拔管 (內徑 Ø2.0m)", "單位": "m", "單價(元)": 15000, "備註": "大口徑排樁"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "入岩或嵌岩鑽掘加價", "單位": "m", "單價(元)": 6500, "備註": "鑿岩破壞機具耗損"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "樁壁垂直度超音波檢測 (Koden test)", "單位": "孔", "單價(元)": 12000, "備註": "確認鑽孔垂直度"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "預埋聲測管(CSL)及樁身完整性檢測", "單位": "孔", "單價(元)": 18000, "備註": "確認混凝土無斷樁"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "鋼筋籠組立、吊放與續接器接合", "單位": "噸", "單價(元)": 38000, "備註": "含搭接或續接器"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "特密管水中混凝土澆置 (坍度>20cm)", "單位": "m³", "單價(元)": 4200, "備註": "高流動性混凝土"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "樁頭劣質混凝土敲除 (打石)", "單位": "座", "單價(元)": 6500, "備註": "確保樁頭接合品質"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "RC 樁帽或抗滑樁連結梁", "單位": "m", "單價(元)": 12000, "備註": "整體抗滑剛性"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "樁體預埋傾斜管與應變計", "單位": "組", "單價(元)": 85000, "備註": "長期變形監測"},
    {"主工項": "抗滑樁與連續壁工程", "細項名稱": "劣質泥水沉澱與環保外運", "單位": "m³", "單價(元)": 1800, "備註": "廢漿處理"},

    # --- 【擋土牆工程 (懸臂式 / 扶壁式)】 ---
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "基礎開挖、臨時擋土及安全支撐", "單位": "m³", "單價(元)": 850, "備註": "確保開挖面穩定"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "基礎地盤置換或碎石級配處理", "單位": "m³", "單價(元)": 1200, "備註": "承載力確認與地盤改良"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "基礎墊層PC (厚10cm)", "單位": "m²", "單價(元)": 450, "備註": "打底"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "鋼筋組立 (含基礎與牆身)", "單位": "噸", "單價(元)": 32000, "備註": "含加工及綁紮"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "內外牆清水模板組立及拆除", "單位": "m²", "單價(元)": 850, "備註": "牆面及基礎"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "外牆施工架組立及拆除", "單位": "m²", "單價(元)": 280, "備註": "人員施工踩踏用"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "混凝土澆置 (280kgf/cm²)", "單位": "m³", "單價(元)": 4000, "備註": "含搗實、養護及剪力榫"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "牆身PVC洩水管及地工不織布濾層", "單位": "處", "單價(元)": 350, "備註": "防微粒阻塞排水孔"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "牆背級配透水回填及縱向盲溝", "單位": "m", "單價(元)": 1500, "備註": "防止牆背水壓累積"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "牆背一般土方回填與夯實", "單位": "m³", "單價(元)": 450, "備註": "利用原土回填"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "伸縮縫、填縫版及止水帶設置", "單位": "m", "單價(元)": 650, "備註": "防滲漏開裂"},
    {"主工項": "RC擋土牆工程 (懸臂/扶壁式)", "細項名稱": "牆頂RC壓頂處理與防護欄杆", "單位": "m", "單價(元)": 2800, "備註": "防墜落"},

    # --- 【加勁擋土牆工程】 ---
    {"主工項": "加勁擋土牆工程", "細項名稱": "基礎開挖與地盤處理", "單位": "m³", "單價(元)": 650, "備註": "土方開挖"},
    {"主工項": "加勁擋土牆工程", "細項名稱": "底部RC基礎墊座 (Leveling Pad)", "單位": "m", "單價(元)": 1500, "備註": "提供牆面基礎平整度"},
    {"主工項": "加勁擋土牆工程", "細項名稱": "地工合成材 (加勁格網/加勁帶) 鋪設", "單位": "m²", "單價(元)": 450, "備註": "依設計張力"},
    {"主工項": "加勁擋土牆工程", "細項名稱": "預鑄混凝土面板 / 砌塊式(Block) 面板", "單位": "m²", "單價(元)": 4500, "備註": "含面板填縫及伸縮縫"},
    {"主工項": "加勁擋土牆工程", "細項名稱": "牆後透水排水層及洩水管", "單位": "m²", "單價(元)": 650, "備註": "加勁牆排水極重要"},
    {"主工項": "加勁擋土牆工程", "細項名稱": "包被式袋體組立與植生", "單位": "m²", "單價(元)": 1200, "備註": "柔性牆面面積"},
    {"主工項": "加勁擋土牆工程", "細項名稱": "外購粒料回填料源及運輸費", "單位": "m³", "單價(元)": 850, "備註": "提供良好摩擦力"},
    {"主工項": "加勁擋土牆工程", "細項名稱": "牆體粒料回填與分層滾壓夯實", "單位": "m³", "單價(元)": 550, "備註": "壓實度試驗"},
    {"主工項": "加勁擋土牆工程", "細項名稱": "牆頂壓頂RC與護欄", "單位": "m", "單價(元)": 3500, "備註": "頂部收邊"},

    # --- 【重力式/蛇籠擋土牆】 ---
    {"主工項": "重力式/石籠擋土牆工程", "細項名稱": "石籠基礎整平、墊層與隔離不織布", "單位": "m²", "單價(元)": 850, "備註": "防底部淘刷流失"},
    {"主工項": "重力式/石籠擋土牆工程", "細項名稱": "重力式擋土牆基礎開挖與PC墊層", "單位": "m", "單價(元)": 2500, "備註": "重力牆底層"},
    {"主工項": "重力式/石籠擋土牆工程", "細項名稱": "重力式無筋混凝土擋土牆 (H=2.0m~3.0m)", "單位": "m³", "單價(元)": 3800, "備註": "含模板與澆置"},
    {"主工項": "重力式/石籠擋土牆工程", "細項名稱": "牆身PVC洩水管 (含不織布)", "單位": "處", "單價(元)": 250, "備註": "排水減壓"},
    {"主工項": "重力式/石籠擋土牆工程", "細項名稱": "蛇籠/箱型石籠組立 (含防蝕網與塊石)", "單位": "只", "單價(元)": 4500, "備註": "合併防蝕型規格"},

    # --- 【防落石網與防護工程】 ---
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "坡面雜木清除與危石整修", "單位": "m²", "單價(元)": 150, "備註": "施作前置作業"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "高山特殊吊運 (索道或直升機代金)", "單位": "式", "單價(元)": 500000, "備註": "無便道區域必備(視情況選用)"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "被動網：鋼柱RC基礎與底板固定", "單位": "座", "單價(元)": 25000, "備註": "柱底支撐"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "被動網：上拉錨索與錨碇微型樁", "單位": "組", "單價(元)": 45000, "備註": "吸收衝擊拉力關鍵"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "被動網：高強度鋼柱及緩衝鋼纜 (1000kJ)", "單位": "組", "單價(元)": 85000, "備註": "消能元件"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "被動網：攔截主網與牽引索組立", "單位": "m²", "單價(元)": 5500, "備註": "依攔截面積計價"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "被動網：內襯菱形次網", "單位": "m²", "單價(元)": 450, "備註": "攔截小型落石"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "主動網：鋼索格網(加壓型)與岩栓錨碇", "單位": "m²", "單價(元)": 3800, "備註": "緊貼坡面提供圍束力"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "落石攔石溝/攔石牆構築", "單位": "m", "單價(元)": 12000, "備註": "RC構造防護槽"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "落石能量分析與模擬 (2D/3D)", "單位": "式", "單價(元)": 180000, "備註": "設計階段模擬計算"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "坡面懸吊式施工架組立及拆除", "單位": "m²", "單價(元)": 650, "備註": "陡坡施工作業面"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "掛網噴凝土：鋪設雙層鋼絲網", "單位": "m²", "單價(元)": 350, "備註": "補強網"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "掛網噴凝土：噴槍澆置 (厚10~15cm)", "單位": "m²", "單價(元)": 1200, "備註": "含配比與養護"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "掛網噴凝土：洩水孔與背填排水管", "單位": "處", "單價(元)": 450, "備註": "防止水壓將噴凝土頂破"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "坡面削坡減載與土方挖填", "單位": "m³", "單價(元)": 450, "備註": "降低邊坡載重"},
    {"主工項": "防落石網與坡面防護工程", "細項名稱": "坡趾壓腳土石方堆置", "單位": "m³", "單價(元)": 550, "備註": "抵抗滑動剪力"},

    # --- 【護岸及坡趾保護工程】 ---
    {"主工項": "護岸及坡趾保護工程", "細項名稱": "河川導流、圍堰與施工期抽水", "單位": "式", "單價(元)": 450000, "備註": "水中施工必備"},
    {"主工項": "護岸及坡趾保護工程", "細項名稱": "基礎拋塊石護趾 (D=30~50cm)", "單位": "m³", "單價(元)": 1800, "備註": "拋石防淘刷深"},
    {"主工項": "護岸及坡趾保護工程", "細項名稱": "基礎固床工 (RC構造)", "單位": "m³", "單價(元)": 4500, "備註": "含模板、鋼筋及抗沖刷設計"},
    {"主工項": "護岸及坡趾保護工程", "細項名稱": "重力式RC護岸擋土牆", "單位": "m", "單價(元)": 32000, "備註": "含基礎開挖、鋼筋、模板、澆置"},
    {"主工項": "護岸及坡趾保護工程", "細項名稱": "護岸護坦、排水孔與預鑄塊", "單位": "m²", "單價(元)": 2800, "備註": "消能與坡趾防護"},
    {"主工項": "護岸及坡趾保護工程", "細項名稱": "打設鋼板樁護趾 (Type IV, 永久留置)", "單位": "m", "單價(元)": 15000, "備註": "含打拔、材料費及防淘刷"},
    {"主工項": "護岸及坡趾保護工程", "細項名稱": "坡面砌塊石 (乾砌/漿砌, 厚40cm)", "單位": "m²", "單價(元)": 2500, "備註": "含背填與砂漿填縫"},
    {"主工項": "護岸及坡趾保護工程", "細項名稱": "雷諾墊護坡 (厚0.3m)", "單位": "m²", "單價(元)": 1500, "備註": "柔性抗淘刷鋪面"},

    # --- 【常規排水工程】 ---
    {"主工項": "常規集水管與截水溝", "細項名稱": "橫向集水管 (PVC透水管 內徑 Ø50mm)", "單位": "m", "單價(元)": 850, "備註": "含鑽孔與不織布包覆"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "橫向集水管 (HDPE波紋管 內徑 Ø100mm)", "單位": "m", "單價(元)": 1400, "備註": "高抗壓，含鑽孔"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "坡面排水廊道開挖與支撐", "單位": "m", "單價(元)": 45000, "備註": "大規模崩塌地排水主力"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "深層滲井鑽掘與過濾材料回填", "單位": "m", "單價(元)": 8500, "備註": "引導淺層水至深層地層"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "坡面U型截水溝 (W60cm x H60cm)", "單位": "m", "單價(元)": 3200, "備註": "現場澆置"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "RC 陰井 / 集水井 (含鑄鐵格柵)", "單位": "座", "單價(元)": 8000, "備註": "統一常規尺寸單價"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "山區跌水工 (RC階梯式)", "單位": "座", "單價(元)": 18000, "備註": "依設計高差調整"},
    {"主工項": "常規集水管與截水溝", "細項名稱": "地下盲溝 (包含碎石級配及透水管)", "單位": "m", "單價(元)": 2200, "備註": "截斷地下水路"}
]

# ==========================================
# 資料庫版本驗證機制 (解決 Session 覆寫問題)
# ==========================================
def initialize_database():
    """驗證實體版本檔，若為新版則強制覆寫 DB_FILE，否則保留既有共享資料"""
    needs_update = True
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            if f.read().strip() == CURRENT_VERSION:
                needs_update = False
                
    if needs_update or not os.path.exists(DB_FILE):
        df = pd.DataFrame(DEFAULT_DB)
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        with open(VERSION_FILE, 'w') as f:
            f.write(CURRENT_VERSION)

# 執行初始化驗證
initialize_database()

# 讀取共用資料庫
def load_db():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['單價(元)'] = df['單價(元)'].astype(int)
        return df
    return pd.DataFrame(DEFAULT_DB)

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
    st.caption("依據公共工程預算編列慣例，直接工程費將依序乘上以下費率累計。")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        osh_pct = st.number_input("勞安衛生費 (%)", value=1.5, step=0.1)
        qc_pct = st.number_input("品質管理費 (%)", value=1.0, step=0.1)
    with col_m2:
        env_pct = st.number_input("環境保護費 (%)", value=0.5, step=0.1)
        ins_pct = st.number_input("營造保險費 (%)", value=0.5, step=0.1)
    with col_m3:
        management_pct = st.number_input("包商利潤與管理費 (%)", value=10.0, step=0.5)
    with col_m4:
        contingency_pct = st.number_input("工程預備費 (%)", value=5.0, step=0.5)
        tax_pct = st.number_input("營業稅率 (%)", value=5.0, step=0.5)

    st.markdown("---")
    
    st.subheader("📊 3. 估算結果分析與明細")
    if len(selected_details) > 0:
        df_selected = pd.DataFrame(selected_details)
        direct_cost = df_selected['複價'].sum()
        
        # 依據 PCCES 慣例逐步累計計算
        osh_cost = int(direct_cost * (osh_pct / 100))
        qc_cost = int(direct_cost * (qc_pct / 100))
        env_cost = int(direct_cost * (env_pct / 100))
        ins_cost = int(direct_cost * (ins_pct / 100))
        
        subtotal_1 = direct_cost + osh_cost + qc_cost + env_cost + ins_cost
        management_cost = int(subtotal_1 * (management_pct / 100))
        
        subtotal_2 = subtotal_1 + management_cost
        contingency_cost = int(subtotal_2 * (contingency_pct / 100))
        
        subtotal_3 = subtotal_2 + contingency_cost
        tax_cost = int(subtotal_3 * (tax_pct / 100))
        
        total_cost = subtotal_3 + tax_cost
        
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
                "費用項目": [
                    "一、直接工程費", 
                    f"二、勞安/品管/環保/保險小計", 
                    f"三、包商利潤與管理費 ({management_pct}%)", 
                    f"四、工程預備費 ({contingency_pct}%)", 
                    f"五、營業稅 ({tax_pct}%)", 
                    "總計"
                ],
                "金額 (NT$)": [
                    direct_cost, 
                    (osh_cost + qc_cost + env_cost + ins_cost), 
                    management_cost, 
                    contingency_cost, 
                    tax_cost, 
                    total_cost
                ]
            })
            st.dataframe(summary_table.style.format({"金額 (NT$)": "{:,.0f}"}), use_container_width=True, hide_index=True)
            
        with res_col2:
            st.write("##### 📈 經費佔比視覺化")
            chart_data = pd.DataFrame({
                "費用類別": ["直接工程", "安全品管等附屬", "管理及利潤", "預備費", "營業稅"],
                "金額": [direct_cost, (osh_cost + qc_cost + env_cost + ins_cost), management_cost, contingency_cost, tax_cost]
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
                    "安全品管等附屬": (osh_cost + qc_cost + env_cost + ins_cost),
                    "管理費": management_cost,
                    "預備費": contingency_cost,
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
                
                # 處理新舊版本的相容性
                aux_cost = record.get('安全品管等附屬', record.get('雜項費', 0))
                mgt_cost = record.get('管理費', 0)
                contingency_cost = record.get('預備費', 0)
                tax_cost = record.get('營業稅', 0)
                
                summary_cols[1].metric("安全/品管/保險", f"NT$ {aux_cost:,}")
                summary_cols[2].metric("管理費", f"NT$ {mgt_cost:,}")
                summary_cols[3].metric("營業稅", f"NT$ {tax_cost:,}")
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
