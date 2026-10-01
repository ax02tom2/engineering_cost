import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="大地工程經費初估與單價資料庫",
    page_icon="⛰️",
    layout="wide"
)

# ==========================================
# 初始化大地工程預設資料庫（參考 PCCES 公開資訊）
# ==========================================
if 'cost_db' not in st.session_state:
    st.session_state['cost_db'] = pd.DataFrame([
        {"項次": 1, "工程類別": "擋土與開挖", "工項名稱": "連續壁 (厚度80cm)", "單位": "m²", "單價(元)": 9500, "備註": "含導溝、開挖與特密管澆置"},
        {"項次": 2, "工程類別": "擋土與開挖", "工項名稱": "預壘排樁 (CIP, 直徑60cm)", "單位": "m", "單價(元)": 1800, "備註": "含鑽掘、鋼筋籠與灌漿"},
        {"項次": 3, "工程類別": "擋土與開挖", "工項名稱": "鋼板樁打拔 (Type IV)", "單位": "m", "單價(元)": 650, "備註": "震動機打拔工資 (不含長租)"},
        {"項次": 4, "工程類別": "支撐工程", "工項名稱": "水平型鋼支撐架設與拆除", "單位": "噸", "單價(元)": 6500, "備註": "含千斤頂施預力與拆除"},
        {"項次": 5, "工程類別": "地錨與岩栓", "工項名稱": "預力地錨 (永久性, 30噸~40噸)", "單位": "m", "單價(元)": 1600, "備註": "含鑽孔、灌漿及張拉鎖定"},
        {"項次": 6, "工程類別": "地錨與岩栓", "工項名稱": "自鑽式岩栓 / 土釘", "單位": "m", "單價(元)": 950, "備註": "含引孔及二次灌漿"},
        {"項次": 7, "工程類別": "坡地穩定", "工項名稱": "微型樁 (直徑15cm)", "單位": "m", "單價(元)": 1200, "備註": "含無縫鋼管與水泥砂漿"},
        {"項次": 8, "工程類別": "坡地穩定", "工項名稱": "抗滑樁 (大口徑全套管, 直徑100cm)", "單位": "m", "單價(元)": 15000, "備註": "含鋼筋籠及混凝土灌注"},
        {"項次": 9, "工程類別": "水土保持", "工項名稱": "大口徑集水井 (直徑>1.5m)", "單位": "m", "單價(元)": 15000, "備註": "含環片支撐及開挖排水"},
        {"項次": 10, "工程類別": "水土保持", "工項名稱": "橫向集水管 / 坡面集水管", "單位": "m", "單價(元)": 800, "備註": "含鑽孔與透水管材"},
        {"項次": 11, "工程類別": "水土保持", "工項名稱": "坡面植生 (噴植草籽)", "單位": "m²", "單價(元)": 250, "備註": "含客土、草籽及養護"},
        {"項次": 12, "工程類別": "雜項工程", "工項名稱": "施工臨時便道 (開挖與級配回填)", "單位": "式", "單價(元)": 250000, "備註": "依現地狀況調整單價"}
    ])

if 'history' not in st.session_state:
    st.session_state['history'] = []

st.title("⛰️ 大地工程經費初估資料庫與計算系統")
st.markdown("內建大地工程常見公開參考單價，請於選單挑選工項並填寫數量，系統將自動試算總經費。")

# 側邊欄導覽
tab = st.sidebar.radio("功能選單", ["📊 工程經費初估計算", "📚 大地單價資料庫管理", "📁 歷史估算紀錄與匯出"])

