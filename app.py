import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="工程經費初估資料庫與計算系統",
    page_icon="🏗️",
    layout="wide"
)

# 初始化資料庫（Session State）
if 'cost_db' not in st.session_state:
    st.session_state['cost_db'] = pd.DataFrame([
        {"項次": 1, "工程類別": "建築工程", "工項名稱": "RC造集合住宅（地上10層以下）", "單位": "坪", "單價(元)": 85000, "備註": "含基礎與基本裝修"},
        {"項次": 2, "工程類別": "建築工程", "工項名稱": "鋼骨結構廠房（SRC/SS）", "單位": "坪", "單價(元)": 95000, "備註": "大跨距鋼構"},
        {"項次": 3, "工程類別": "土木工程", "工項名稱": "基地開挖與支撐（擋土工程）", "單位": "立方公尺 (m³)", "單價(元)": 1800, "備註": "連續壁及H型鋼支撐"},
        {"項次": 4, "工程類別": "道路橋樑", "工項名稱": "瀝青混凝土鋪面工程", "單位": "平方公尺 (m²)", "單價(元)": 650, "備註": "厚度 10cm"},
        {"項次": 5, "工程類別": "機電工程", "工項名稱": "空調與消防綜合機電系統", "單位": "坪", "單價(元)": 22000, "備註": "商辦/住宅標準等級"},
        {"項次": 6, "工程類別": "景觀綠美化", "工項名稱": "戶外景觀植栽與鋪面", "單位": "平方公尺 (m²)", "單價(元)": 3200, "備註": "含草皮、灌木與透水鋪面"}
    ])

if 'history' not in st.session_state:
    st.session_state['history'] = []

st.title("🏗️ 工程經費初估資料庫與計算系統")
st.markdown("本系統提供工程單價參考資料庫維護，以及結合間接費用（管理費、設計費、準備金、稅金）的工程經費快速初估與試算功能。")

# 側邊欄導覽
tab = st.sidebar.radio("功能選單", ["📊 工程經費初估計算", "📚 單價資料庫管理", "📁 歷史估算紀錄與匯出"])

