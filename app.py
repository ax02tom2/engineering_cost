import streamlit as st
import pandas as pd
import altair as alt

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

# 自訂 CSS
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

st.title("⛰️ 大地工程經費初估與資料庫")

with st.sidebar:
    st.header("功能導覽")
    tab = st.radio("", ["📊 專案經費初估", "📚 單價資料庫管理", "📁 歷史估算紀錄"])
    st.markdown("---")
    st.info("💡 **單價更新說明**\n\nPCCES 單價無法自動即時抓取，請利用「資料庫管理」的 CSV 匯入功能進行整批單價更新。")

# ==========================================
# TAB 1: 專案經費初估
# ==========================================
if tab == "📊 專案經費初估":
    
    st.subheader("1. 專案名稱與工程項目設定")
    project_name = st.text_input("專案名稱", "某坡地穩定與水保改善工程")
    
    db = st.session_state['cost_db']
    all_major_items = db['主工項'].unique().tolist()
    
    selected_majors = st.multiselect(
        "請選擇本次工程涵蓋的主項目 (可複選)：", 
        options=all_major_items,
        placeholder="點擊此處展開清單..."
    )
    
    selected_details = []
    
    if selected_majors:
        st.markdown("#### 📝 細項數量與單價設定")
        st.caption("請填寫數量。參考價與小計皆已統一對齊，若需微調單價請修改「自訂單價」。")
        
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
            st.dataframe(
                df_selected.style.format({
                    "數量": "{:,.1f}", 
                    "單價(元)": "{:,.0f}", 
                    "複價": "{:,.0f}"
                }), 
                use_container_width=True, 
                hide_index=True
            )
            
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
            if st.button("💾 儲存專案至歷史紀錄", type="primary", use_container_width=True):
                # ★ 升級：連同明細資料表 (df_selected) 一起存入歷史紀錄
                record = {
                    "專案名稱": project_name,
                    "直接工程費": direct_cost,
                    "雜項費": misc_cost,
                    "管理費": management_cost,
                    "營業稅": tax_cost,
                    "總經費": total_cost,
                    "時間": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                    "細項明細": df_selected.to_dict('records') # 將 DataFrame 轉為字典清單儲存
                }
                st.session_state['history'].append(record)
                st.success("儲存成功！請至「歷史估算紀錄」查看包含所有細項的完整報表。")
    else:
        st.info("👈 請先於上方區塊勾選工項並填寫大於 0 的數量，系統將於此處生成完整明細與分析圖表。")

# ==========================================
# TAB 2: 單價資料庫管理
# ==========================================
elif tab == "📚 單價資料庫管理":
    st.header("📚 單價資料庫與 PCCES 批次更新")
    
    db = st.session_state['cost_db']
    
    c_dl, c_up = st.columns([1, 1], gap="large")
    with c_dl:
        st.markdown("#### ⬇️ 步驟 1: 下載目前資料庫")
        st.caption("匯出 CSV，交由估算人員比對最新 PCCES 行情並修改單價。")
        csv_db = db.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載 CSV 模板", data=csv_db, file_name="geotech_database.csv", mime="text/csv")
    
    with c_up:
        st.markdown("#### ⬆️ 步驟 2: 匯入最新單價表")
        st.caption("上傳修改完成的 CSV，系統將自動覆蓋更新單價。")
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
# TAB 3: 歷史估算紀錄 (全面升級版)
# ==========================================
elif tab == "📁 歷史估算紀錄":
    st.header("📁 歷史估算紀錄與匯出")
    st.markdown("點擊專案卡片即可檢視該專案的**所有工程細項、數量與單價明細**。")
    
    if len(st.session_state['history']) > 0:
        
        # 建立匯出所有明細的超級大表
        all_export_data = []
        
        for idx, record in enumerate(st.session_state['history']):
            # ★ 升級：使用 expander 將每個專案做成卡片，點開可看明細
            with st.expander(f"📌 [{record['時間']}] {record['專案名稱']} ─ 總經費: NT$ {record['總經費']:,}"):
                
                # 顯示該專案的總表摘要
                st.markdown("##### 📊 專案費用總結")
                summary_cols = st.columns(5)
                summary_cols[0].metric("直接工程費", f"NT$ {record['直接工程費']:,}")
                summary_cols[1].metric("雜項費", f"NT$ {record['雜項費']:,}")
                summary_cols[2].metric("管理費", f"NT$ {record['管理費']:,}")
                summary_cols[3].metric("營業稅", f"NT$ {record['營業稅']:,}")
                summary_cols[4].metric("總經費", f"NT$ {record['總經費']:,}")
                
                # 顯示該專案儲存的細項明細
                st.markdown("##### 📝 專案工程細項明細")
                if "細項明細" in record and record["細項明細"]:
                    detail_df = pd.DataFrame(record["細項明細"])
                    st.dataframe(
                        detail_df.style.format({
                            "數量": "{:,.1f}", 
                            "單價(元)": "{:,.0f}", 
                            "複價": "{:,.0f}"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # 準備匯出資料（加上專案名稱作為識別）
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
            # 匯出只有總表的 CSV
            history_summary_df = pd.DataFrame(st.session_state['history']).drop(columns=['細項明細'], errors='ignore')
            csv_summary = history_summary_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 下載歷史紀錄 (僅總表 CSV)", data=csv_summary, file_name="history_summary.csv", mime="text/csv", use_container_width=True)
            
        with col_btn2:
            # 匯出包含所有專案、所有細項的大表 CSV
            if all_export_data:
                export_df = pd.DataFrame(all_export_data)
                # 重新排列欄位，讓專案名稱與時間在最前面
                cols = ['專案名稱', '估算時間'] + [c for c in export_df.columns if c not in ['專案名稱', '估算時間']]
                export_df = export_df[cols]
                
                csv_details = export_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下載歷史紀錄 (含所有細項明細 CSV)", data=csv_details, file_name="history_full_details.csv", mime="text/csv", use_container_width=True)
        
        with col_btn3:
            if st.button("🗑️️ 清空所有歷史紀錄", use_container_width=True):
                st.session_state['history'] = []
                st.rerun()
                
    else:
        st.info("目前尚無歷史估算紀錄。請先於「專案經費初估」頁面儲存專案。")
