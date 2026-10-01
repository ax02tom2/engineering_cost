import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="大地工程經費初估與單價資料庫",
    page_icon="⛰️",
    layout="wide"
)

# 初始化大地工程專屬資料庫（Session State）
if 'cost_db' not in st.session_state:
    st.session_state['cost_db'] = pd.DataFrame([
        {"項次": 1, "工程類別": "大地工程", "工項名稱": "預力地錨（雙J/面板式，L=20m）", "單位": "m", "單價(元)": 2000, "備註": "Tw=30ton@3m, L=20m"},
        {"項次": 2, "工程類別": "大地工程", "工項名稱": "坡面集水管 / 橫向集水管", "單位": "m", "單價(元)": 2000, "備註": "L=40m@3m，含鑽孔與管材"},
        {"項次": 3, "工程類別": "大地工程", "工項名稱": "大口徑集水井（直徑>1.5m）", "單位": "m", "單價(元)": 15000, "備註": "含環片支撐及開挖排水"},
        {"項次": 4, "工程類別": "大地工程", "工項名稱": "坡面截水溝 / 排水溝", "單位": "m", "單價(元)": 3000, "備註": "現場澆置或U型溝排水"},
        {"項次": 5, "工程類別": "大地工程", "工項名稱": "抗滑樁（鋼管樁/RC樁）", "單位": "支", "單價(元)": 120000, "備註": "含鑽孔、鋼筋籠及混凝土灌注"},
        {"項次": 6, "工程類別": "大地工程", "工項名稱": "施工開闢臨時便道（含開挖回填）", "單位": "式", "單價(元)": 500000, "備註": "山區便道整地及夯實"}
    ])

if 'history' not in st.session_state:
    st.session_state['history'] = []

st.title("⛰️ 大地工程經費初估資料庫與計算系統")
st.markdown("專為坡地穩定、地錨、集水井、抗滑樁等大地工程設計的經費智慧初估與單價管理系統。")

# 側邊欄導覽
tab = st.sidebar.radio("功能選單", ["📊 工程經費初估計算", "📚 大地單價資料庫管理", "📁 歷史估算紀錄與匯出"])

# ----------------------------------------------------
# TAB 1: 工程經費初估計算
# ----------------------------------------------------
if tab == "📊 工程經費初估計算":
    st.header("💡 大地工程經費智慧初估試算")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. 專案基本資料與工項配置")
        project_name = st.text_input("專案名稱", "鵞鵞嶺路穩定性強化處理工程")
        
        db = st.session_state['cost_db']
        
        # 允許使用者組合多個工項進行初估
        st.markdown("---")
        st.write("請勾選並設定本次工程需要的工項與數量：")
        
        selected_items_data = []
        
        for idx, row in db.iterrows():
            col_chk, col_qty, col_price = st.columns([3, 1, 1])
            with col_chk:
                is_checked = st.checkbox(f"{row['工項名稱']} ({row['單位']})", value=(idx < 3), key=f"chk_{idx}")
            if is_checked:
                with col_qty:
                    qty = st.number_input(f"數量 ({row['單位']})", value=100.0 if row['單位']=='m' else 1.0, step=10.0, key=f"qty_{idx}")
                with col_price:
                    prc = st.number_input(f"單價", value=float(row['單價(元)']), step=100.0, key=f"prc_{idx}")
                
                selected_items_data.append({
                    "工項名稱": row['工項名稱'],
                    "單位": row['單位'],
                    "數量": qty,
                    "單價": prc,
                    "複價": qty * prc,
                    "備註": row['備註']
                })
            else:
                # 佔位避免排版亂掉
                pass

        st.subheader("2. 間接費用與稅金比例設定")
        col_a, col_b = st.columns(2)
        with col_a:
            misc_pct = st.number_input("雜項工程費率 (%)", value=15.0, step=0.5, help="通常為直接工程費之一定比例")
            management_pct = st.number_input("工程管理及利潤率 (%)", value=10.0, step=0.5, help="通常為（直接工程費 + 雜項工程費）之一定比例")
        with col_b:
            tax_pct = st.number_input("營業稅率 (%)", value=5.0, step=0.5)

    with col2:
        st.subheader("3. 經費總表與結構分析")
        
        if len(selected_items_data) > 0:
            df_selected = pd.DataFrame(selected_items_data)
            direct_cost = df_selected['複價'].sum()
            
            # 依照您圖片中的邏輯計算間接費用
            misc_cost = direct_cost * (misc_pct / 100)
            subtotal_1 = direct_cost + misc_cost
            
            management_cost = subtotal_1 * (management_pct / 100)
            subtotal_2 = subtotal_1 + management_cost
            
            tax_cost = subtotal_2 * (tax_pct / 100)
            total_cost = subtotal_2 + tax_cost
            
            st.metric(label="💰 總經費初估 (含稅)", value=f"NT$ {total_cost:,.0f} 元")
            
            # 顯示直接工程費明細
            st.write("##### 一、直接工程費明細")
            st.dataframe(df_selected[['工項名稱', '單位', '數量', '單價', '複價', '備註']].style.format({"數量": "{:,.1f}", "單價": "{:,.0f}", "複價": "{:,.0f}"}), use_container_width=True)
            st.write(f"**直接工程費小計：NT$ {direct_cost:,.0f} 元**")
            
            st.write("##### 二、總表結構摘要")
            summary_table = pd.DataFrame({
                "項目": ["一、直接工程費", f"二、雜項工程 ({misc_pct}%)", f"三、工程管理及利潤 ({management_pct}%)", f"四、營業稅 ({tax_pct}%)", "總計"],
                "金額 (元)": [direct_cost, misc_cost, management_cost, tax_cost, total_cost]
            })
            st.dataframe(summary_table.style.format({"金額 (元)": "{:,.0f}"}), use_container_width=True)
            
            # 圖表分析
            chart_data = pd.DataFrame({
                "費用類別": ["直接工程費", "雜項工程", "管理及利潤", "營業稅"],
                "金額": [direct_cost, misc_cost, management_cost, tax_cost]
            })
            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('金額:Q', title='金額 (NT$)'),
                y=alt.Y('費用類別:N', sort='-x', title='費用類別'),
                color='費用類別:N',
                tooltip=['費用類別', alt.Tooltip('金額:Q', format=',.0f')]
            ).properties(height=220, title="經費組成結構圖")
            st.altair_chart(chart, use_container_width=True)
            
            if st.button("💾 儲存此筆專案估算至歷史紀錄", type="primary"):
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
            st.warning("請至少在左側勾選一項工程項目進行試算。")