# ==========================================
# TAB 1: 工程經費初估計算
# ==========================================
if tab == "📊 工程經費初估計算":
    st.header("💡 大地工程經費智慧初估試算")
    
    db = st.session_state['cost_db']
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("1. 專案名稱與工項選擇")
        project_name = st.text_input("專案名稱", "某坡地穩定與水保改善工程")
        
        # 製作下拉多選選單
        all_item_names = db['工項名稱'].tolist()
        selected_item_names = st.multiselect(
            "請選擇本次工程需要的工項 (可複選)：", 
            options=all_item_names,
            placeholder="點擊此處展開工項列表..."
        )
        
        selected_items_data = []
        
        if selected_item_names:
            st.markdown("##### 📝 請輸入各工項數量 (單價已自動帶入公開行情，亦可手動微調)")
            for item_name in selected_item_names:
                # 從資料庫抓取該工項的預設資料
                row = db[db['工項名稱'] == item_name].iloc[0]
                
                with st.container():
                    st.markdown(f"**{item_name}** ({row['備註']})")
                    c_qty, c_price, c_total = st.columns([1, 1, 1])
                    
                    with c_qty:
                        qty = st.number_input(f"數量 ({row['單位']})", value=10.0, step=10.0, key=f"qty_{item_name}")
                    with c_price:
                        # 預設帶入公開單價，但也允許使用者微調
                        prc = st.number_input(f"單價 (元/{row['單位']})", value=float(row['單價(元)']), step=100.0, key=f"prc_{item_name}")
                    with c_total:
                        subtotal = qty * prc
                        st.metric("複價小計", f"NT$ {subtotal:,.0f}")
                    
                    st.divider()
                    
                    selected_items_data.append({
                        "工項名稱": item_name,
                        "單位": row['單位'],
                        "數量": qty,
                        "單價": prc,
                        "複價": subtotal,
                        "備註": row['備註']
                    })

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
            
            # 間接費用計算邏輯
            misc_cost = direct_cost * (misc_pct / 100)
            subtotal_1 = direct_cost + misc_cost
            
            management_cost = subtotal_1 * (management_pct / 100)
            subtotal_2 = subtotal_1 + management_cost
            
            tax_cost = subtotal_2 * (tax_pct / 100)
            total_cost = subtotal_2 + tax_cost
            
            st.metric(label="💰 總經費初估 (含稅)", value=f"NT$ {total_cost:,.0f} 元")
            
            st.write("##### 一、直接工程費明細")
            st.dataframe(df_selected[['工項名稱', '數量', '單位', '單價', '複價']].style.format({"數量": "{:,.1f}", "單價": "{:,.0f}", "複價": "{:,.0f}"}), use_container_width=True, hide_index=True)
            
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
            st.info("👈 請先從左側選單選擇「工項」以進行試算。")

# ==========================================
# TAB 2: 單價資料庫管理
# ==========================================
elif tab == "📚 大地單價資料庫管理":
    st.header("📚 大地工程參考單價資料庫")
    st.markdown("此處數據皆以**公開資訊 (如PCCES等)**為預設基準。若查無所需工項，請透過下方表單手動新增。")
    
    db = st.session_state['cost_db']
    
    search_query = st.text_input("🔍 搜尋工項名稱", "")
    if search_query:
        display_db = db[db['工項名稱'].str.contains(search_query, case=False)]
    else:
        display_db = db
        
    st.dataframe(display_db, use_container_width=True, hide_index=True)
    
    st.subheader("➕ 人工新增自訂工項")
    with st.form("add_geotech_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_cat = st.selectbox("工程類別", ["擋土與開挖", "支撐工程", "地錨與岩栓", "坡地穩定", "水土保持", "雜項工程", "其他"])
            new_name = st.text_input("工項名稱 (例如：特殊口徑集水井)")
            new_unit = st.text_input("單位 (例如：m, 支, 式, m²)")
        with col2:
            new_price = st.number_input("單價 (元)", min_value=0.0, value=5000.0, step=100.0)
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
                st.success(f"成功新增：{new_name}！現在您可以回到「工程經費初估計算」選單中找到它。")
                st.rerun()
            else:
                st.error("請輸入工項名稱！")

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

# ==========================================
# 網頁下方資料來源備註 (Footer)
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 13px;'>
        📌 <b>資料來源與免責聲明備註：</b><br>
        1. 本系統預設內建之參考單價，係參考<b>行政院公共工程委員會 (PCCES) 價格資料庫</b>及近期國內大地工程招標之公開參考行情編製。<br>
        2. 工程造價會因現地地質條件、施工動線、機具進場難易度及物價波動而有顯著差異，公開行情僅供基準參考。<br>
        3. 本系統提供之數據與試算結果僅供<b>專案初期經費編列、可行性評估參考</b>，不具備法律或合約約束力。正式經費應依詳細設計圖說及預算書為準。<br>
        4. 若公開資料庫未涵蓋特殊工項，使用者可利用「單價資料庫管理」頁面以人工方式自行擴充。
    </div>
    """,
    unsafe_allow_html=True
)
