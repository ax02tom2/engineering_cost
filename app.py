import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="大地工程經費初估與單價資料庫",
    page_icon="⛰️",
    layout="wide"
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
        {"主工項": "防落石與坡面防護工程", "細項名稱": "高強度防落石網 (被動式, 攔截能量500kJ)", "單位": "m", "單價(元)": 25000, "備註": "含鋼柱、基座、緩衝繩"},
        {"主工項": "防落石與坡面防護工程", "細項名稱": "坡面覆蓋防落石網 (主動式, 菱形網+岩栓)", "單位": "m²", "單價(元)": 1200, "備註": "含短岩栓與鍍鋅網"},
        {"主工項": "防落石與坡面防護工程", "細項名稱": "噴凝土護坡 (厚度 10cm)", "單位": "m²", "單價(元)": 850, "備註": "含點焊鋼絲網及配比噴槍澆置"},
        
        # --- 【集水井工程 (不同尺寸)】 ---
        {"主工項": "集水井工程 (含開挖與RC構造)", "細項名稱": "中型集水井 (內徑 1.0m x 1.0m)", "單位": "座", "單價(元)": 18000, "備註": "含格柵蓋板及底部跌水"},
        {"主工項": "大口徑集水井 (深井工法)", "細項名稱": "內徑 3.5m 鋼襯鐵/RC大口徑集水井", "單位": "m", "單價(元)": 85000, "備註": "依深度計價，含局限開挖、環片"},
        {"主工項": "大口徑集水井 (深井工法)", "細項名稱": "內徑 4.5m 鋼襯鐵/RC大口徑集水井", "單位": "m", "單價(元)": 115000, "備註": "依深度計價，含局限開挖、環片"},
        {"主工項": "大口徑集水井 (深井工法)", "細項名稱": "井內不鏽鋼爬梯 (含防墜設施)", "單位": "m", "單價(元)": 3500, "備註": "SUS304"},
        {"主工項": "大口徑集水井 (深井工法)", "細項名稱": "底部封底混凝土", "單位": "m³", "單價(元)": 3500, "備註": "3000psi"},
        
        # --- 【集水管與截水溝工程】 ---
        {"主工項": "集水管與截排水工程", "細項名稱": "橫向/輻射集水管 (PVC透水管 內徑 Ø50mm)", "單位": "m", "單價(元)": 850, "備註": "含鑽孔及管材"},
        {"主工項": "集水管與截排水工程", "細項名稱": "橫向/輻射集水管 (HDPE波紋管 內徑 Ø150mm)", "單位": "m", "單價(元)": 1800, "備註": "含鑽孔及管材"},
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

st.title("⛰️ 大地工程經費初估資料庫與計算系統")

# 側邊欄導覽
tab = st.sidebar.radio("功能選單", ["📊 專案經費初估 (互動式表格)", "📚 單價資料庫管理 (更新/匯入)", "📁 歷史估算紀錄"])