# ----------------------------------------------------
# TAB 2: 單價資料庫管理
# ----------------------------------------------------
elif tab == "📚 大地單價資料庫管理":
    st.header("📚 大地工程參考單價資料庫")
    st.markdown("管理各類大地工程（地錨、集水井、抗滑樁等）之參考單價。")
    
    db = st.session_state['cost_db']
    
    search_query = st.text_input("🔍 搜尋工項名稱", "")
    if search_query:
        display_db = db[db['工項名稱'].str.contains(search_query, case=False)]
    else:
        display_db = db
        
    st.dataframe(display_db, use_container_width=True)
    
    st.subheader("➕ 新增大地工程工項")
    with st.form("add_geotech_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("工項名稱（例如：大口徑集水井）")
            new_unit = st.text_input("單位（例如：m、支、式、m²）")
        with col2:
            new_price = st.number_input("單價 (元)", min_value=0.0, value=5000.0, step=100.0)
            new_note = st.text_input("備註說明（規格、尺寸、深度的備註）")
            
        submitted = st.form_submit_button("確認新增至資料庫")
        if submitted:
            if new_name:
                new_id = int(db['項次'].max() + 1) if len(db) > 0 else 1
                new_row = pd.DataFrame([{
                    "項次": new_id,
                    "工程類別": "大地工程",
                    "工項名稱": new_name,
                    "單位": new_unit,
                    "單價(元)": new_price,
                    "備註": new_note
                }])
                st.session_state['cost_db'] = pd.concat([db, new_row], ignore_index=True)
                st.success(f"成功新增：{new_name}")
                st.rerun()
            else:
                st.error("請輸入工項名稱！")

# ----------------------------------------------------
# TAB 3: 歷史估算紀錄與匯出
# ----------------------------------------------------
elif tab == "📁 歷史估算紀錄與匯出":
    st.header("📁 歷史估算紀錄與資料匯出")
    
    history_df = pd.DataFrame(st.session_state['history'])
    
    if len(history_df) > 0:
        st.dataframe(history_df, use_container_width=True)
        
        csv = history_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載歷史估算報表 (CSV)",
            data=csv,
            file_name="geotechnical_cost_estimation_report.csv",
            mime="text/csv"
        )
        
        if st.button("🗑️ 清空歷史紀錄"):
            st.session_state['history'] = []
            st.rerun()
    else:
        st.info("目前尚無歷史估算紀錄。")

# ----------------------------------------------------
# 網頁下方資料來源備註 (Footer)
# ----------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 13px;'>
        📌 <b>資料來源與免責聲明備註：</b><br>
        1. 本系統內建之參考單價係依據<b>「行政院公共工程委員會公共工程價格資料庫」</b>及國內各縣市政府、交通部公路局、農業部農村發展及水土保持署之<b>「坡地穩定與大地工程決算慣例」</b>彙整訂定。<br>
        2. 各項工程造價會因地質條件（如岩盤硬度、地下水位）、施工動線、機具進場難易度及物價指數波動而有所差異。<br>
        3. 本系統提供之數據僅供<b>初步工程經費編列、可行性評估或預算初估參考</b>，實際經費應依正式地質鑽探報告、詳細設計圖說及招標規範為準。
    </div>
    """,
    unsafe_allow_html=True
)