# ----------------------------------------------------
# TAB 1: 工程經費初估計算
# ----------------------------------------------------
if tab == "📊 工程經費初估計算":
    st.header("💡 工程經費智慧初估")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. 專案基本資料與數量輸入")
        project_name = st.text_input("專案名稱", "某示範新建工程專案")
        
        db = st.session_state['cost_db']
        categories = db['工程類別'].unique().tolist()
        selected_category = st.selectbox("選擇工程類別", categories)
        
        filtered_items = db[db['工程類別'] == selected_category]
        item_options = filtered_items['工項名稱'].tolist()
        selected_item_name = st.selectbox("選擇參考工項", item_options)
        
        row = filtered_items[filtered_items['工項名稱'] == selected_item_name].iloc[0]
        default_unit_price = float(row['單價(元)'])
        unit = row['單位']
        
        unit_price = st.number_input(f"調整單價 (元/{unit})", value=default_unit_price, step=100.0)
        quantity = st.number_input(f"工程數量 ({unit})", value=100.0, step=10.0)
        
        direct_cost = unit_price * quantity
        
        st.subheader("2. 間接費用比例設定 (%)")
        col_a, col_b = st.columns(2)
        with col_a:
            design_fee_pct = st.number_input("設計監造費率 (%)", value=7.0, step=0.5)
            management_fee_pct = st.number_input("工程管理費率 (%)", value=3.0, step=0.5)
        with col_b:
            contingency_pct = st.number_input("工程準備金率 (%)", value=5.0, step=0.5)
            tax_pct = st.number_input("營業稅率 (%)", value=5.0, step=0.5)

    with col2:
        st.subheader("3. 經費初估總表與結構分析")
        
        design_fee = direct_cost * (design_fee_pct / 100)
        management_fee = direct_cost * (management_fee_pct / 100)
        subtotal_before_contingency = direct_cost + design_fee + management_fee
        contingency = subtotal_before_contingency * (contingency_pct / 100)
        subtotal_before_tax = subtotal_before_contingency + contingency
        tax = subtotal_before_tax * (tax_pct / 100)
        total_cost = subtotal_before_tax + tax
        
        st.metric(label="💰 工程總經費初估 (含稅)", value=f"NT$ {total_cost:,.0f} 元")
        
        cost_breakdown = pd.DataFrame({
            "費用項目": ["直接工程費", "設計監造費", "工程管理費", "工程準備金", "營業稅"],
            "金額 (元)": [direct_cost, design_fee, management_fee, contingency, tax]
        })
        
        st.dataframe(cost_breakdown.style.format({"金額 (元)": "{:,.0f}"}), use_container_width=True)
        
        # 繪製圖表
        chart = alt.Chart(cost_breakdown).mark_bar().encode(
            x=alt.X('金額 (元):Q', title='金額 (NT$)'),
            y=alt.Y('費用項目:N', sort='-x', title='費用項目'),
            color='費用項目:N',
            tooltip=['費用項目', alt.Tooltip('金額 (元):Q', format=',.0f')]
        ).properties(height=250, title="經費結構占比圖")
        
        st.altair_chart(chart, use_container_width=True)
        
        if st.button("💾 儲存此筆估算至歷史紀錄", type="primary"):
            record = {
                "專案名稱": project_name,
                "工程類別": selected_category,
                "工項名稱": selected_item_name,
                "數量": quantity,
                "單位": unit,
                "直接工程費": direct_cost,
                "總經費(含稅)": total_cost,
                "建立時間": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state['history'].append(record)
            st.success("已成功儲存至歷史估算紀錄！")

# ----------------------------------------------------
# TAB 2: 單價資料庫管理
# ----------------------------------------------------
elif tab == "📚 單價資料庫管理":
    st.header("📚 工程單價參考資料庫管理")
    st.markdown("您可以在此檢視、搜尋現有單價資料，或新增自訂的工程單價項目。")
    
    db = st.session_state['cost_db']
    
    search_query = st.text_input("🔍 搜尋工項名稱或類別", "")
    if search_query:
        mask = db['工項名稱'].str.contains(search_query, case=False) | db['工程類別'].str.contains(search_query, case=False)
        display_db = db[mask]
    else:
        display_db = db
        
    st.dataframe(display_db, use_container_width=True)
    
    st.subheader("➕ 新增單價項目")
    with st.form("add_item_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_cat = st.selectbox("工程類別", ["建築工程", "土木工程", "道路橋樑", "機電工程", "景觀綠美化", "其他"])
            new_name = st.text_input("工項名稱")
        with col2:
            new_unit = st.text_input("單位 (如：坪、m²、m³、式)")
            new_price = st.number_input("單價 (元)", min_value=0.0, value=10000.0, step=100.0)
        with col3:
            new_note = st.text_input("備註說明")
            
        submitted = st.form_submit_button("確認新增至資料庫")
        if submitted:
            if new_name:
                new_id = int(db['項次'].max() + 1) if len(db) > 0 else 1
                new_row = pd.DataFrame([{
                    "項次": new_id,
                    "工程類別": new_cat,
                    "工項名稱": new_name,
                    "單位": new_unit,
                    "單價(元)": new_price,
                    "備註": new_note
                }])
                st.session_state['cost_db'] = pd.concat([db, new_row], ignore_index=True)
                st.success(f"成功新增工項：{new_name}")
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
            file_name="engineering_cost_estimation_report.csv",
            mime="text/csv"
        )
        
        if st.button("🗑️ 清空歷史紀錄"):
            st.session_state['history'] = []
            st.rerun()
    else:
        st.info("目前尚無歷史估算紀錄，請至「工程經費初估計算」頁面進行試算與儲存。")