# ==========================================
# TAB 1: 專案經費初估 (互動式表格 - 美觀且不擁擠)
# ==========================================
if tab == "📊 專案經費初估 (互動式表格)":
    st.header("💡 專案經費智慧初估")
    st.markdown("勾選主工程後，請直接於下方 **互動式表格** 雙擊修改 **「✏️自訂單價」** 與 **「✏️數量」**。表格支援千位數逗號顯示，排版更直觀。")
    
    db = st.session_state['cost_db']
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("1. 專案名稱與主工程選擇")
        project_name = st.text_input("專案名稱", "某坡地穩定與水保改善工程")
        
        all_major_items = db['主工項'].unique().tolist()
        selected_majors = st.multiselect(
            "📌 請選擇本次需要的主工程項目 (可複選)：", 
            options=all_major_items,
            placeholder="點擊展開選擇 (例如：擋土牆、防落石)..."
        )
        
        valid_items_df = pd.DataFrame()
        
        if selected_majors:
            st.markdown("#### 📝 細項數量與單價設定 (互動表格)")
            
            # 篩選出選中的主工程細項，建立編輯用 DataFrame
            editor_df = db[db['主工項'].isin(selected_majors)].copy()
            editor_df['✏️自訂單價(元)'] = editor_df['單價(元)'] # 預設等於參考單價
            editor_df['✏️數量'] = 0.0 # 預設數量為0
            
            # 重新排列顯示順序
            editor_df = editor_df[['主工項', '細項名稱', '單位', '單價(元)', '✏️自訂單價(元)', '✏️數量', '備註']]
            
            # 呼叫 Streamlit 互動式表格 (Data Editor)
            edited_df = st.data_editor(
                editor_df,
                column_config={
                    "主工項": st.column_config.TextColumn("主工程", disabled=True),
                    "細項名稱": st.column_config.TextColumn("細項與規格", disabled=True),
                    "單位": st.column_config.TextColumn("單位", disabled=True),
                    "單價(元)": st.column_config.NumberColumn("參考單價", format="%d", disabled=True),
                    "✏️自訂單價(元)": st.column_config.NumberColumn("✏️自訂單價", format="%d", min_value=0),
                    "✏️數量": st.column_config.NumberColumn("✏️數量", format="%.1f", min_value=0.0, step=1.0),
                    "備註": st.column_config.TextColumn("備註", disabled=True),
                },
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )
            
            # 只濾出有輸入數量的項目進行總價計算
            valid_items_df = edited_df[edited_df['✏️數量'] > 0].copy()
            if not valid_items_df.empty:
                valid_items_df['複價'] = (valid_items_df['✏️數量'] * valid_items_df['✏️自訂單價(元)']).astype(int)

        st.subheader("2. 間接費用與稅金比例設定")
        col_a, col_b = st.columns(2)
        with col_a:
            misc_pct = st.number_input("雜項工程費率 (%)", value=15.0, step=0.5)
            management_pct = st.number_input("工程管理及利潤率 (%)", value=10.0, step=0.5)
        with col_b:
            tax_pct = st.number_input("營業稅率 (%)", value=5.0, step=0.5)

    with col2:
        st.subheader("3. 經費總表與結構分析")
        
        if not valid_items_df.empty:
            direct_cost = valid_items_df['複價'].sum()
            
            misc_cost = int(direct_cost * (misc_pct / 100))
            subtotal_1 = direct_cost + misc_cost
            
            management_cost = int(subtotal_1 * (management_pct / 100))
            subtotal_2 = subtotal_1 + management_cost
            
            tax_cost = int(subtotal_2 * (tax_pct / 100))
            total_cost = subtotal_2 + tax_cost
            
            st.metric(label="💰 總經費初估 (含稅)", value=f"NT$ {total_cost:,} 元")
            
            st.write("##### 一、直接工程費明細清單")
            display_valid = valid_items_df[['主工項', '細項名稱', '✏️數量', '單位', '✏️自訂單價(元)', '複價']].rename(columns={'✏️數量': '數量', '✏️自訂單價(元)': '單價'})
            st.dataframe(
                display_valid.style.format({
                    "數量": "{:,.1f}", 
                    "單價": "{:,.0f}", 
                    "複價": "{:,.0f}"
                }), 
                use_container_width=True, 
                hide_index=True
            )
            
            st.write("##### 二、總表結構摘要")
            summary_table = pd.DataFrame({
                "項目": ["一、直接工程費", f"二、雜項工程 ({misc_pct}%)", f"三、工程管理及利潤 ({management_pct}%)", f"四、營業稅 ({tax_pct}%)", "總計"],
                "金額 (元)": [direct_cost, misc_cost, management_cost, tax_cost, total_cost]
            })
            st.dataframe(summary_table.style.format({"金額 (元)": "{:,.0f}"}), use_container_width=True, hide_index=True)
            
            # 圖表分析
            chart_data = pd.DataFrame({
                "費用類別": ["直接工程費", "雜項工程", "管理及利潤", "營業稅"],
                "金額": [direct_cost, misc_cost, management_cost, tax_cost]
            })
            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('金額:Q', title='金額 (NT$)'),
                y=alt.Y('費用類別:N', sort='-x', title='費用類別'),
                color=alt.Color('費用類別:N', legend=None),
                tooltip=['費用類別', alt.Tooltip('金額:Q', format=',d')]
            ).properties(height=250, title="經費組成結構圖")
            st.altair_chart(chart, use_container_width=True)
            
            if st.button("💾 儲存此筆專案估算至歷史紀錄", type="primary", use_container_width=True):
                record = {
                    "專案名稱": project_name,
                    "直接工程費": direct_cost,
                    "雜項工程費": misc_cost,
                    "管理及利潤": management_cost,
                    "營業稅": tax_cost,
                    "總經費(含稅)": total_cost,
                    "建立時間": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state['history'].append(record)
                st.success("已成功儲存至歷史紀錄！")
        else:
            st.info("👈 請於左側選擇主工程，並在下方表格輸入大於 0 的「數量」以進行試算。")

# ==========================================
# TAB 2: 單價資料庫管理 (新增 CSV 匯入更新功能)
# ==========================================
elif tab == "📚 單價資料庫管理 (更新/匯入)":
    st.header("📚 單價資料庫與 PCCES 批次更新")
    
    st.info("""
    💡 **關於 PCCES 單價自動同步：**
    行政院公共工程委員會 (PCCES) 的單價會依地區、時間及專案規模浮動，且官方目前**未提供即時公開 API** 供外部自動串接。
    👉 **實務作法：** 估算人員可定期將最新的 PCCES 參考價格整理為 Excel/CSV 檔案，利用下方的 **「批次匯入」** 功能，一鍵更新系統資料庫。
    """)
    
    db = st.session_state['cost_db']
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("⬇️ 匯出目前資料庫模板")
        csv_db = db.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="📥 下載資料庫 CSV (可用於更新單價)", data=csv_db, file_name="geotech_database_template.csv", mime="text/csv")
    
    with col_b:
        st.subheader("⬆️ 上傳更新資料庫 (CSV)")
        uploaded_file = st.file_uploader("上傳已更新單價的 CSV 檔案", type=["csv"])
        if uploaded_file is not None:
            try:
                new_db = pd.read_csv(uploaded_file)
                if set(['主工項', '細項名稱', '單位', '單價(元)']).issubset(new_db.columns):
                    st.session_state['cost_db'] = new_db
                    st.success("✅ 資料庫已成功覆蓋更新！")
                    st.rerun()
                else:
                    st.error("❌ CSV 欄位格式錯誤，請確認包含：主工項, 細項名稱, 單位, 單價(元)")
            except Exception as e:
                st.error(f"檔案讀取失敗: {e}")

    st.markdown("---")
    st.subheader("🔍 目前資料庫檢視與手動新增")
    
    search_query = st.text_input("🔍 搜尋工項名稱", "")
    if search_query:
        mask = db['主工項'].str.contains(search_query, case=False) | db['細項名稱'].str.contains(search_query, case=False)
        display_db = db[mask]
    else:
        display_db = db
        
    st.dataframe(display_db.style.format({"單價(元)": "{:,.0f}"}), use_container_width=True, hide_index=True)
    
    with st.expander("➕ 人工單筆新增細項/新尺寸規格"):
        with st.form("add_geotech_form"):
            c1, c2 = st.columns(2)
            with c1:
                existing_majors = db['主工項'].unique().tolist()
                new_major = st.selectbox("歸屬主工項", existing_majors + ["-- 新增自訂主工項 --"])
                if new_major == "-- 新增自訂主工項 --":
                    new_major = st.text_input("請輸入新的主工項名稱", "")
                new_sub = st.text_input("細項名稱與尺寸 (例如：內徑 8.0m 集水井)")
                new_unit = st.text_input("單位 (例如：m, 座, m³)")
            with c2:
                new_price = st.text_input("單價 (元)", value="1000")
                new_note = st.text_input("備註說明")
                
            if st.form_submit_button("確認新增至資料庫"):
                try:
                    parsed_price = int(new_price.replace(',', ''))
                    if new_major and new_sub:
                        new_row = pd.DataFrame([{"主工項": new_major, "細項名稱": new_sub, "單位": new_unit, "單價(元)": parsed_price, "備註": new_note}])
                        st.session_state['cost_db'] = pd.concat([db, new_row], ignore_index=True)
                        st.success("成功新增規格！")
                        st.rerun()
                except ValueError:
                    st.error("單價請輸入有效數字！")

# ==========================================
# TAB 3: 歷史估算紀錄與匯出
# ==========================================
elif tab == "📁 歷史估算紀錄":
    st.header("📁 歷史估算紀錄與資料匯出")
    history_df = pd.DataFrame(st.session_state['history'])
    
    if len(history_df) > 0:
        format_dict = {col: "{:,.0f}" for col in history_df.columns if "費" in col or "稅" in col}
        st.dataframe(history_df.style.format(format_dict), use_container_width=True, hide_index=True)
        csv = history_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="📥 下載歷史估算總表 (CSV)", data=csv, file_name="geotechnical_cost_summary.csv", mime="text/csv")
        if st.button("🗑️ 清空歷史紀錄"):
            st.session_state['history'] = []
            st.rerun()
    else:
        st.info("目前尚無歷史估算紀錄。")
