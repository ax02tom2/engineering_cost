import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="大地工程經費初估與單價資料庫",
    page_icon="⛰️",
    layout="wide"
)

# ==========================================
# 初始化大地工程預設資料庫（主工項 -> 細項 階層式架構）
# ==========================================
if 'cost_db' not in st.session_state:
    st.session_state['cost_db'] = pd.DataFrame([
        # --- 大口徑集水井 (內徑 4.5m) ---
        {"主工項": "大口徑集水井 (內徑 4.5m)", "細項名稱": "集水井土方機具與人工開挖", "單位": "m³", "單價(元)": 1200, "備註": "含局限空間抽水及吊搬運"},
        {"主工項": "大口徑集水井 (內徑 4.5m)", "細項名稱": "擋土設施 (鋼襯鐵/RC環片組立)", "單位": "m", "單價(元)": 55000, "備註": "按井深計價，含組立工資"},
        {"主工項": "大口徑集水井 (內徑 4.5m)", "細項名稱": "井內不鏽鋼爬梯 (SUS304)", "單位": "m", "單價(元)": 3500, "備註": "附防墜設施"},
        {"主工項": "大口徑集水井 (內徑 4.5m)", "細項名稱": "輻射狀集排水管及鑽孔 (Ø50mm)", "單位": "m", "單價(元)": 1100, "備註": "含鑽孔及透水管安裝"},
        {"主工項": "大口徑集水井 (內徑 4.5m)", "細項名稱": "底部封底混凝土澆置", "單位": "m³", "單價(元)": 3500, "備註": "3000psi 混凝土"},
        {"主工項": "大口徑集水井 (內徑 4.5m)", "細項名稱": "開挖土方合法外運", "單位": "m³", "單價(元)": 850, "備註": "B1/B2 類土方含運棄"},
        
        # --- 預力地錨工程 (永久性) ---
        {"主工項": "預力地錨工程 (永久性)", "細項名稱": "地錨鑽孔 (土壤/卵礫石層)", "單位": "m", "單價(元)": 1400, "備註": "套管鑽掘"},
        {"主工項": "預力地錨工程 (永久性)", "細項名稱": "鋼絞線及防蝕套管組裝吊放", "單位": "m", "單價(元)": 850, "備註": "3~5股鋼絞線"},
        {"主工項": "預力地錨工程 (永久性)", "細項名稱": "地錨二次高壓灌漿", "單位": "m", "單價(元)": 450, "備註": "純水泥漿"},
        {"主工項": "預力地錨工程 (永久性)", "細項名稱": "地錨張拉與錨具鎖定", "單位": "孔", "單價(元)": 3500, "備註": "含施預力及檢測"},
        {"主工項": "預力地錨工程 (永久性)", "細項名稱": "地錨封頭混凝土保護", "單位": "孔", "單價(元)": 1500, "備註": "防鏽及保護蓋"},
        
        # --- 抗滑樁工程 (全套管直徑 1.0m) ---
        {"主工項": "抗滑樁工程 (全套管 Ø1.0m)", "細項名稱": "全套管機具鑽掘", "單位": "m", "單價(元)": 6500, "備註": "含搖管機操作"},
        {"主工項": "抗滑樁工程 (全套管 Ø1.0m)", "細項名稱": "鋼筋籠組立與吊放", "單位": "噸", "單價(元)": 38000, "備註": "含主筋及箍筋"},
        {"主工項": "抗滑樁工程 (全套管 Ø1.0m)", "細項名稱": "特密管混凝土澆置", "單位": "m³", "單價(元)": 3200, "備註": "水中混凝土"},
        {"主工項": "抗滑樁工程 (全套管 Ø1.0m)", "細項名稱": "劣質泥水廢土外運", "單位": "m³", "單價(元)": 1200, "備註": "含水廢土處置費"},
        
        # --- 坡面水土保持工程 ---
        {"主工項": "坡面水土保持工程", "細項名稱": "坡面整理與清孔", "單位": "m²", "單價(元)": 150, "備註": "挖土機或人工修坡"},
        {"主工項": "坡面水土保持工程", "細項名稱": "坡面橫向集水管 (Ø50mm)", "單位": "m", "單價(元)": 800, "備註": "含鑽孔與透水管材"},
        {"主工項": "坡面水土保持工程", "細項名稱": "坡面截水溝 (現場澆置U型溝)", "單位": "m", "單價(元)": 2800, "備註": "含模板鋼筋混凝土"},
        {"主工項": "坡面水土保持工程", "細項名稱": "坡面掛網噴植草籽", "單位": "m²", "單價(元)": 450, "備註": "含客土及菱形網"}
    ])

