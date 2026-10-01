import streamlit as st
import pandas as pd
import altair as alt

# 設定網頁為寬版，並自訂整體的主題顏色
st.set_page_config(
    page_title="大地工程經費初估與單價資料庫",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 初始化大地工程預設資料庫
# ==========================================
if 'cost_db' not in st.session_state:
    st.session_state['cost_db'] = pd.DataFrame([
        # --- 【擋土牆工程】 ---
        {"主工項": "擋土牆工程 (懸臂式 RC擋土牆)", "細項名稱": "H=2.0m 懸臂式RC擋土牆", "單位": "m", "單價(元)": 15000, "備註": "含開挖、模板、鋼筋、混凝土及回填"},
        {"主工項": "擋土牆工程 (懸臂式 RC擋土牆)", "細項名稱": "H=3.0m 懸臂式RC擋土牆", "單位": "m", "單價(元)": 28000, "備註": "含開挖、模板、鋼筋、混凝土及回填"},
        {"主工項": "擋土牆工程 (懸臂式 RC擋土牆)", "細項名稱": "H=4.0m 懸臂式RC擋土牆", "單位": "m", "單價(元)": 42000, "備註": "含開挖、模板、鋼筋、混凝土及回填"},
        {"主工項": "擋土牆工程 (重力式 混凝土擋土牆)", "細項名稱": "H=2.0m 重力式混凝土擋土牆", "單位": "m", "單價(元)": 12000, "備註": "含開挖、模板、無筋混凝土澆置"},
        {"主工項": "擋土牆工程 (重力式 混凝土擋土牆)", "細項名稱": "H=3.0m 重力式混凝土擋土牆", "單位": "m", "單價(元)": 22000, "備註": "含開挖、模板、無筋混凝土澆置"},
        {"主工項": "擋土牆工程 (加勁擋土牆)", "細項名稱": "加勁擋土牆 (含網及回填)", "單位": "m²", "單價(元)": 4500, "備註": "立面面積計價，含地工網、級配回填壓實"},
        
        # --- 【防落石與坡面防護工程】 ---
        {"主工項": "防落石與坡面防護工程", "細項名稱": "高強度防落石網 (被動式, 500kJ)", "單位": "m", "單價(元)": 25000, "備註": "含鋼柱、基座、緩衝繩"},
        {"主工項": "防落石與坡面防護工程", "細項名稱": "坡面覆蓋防落石網 (主動式, 菱形網+岩栓)", "單位": "m²", "單價(元)": 1200, "備註": "含短岩栓與鍍鋅網"},
        {"主工項": "防落石與坡面防護工程", "細項名稱": "噴凝土護坡 (厚度 10cm)", "單位": "m²", "單價(元)": 850, "備註": "含點焊鋼絲網及配比噴槍澆置"},
        
        # --- 【集水井工程 (不同尺寸)】 ---
        {"主工項": "集水井工程 (含開挖與RC構造)", "細項名稱": "中型集水井 (內徑 1.0m x 1.0m)", "單位": "座", "單價(元)": 18000, "備註": "含格柵蓋板及底部跌水"},
        {"主工項": "大口徑集水井 (深井工法)", "細項名稱": "內徑 3.5m 鋼襯鐵/RC大口徑集水井", "單位": "m", "單價(元)": 85000, "備註": "依深度計價，含局限開挖、環片"},
        {"主工項": "大口徑集水井 (深井工法)", "細項名稱": "內徑 4.5m 鋼襯鐵/RC大口徑集水井", "單位": "m", "單價(元)": 115000, "備註": "依深度計價，含局限開挖、環片"},
        {"主工項": "大口徑集水井 (深井工法)", "細項名稱": "井內不鏽鋼爬梯 (含防墜設施)", "單位": "m", "單價(元)": 3500, "備註": "SUS304"},
        {"主工項": "大口徑集水井 (深井工法)", "細項名稱": "底部封底混凝土", "單位": "m³", "單價(元)": 3500, "備註": "3000psi"},
        
        # --- 【集水管與截水溝工程】 ---
        {"主工項": "集水管與截排水工程", "細項名稱": "橫向/輻射集水管 (PVC 內徑 Ø50mm)", "單位": "m", "單價(元)": 850, "備註": "含鑽孔及管材"},
        {"主工項": "集水管與截排水工程", "細項名稱": "橫向/輻射集水管 (HDPE 內徑 Ø150mm)", "單位": "m", "單價(元)": 1800, "備註": "含鑽孔及管材"},
        {"主工項": "集水管與截排水工程", "細項名稱": "坡面U型截水溝 (W60cm x H60cm)", "單位": "m", "單價(元)": 2800, "備註": "現場澆置"},
        
        # --- 【抗滑樁與地錨工程】 ---
        {"主工項": "抗滑樁工程", "細項名稱": "抗滑樁 (全套管機鑽掘 內徑 Ø1.0m)", "單位": "m", "單價(元)": 6500, "備註": "僅鑽掘工資"},
        {"主工項": "抗滑樁工程", "細項名稱": "抗滑樁鋼筋籠組立", "單位": "噸", "單價(元)": 38000, "備註": "含材料與組立"},
        {"主工項": "預力地錨工程", "細項名稱": "預力地錨 (永久性, 30噸)", "單位": "m", "單價(元)": 1400, "備註": "含鑽孔、鋼絞線、灌漿"},
        {"主工項": "預力地錨工程", "細項名稱": "地錨張拉與鎖定 (含防鏽封頭)", "單位": "孔", "單價(元)": 5000, "備註": "單孔計價"}
    ])
    st.session_state['cost_db']['單價(元)'] = st.session_state['cost_db']['單價(元)'].astype(int)

if 'history' not in st.session_state:
    st.session_state['history'] = []

# 自訂 CSS，增加區塊留白，美化按鈕與字體大小，減少擁擠感
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stExpander { border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;}
        .metric-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #0056b3; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;}
        h1, h2, h3 { color: #2c3e50; }
        .price-text { font-size: 1.1rem; color: #4CAF50; font-weight: bold; }
        hr { margin: 1.5em 0; border: 0; height: 1px; background: #eee; }
    </style>
""", unsafe_allow_html=True)


st.title("⛰️ 大地工程經費初估與資料庫")

# 側邊欄導覽
with st.sidebar:
    st.header("功能導覽")
    tab = st.radio("", ["📊 專案經費初估", "📚 單價資料庫管理", "📁 歷史估算紀錄"])
    st.markdown("---")
    st.info("💡 **單價更新說明**\n\nPCCES 單價無法自動即時抓取，請利用「資料庫管理」的 CSV 匯入功能進行整批單價更新。")

# ==========================================
# TAB 1: 專案經費初估 (回歸區塊展開式，版面重構)
# ==========================================
if tab == "📊 專案經費初估":
    
    # 頂部：專案基本資料 (佔滿寬度)
    st.subheader("1. 專案設定")
    project_name = st.text_input("專案名稱", "某坡地穩定與水保改善工程", help="輸入專案名稱以便未來在歷史紀錄中查找")
    
    st.markdown("<br>", unsafe_allow_html=True) # 增加留白
    
    # 版面分割：左側 (佔 7 成) 負責挑選工項與設定；右側 (佔 3 成) 負責顯示結果
    left_col, right_col = st.columns([7, 3], gap="large")
    
    with left_col:
        st.subheader("2. 工程項目選擇與數量設定")
        db = st.session_state['cost_db']
        all_major_items = db['主工項'].unique().tolist()
        
        selected_majors = st.multiselect(
            "請選擇本次工程涵蓋的主項目 (可複選)：", 
            options=all_major_items,
            placeholder="點擊此處展開清單..."
        )
        
        selected_details = []
        
        if selected_majors:
            st.markdown("---")
            # 展開區塊設計 (前一版的美觀卡片感)
            for major in selected_majors:
                with st.expander(f"📂 {major}", expanded=True):
                    sub_items = db[db['主工項'] == major]
                    
                    for idx, row in sub_items.iterrows():
                        sub_name = row['細項名稱']
                        unit = row['單位']
                        default_price = int(row['單價(元)'])
                        
                        st.markdown(f"**{sub_name}** <span style='color:gray; font-size:12px;'>({row['備註']})</span>", unsafe_allow_html=True)
                        
                        # 4 格佈局：數量 | 系統單價 | 覆蓋單價 | 小計
                        c_qty, c_ref, c_custom, c_total = st.columns([1.5, 1.5, 1.5, 1.5])
                        
                        with c_qty:
                            qty = st.number_input(f"數量 ({unit})", value=0.0, step=10.0, key=f"qty_{major}_{idx}")
                        
                        with c_ref:
                            st.markdown(f"<div style='margin-top: 30px; font-size: 14px;'>參考價: <br><span class='price-text'>NT$ {default_price:,}</span></div>", unsafe_allow_html=True)
                            
                        with c_custom:
                            custom_val = st.text_input(f"修改單價(可選)", value=str(default_price), key=f"prc_{major}_{idx}")
                            try:
                                prc = int(custom_val.replace(',', ''))
                            except ValueError:
                                prc = default_price
                                
                        with c_total:
                            subtotal = int(qty * prc)
                            st.markdown(f"<div style='margin-top: 30px; font-size: 14px; text-align:right;'>小計: <br><b>NT$ {subtotal:,}</b></div>", unsafe_allow_html=True)
                            
                        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                        
                        if qty > 0:
                            selected_details.append({
                                "主工項": major,
                                "細項名稱": sub_name,
                                "單位": unit,
                                "數量": qty,
                                "單價": prc,
                                "複價": subtotal
                            })

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("3. 間接費用費率 (%)")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            misc_pct = st.number_input("雜項工程費率", value=15.0, step=0.5)
        with col_m2:
            management_pct = st.number_input("管理及利潤率", value=10.0, step=0.5)
        with col_m3:
            tax_pct = st.number_input("營業稅率", value=5.0, step=0.5)

    with right_col:
        # 右側永遠固定顯示計算結果
        st.subheader("📊 估算結果分析")
        
        if len(selected_details) > 0:
            df_selected = pd.DataFrame(selected_details)
            direct_cost = df_selected['複價'].sum()
            
            misc_cost = int(direct_cost * (misc_pct / 100))
            subtotal_1 = direct_cost + misc_cost
            management_cost = int(subtotal_1 * (management_pct / 100))
            subtotal_2 = subtotal_1 + management_cost
            tax_cost = int(subtotal_2 * (tax_pct / 100))
            total_cost = subtotal_2 + tax_cost
            
            # 使用醒目的設計卡片顯示總價
            st.markdown(f"""
            <div class="metric-card">
                <p style="margin:0; color:#555; font-size:14px;">總經費初估 (含稅)</p>
                <h2 style="margin:0; color:#0056b3; font-size:28px;">NT$ {total_cost:,}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # 結構摘要表
            summary_table = pd.DataFrame({
                "項目": ["直接工程", "雜項工程", "管理及利潤", "營業稅"],
                "金額": [direct_cost, misc_cost, management_cost, tax_cost]
            })
            st.dataframe(summary_table.style.format({"金額": "{:,.0f}"}), use_container_width=True, hide_index=True)
            
            # 圖表
            chart = alt.Chart(summary_table).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X('金額:Q', title='金額 (NT$)', axis=alt.Axis(format='d')),
                y=alt.Y('項目:N', sort='-x', title=''),
                color=alt.Color('項目:N', legend=None),
                tooltip=['項目', alt.Tooltip('金額:Q', format=',d')]
            ).properties(height=200).configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 儲存專案至歷史紀錄", type="primary", use_container_width=True):
                record = {
                    "專案名稱": project_name,
                    "直接工程費": direct_cost,
                    "雜項費": misc_cost,
                    "管理費": management_cost,
                    "營業稅": tax_cost,
                    "總經費": total_cost,
                    "時間": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state['history'].append(record)
                st.success("儲存成功！")
        else:
            st.info("👈 請於左側選擇工項並填寫數量。")

# ==========================================
# TAB 2: 單價資料庫管理 (PCCES 批次更新)
# ==========================================
elif tab == "📚 單價資料庫管理":
    st.header("📚 單價資料庫與 PCCES 批次更新")
    
    db = st.session_state['cost_db']
    
    c_dl, c_up = st.columns([1, 1], gap="large")
    with c_dl:
        st.markdown("#### ⬇️ 步驟 1: 下載目前資料庫")
        st.caption("將現有資料庫匯出為 CSV，交由估算人員比對最新 PCCES 行情並修改單價。")
        csv_db = db.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載 CSV 模板", data=csv_db, file_name="geotech_database.csv", mime="text/csv")
    
    with c_up:
        st.markdown("#### ⬆️ 步驟 2: 匯入最新單價表")
        st.caption("上傳修改完成的 CSV，系統將自動覆蓋並更新所有單價。")
        uploaded_file = st.file_uploader("上傳更新後的 CSV 檔案", type=["csv"], label_visibility="collapsed")
        if uploaded_file is not None:
            try:
                new_db = pd.read_csv(uploaded_file)
                if set(['主工項', '細項名稱', '單位', '單價(元)']).issubset(new_db.columns):
                    st.session_state['cost_db'] = new_db
                    st.success("✅ 資料庫更新成功！")
                    st.rerun()
                else:
                    st.error("欄位格式錯誤，請確認 CSV 包含：主工項, 細項名稱, 單位, 單價(元)")
            except Exception as e:
                st.error(f"檔案讀取失敗: {e}")

    st.markdown("---")
    st.markdown("#### 🔍 目前資料庫檢視與單筆新增")
    
    search_query = st.text_input("🔍 搜尋工項名稱", "", placeholder="例如：集水井")
    display_db = db[db['主工項'].str.contains(search_query, case=False) | db['細項名稱'].str.contains(search_query, case=False)] if search_query else db
    st.dataframe(display_db.style.format({"單價(元)": "{:,.0f}"}), use_container_width=True, hide_index=True)
    
    with st.expander("➕ 人工單筆新增細項規格"):
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
                        st.session_state['cost_db'] = pd.concat([db, new_row], ignore_index=True)
                        st.success("新增成功！")
                        st.rerun()
                except ValueError:
                    st.error("單價請輸入有效數字！")

# ==========================================
# TAB 3: 歷史估算紀錄
# ==========================================
elif tab == "📁 歷史估算紀錄":
    st.header("📁 歷史估算紀錄與匯出")
    history_df = pd.DataFrame(st.session_state['history'])
    
    if len(history_df) > 0:
        format_dict = {col: "{:,.0f}" for col in history_df.columns if "費" in col or "稅" in col}
        st.dataframe(history_df.style.format(format_dict), use_container_width=True, hide_index=True)
        csv = history_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載歷史報表 (CSV)", data=csv, file_name="geotech_history.csv", mime="text/csv")
        if st.button("🗑️ 清空紀錄"):
            st.session_state['history'] = []
            st.rerun()
    else:
        st.info("目前尚無歷史估算紀錄。")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 12px;'>本系統單價邏輯參考行政院公共工程委員會 (PCCES) 規則編製。正式經費應依設計圖說與預算書為準。</div>", unsafe_allow_html=True)