if 'history' not in st.session_state:
    st.session_state['history'] = []

st.title("⛰️ 大地工程經費初估資料庫與計算系統")
st.markdown("採用**「主工項 ➔ 細項」**編列邏輯。請先選擇大項目，系統將自動展開該項目包含的詳細工序，填寫數量即可進行精確試算。")

# 側邊欄導覽
tab = st.sidebar.radio("功能選單", ["📊 階層式經費初估", "📚 單價資料庫管理", "📁 歷史估算紀錄與匯出"])

# ==========================================
# TAB 1: 工程經費初估計算 (階層式)
# ==========================================
if tab == "📊 階層式經費初估":
    st.header("💡 大地工程階層式經費初估")
    
    db = st.session_state['cost_db']
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("1. 專案名稱與主工程選擇")
        project_name = st.text_input("專案名稱", "某坡地穩定與大口徑集水井工程")
        
        # 取得所有不重複的主工項
        all_major_items = db['主工項'].unique().tolist()
        
        selected_majors = st.multiselect(
            "📌 請選擇本次需要的主工程項目 (可複選)：", 
            options=all_major_items,
            placeholder="點擊展開選擇 (例如：大口徑集水井、預力地錨)..."
        )
        
        selected_details = []
        
        if selected_majors:
            st.markdown("---")
            st.markdown("#### 📝 細項數量設定")
            st.caption("系統已展開您選擇的主工程。請於需要的細項填寫數量 (若該細項不需要，維持數量 0 即可)。")
            
            for major in selected_majors:
                with st.expander(f"📂 {major}", expanded=True):
                    # 抓取該主工項底下的所有細項
                    sub_items = db[db['主工項'] == major]
                    
                    for idx, row in sub_items.iterrows():
                        sub_name = row['細項名稱']
                        unit = row['單位']
                        default_price = float(row['單價(元)'])
                        
                        st.markdown(f"**{sub_name}** *(備註: {row['備註']})*")
                        c_qty, c_price, c_total = st.columns([1, 1, 1])
                        
                        with c_qty:
                            # 預設數量為 0，有輸入數字才會計算
                            qty = st.number_input(f"數量 ({unit})", value=0.0, step=10.0, key=f"qty_{major}_{sub_name}")
                        with c_price:
                            prc = st.number_input(f"單價 (元/{unit})", value=default_price, step=100.0, key=f"prc_{major}_{sub_name}")
                        with c_total:
                            subtotal = qty * prc
                            st.metric("複價小計", f"NT$ {subtotal:,.0f}")
                        
                        st.divider()
                        
                        # 只要數量大於0，就加入計算清單
                        if qty > 0:
                            selected_details.append({
                                "主工項": major,
                                "細項名稱": sub_name,
                                "單位": unit,
                                "數量": qty,
                                "單價": prc,
                                "複價": subtotal
                            })

        st.subheader("2. 間接費用與稅金比例設定")
        col_a, col_b = st.columns(2)
        with col_a:
            misc_pct = st.number_input("雜項工程費率 (%)", value=15.0, step=0.5)
            management_pct = st.number_input("工程管理及利潤率 (%)", value=10.0, step=0.5)
        with col_b:
            tax_pct = st.number_input("營業稅率 (%)", value=5.0, step=0.5)

    with col2:
        st.subheader("3. 經費總表與結構分析")
        
        if len(selected_details) > 0:
            df_selected = pd.DataFrame(selected_details)
            direct_cost = df_selected['複價'].sum()
            
            # 間接費用計算
            misc_cost = direct_cost * (misc_pct / 100)
            subtotal_1 = direct_cost + misc_cost
            
            management_cost = subtotal_1 * (management_pct / 100)
            subtotal_2 = subtotal_1 + management_cost
            
            tax_cost = subtotal_2 * (tax_pct / 100)
            total_cost = subtotal_2 + tax_cost
            
            st.metric(label="💰 總經費初估 (含稅)", value=f"NT$ {total_cost:,.0f} 元")
            
            st.write("##### 一、直接工程費細項明細")
            # 顯示給使用者的明細表，依照主工項分群
            st.dataframe(
                df_selected[['主工項', '細項名稱', '數量', '單位', '單價', '複價']].style.format({"數量": "{:,.1f}", "單價": "{:,.0f}", "複價": "{:,.0f}"}), 
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
                tooltip=['費用類別', alt.Tooltip('金額:Q', format=',.0f')]
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
            st.info("👈 請於左側選擇主工程，並在展開的細項中「輸入大於0的數量」以進行計算。")

# ==========================================
# TAB 2: 單價資料庫管理 (主/細項 雙層架構)
# ==========================================
elif tab == "📚 單價資料庫管理":
    st.header("📚 階層式單價資料庫管理")
    st.markdown("所有資料皆依據 **主工項 ➔ 細項名稱** 之架構編列。您可透過下方表單新增特定主工項底下的細項。")
    
    db = st.session_state['cost_db']
    
    search_query = st.text_input("🔍 搜尋主工項或細項名稱", "")
    if search_query:
        mask = db['主工項'].str.contains(search_query, case=False) | db['細項名稱'].str.contains(search_query, case=False)
        display_db = db[mask]
    else:
        display_db = db
        
    st.dataframe(display_db, use_container_width=True, hide_index=True)
    
    st.subheader("➕ 人工新增細項資料")
    with st.form("add_geotech_form"):
        col1, col2 = st.columns(2)
        with col1:
            # 可以選擇現有主工項，或輸入新的主工項
            existing_majors = db['主工項'].unique().tolist()
            new_major = st.selectbox("歸屬主工項 (選擇現有，或選'新增自訂主工項')", existing_majors + ["-- 新增自訂主工項 --"])
            
            if new_major == "-- 新增自訂主工項 --":
                new_major = st.text_input("請輸入新的主工項名稱", "")
                
            new_sub = st.text_input("細項名稱 (例如：井內照明設備安裝)")
            new_unit = st.text_input("單位 (例如：m, 支, 式, m³)")
            
        with col2:
            new_price = st.number_input("單價 (元)", min_value=0.0, value=1000.0, step=100.0)
            new_note = st.text_input("備註說明")
            
        submitted = st.form_submit_button("確認新增至資料庫")
        if submitted:
            if new_major and new_sub:
                new_row = pd.DataFrame([{
                    "主工項": new_major,
                    "細項名稱": new_sub,
                    "單位": new_unit,
                    "單價(元)": new_price,
                    "備註": new_note
                }])
                st.session_state['cost_db'] = pd.concat([db, new_row], ignore_index=True)
                st.success(f"成功新增細項：【{new_major}】 ➔ {new_sub}！")
                st.rerun()
            else:
                st.error("主工項與細項名稱皆不可空白！")

# ==========================================
# TAB 3: 歷史估算紀錄與匯出
# ==========================================
elif tab == "📁 歷史估算紀錄與匯出":
    st.header("📁 歷史估算紀錄與資料匯出")
    
    history_df = pd.DataFrame(st.session_state['history'])
    
    if len(history_df) > 0:
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        
        csv = history_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載歷史估算總表 (CSV)",
            data=csv,
            file_name="geotechnical_cost_summary.csv",
            mime="text/csv"
        )
        
        if st.button("🗑️ 清空歷史紀錄"):
            st.session_state['history'] = []
            st.rerun()
    else:
        st.info("目前尚無歷史估算紀錄。")

# ==========================================
# 網頁下方資料來源備註 (Footer)
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 13px;'>
        📌 <b>資料來源與免責聲明備註：</b><br>
        1. 本系統工項拆分邏輯與預設參考單價，係參考<b>行政院公共工程委員會 (PCCES) 價格資料庫編碼規則</b>及近期國內大地工程招標之公開參考行情編製。<br>
        2. 以「大口徑集水井」為例，已細分為開挖、擋土支撐、爬梯、集排水管等實務計價細項，單價會因現地地質條件（如卵礫石層、岩盤）、施工動線與物價波動而有差異。<br>
        3. 本系統提供之數據與試算結果僅供<b>專案初期經費編列、可行性評估參考</b>，不具備法律或合約約束力。正式經費應依詳細設計圖說及預算書為準。
    </div>
    """,
    unsafe_allow_html=True
)
