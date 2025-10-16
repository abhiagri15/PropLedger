"""
Reports page for PropLedger
Extracted from app_auth.py for better maintainability
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from streamlit_option_menu import option_menu
from database.database_operations import DatabaseOperations

def render_reports():
    """Render the Reports page"""
    db = DatabaseOperations()

    st.markdown('<h1 class="main-header">📊 Reports</h1>', unsafe_allow_html=True)

    # Sub-menu for Reports
    sub_selected = option_menu(
        None,
        ["P&L", "Transactions"],
        icons=["graph-up", "list-task"],
        menu_icon="cast",
        default_index=0,
        key="reports_submenu",
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#02ab21"},
        }
    )

    if sub_selected == "P&L":
        # Check if demo mode
        is_demo_mode = False
        if st.session_state.user:
            if hasattr(st.session_state.user, 'email'):
                user_email = st.session_state.user.email
            else:
                user_email = st.session_state.user.get('email', 'Unknown')

            if user_email == 'demo@example.com':
                is_demo_mode = True

        if is_demo_mode:
            st.info("📊 **Demo Mode**: Showing sample reports with sample data")

            # Demo P&L Report
            st.markdown("### 📈 Profit & Loss Report (Demo)")

            # Demo report type selection
            demo_report_type = st.selectbox("Report Type", ["Yearly", "Monthly", "Custom"], key="demo_report_type")
            if demo_report_type == "Yearly":
                st.selectbox("Select Year", options=list(range(2020, date.today().year + 2)), index=date.today().year - 2020, key="demo_year_selector")
            elif demo_report_type == "Monthly":
                current_year = date.today().year
                month_options = [
                    f"January {current_year}", f"February {current_year}", f"March {current_year}",
                    f"April {current_year}", f"May {current_year}", f"June {current_year}",
                    f"July {current_year}", f"August {current_year}", f"September {current_year}",
                    f"October {current_year}", f"November {current_year}", f"December {current_year}"
                ]
                st.selectbox("Select Month", options=month_options, index=date.today().month - 1, key="demo_month_selector")
            else:
                st.date_input("Start Date", value=date.today().replace(day=1), key="demo_custom_start")
                st.date_input("End Date", value=date.today(), key="demo_custom_end")

            # Demo data and charts
            demo_data = {
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'Revenue': [2500, 2300, 2800, 2200, 2500, 2400],
                'Expenses': [1800, 1900, 1750, 2000, 1850, 1950],
                'Net Income': [700, 600, 750, 500, 650, 550]
            }
            from plotly.subplots import make_subplots
            fig = make_subplots(rows=2, cols=1, subplot_titles=('Monthly Revenue vs Expenses', 'Monthly Net Income'), vertical_spacing=0.1)
            fig.add_trace(go.Bar(name='Revenue', x=demo_data['Month'], y=demo_data['Revenue'], marker_color='#2E8B57'), row=1, col=1)
            fig.add_trace(go.Bar(name='Expenses', x=demo_data['Month'], y=demo_data['Expenses'], marker_color='#DC143C'), row=1, col=1)
            fig.add_trace(go.Bar(name='Net Income', x=demo_data['Month'], y=demo_data['Net Income'], marker_color='#4169E1'), row=2, col=1)
            fig.update_layout(height=600, showlegend=True, title_text="Demo P&L Report")
            st.plotly_chart(fig, use_container_width=True)
            m1, m2, m3 = st.columns(3)
            with m1: st.metric("Total Revenue", "$15,000", "5.2%")
            with m2: st.metric("Total Expenses", "$11,250", "3.1%")
            with m3: st.metric("Net Profit", "$3,750", "8.3%")
        else:
            # Real P&L Report
            st.markdown("### 📈 Profit & Loss Report")

            # Get selected organization
            if 'selected_organization' in st.session_state and st.session_state.selected_organization:
                selected_org_id = st.session_state.selected_organization
                org_name = st.session_state.get('selected_org_name')
                if not org_name:
                    try:
                        org_obj = db.get_organization_by_id(selected_org_id)
                        org_name = org_obj.name if org_obj else 'Unknown Organization'
                    except Exception:
                        org_name = 'Unknown Organization'

                # Date range selection
                col1, col2 = st.columns(2)
                with col1:
                    report_type = st.selectbox("Report Type", ["Yearly", "Monthly", "Custom"], key="report_type")

                with col2:
                    if report_type == "Yearly":
                        selected_year = st.selectbox("Select Year",
                                                   options=list(range(2020, date.today().year + 2)),
                                                   index=date.today().year - 2020,
                                                   key="year_selector")
                        start_date = date(selected_year, 1, 1)
                        end_date = date(selected_year + 1, 1, 1)
                        period_text = f"Year: {selected_year}"
                    elif report_type == "Monthly":
                        current_year = date.today().year
                        month_options = [
                            f"January {current_year}", f"February {current_year}", f"March {current_year}",
                            f"April {current_year}", f"May {current_year}", f"June {current_year}",
                            f"July {current_year}", f"August {current_year}", f"September {current_year}",
                            f"October {current_year}", f"November {current_year}", f"December {current_year}"
                        ]
                        selected_month = st.selectbox("Select Month",
                                                    options=month_options,
                                                    index=date.today().month - 1,
                                                    key="month_selector")
                        month_number = month_options.index(selected_month) + 1
                        start_date = date(current_year, month_number, 1)
                        end_date = date(current_year + 1, 1, 1) if month_number == 12 else date(current_year, month_number + 1, 1)
                        period_text = f"Month: {selected_month}"
                    else:  # Custom
                        col_start, col_end = st.columns(2)
                        with col_start:
                            start_date = st.date_input("Start Date", value=date.today().replace(day=1), key="custom_start")
                        with col_end:
                            end_date = st.date_input("End Date", value=date.today(), key="custom_end")
                        period_text = f"Period: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"

                # Generate P&L Report
                # Generate P&L Report + Downloads row
                col_gen, col_pdf, col_xls = st.columns([2,1,1])
                with col_gen:
                    generate_clicked = st.button("Generate P&L Report", key="generate_pl")
                with col_pdf:
                    download_pdf_clicked = st.button("📄 Download PDF", key="download_pl_pdf")
                with col_xls:
                    download_xls_clicked = st.button("📊 Download Excel", key="download_pl_xls")

                # Auto-trigger report generation once on first load of Reports
                auto_trigger = False
                if 'pl_auto_generated' not in st.session_state:
                    st.session_state.pl_auto_generated = False
                if not st.session_state.pl_auto_generated:
                    auto_trigger = True
                    st.session_state.pl_auto_generated = True

                if generate_clicked or download_pdf_clicked or download_xls_clicked or auto_trigger:
                    try:
                        # Get income data
                        income_result = db.supabase.table("income").select("*").eq(
                            "organization_id", selected_org_id
                        ).gte("transaction_date", start_date.isoformat()).lt(
                            "transaction_date", end_date.isoformat()
                        ).execute()

                        # Get expense data
                        expense_result = db.supabase.table("expenses").select("*").eq(
                            "organization_id", selected_org_id
                        ).gte("transaction_date", start_date.isoformat()).lt(
                            "transaction_date", end_date.isoformat()
                        ).execute()

                        org_title = org_name if org_name else "Organization"
                        # Determine friendly period text
                        if report_type == "Yearly":
                            period_text = f"Year: {selected_year}"
                        elif report_type == "Monthly":
                            period_text = f"Month: {selected_month}"
                        else:
                            period_text = f"Period: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"

                        if income_result.data or expense_result.data:
                            # Calculate totals
                            total_income = sum(float(item.get('amount', 0)) for item in income_result.data)
                            total_expenses = sum(float(item.get('amount', 0)) for item in expense_result.data)
                            net_profit = total_income - total_expenses

                            # Show heading with org + period
                            st.markdown(f"### 📈 {org_title} P&L — {period_text}")

                            # Summary metrics
                            m1, m2, m3 = st.columns(3)
                            with m1:
                                st.metric("Total Income", f"${total_income:,.2f}")
                            with m2:
                                st.metric("Total Expenses", f"${total_expenses:,.2f}")
                            with m3:
                                margin = (net_profit / total_income * 100) if total_income else 0
                                st.metric("Net Profit", f"${net_profit:,.2f}", f"{margin:.1f}%")

                            # Charts
                            from plotly.subplots import make_subplots

                            # Build monthly trend if Yearly report
                            if report_type == "Yearly":
                                def to_month(row):
                                    return str(row.get('transaction_date', '') or '')[:7]
                                income_df = pd.DataFrame(income_result.data)
                                expense_df = pd.DataFrame(expense_result.data)
                                income_monthly = income_df.assign(month=income_df.apply(to_month, axis=1)).groupby('month')['amount'].sum() if not income_df.empty else pd.Series(dtype=float)
                                expense_monthly = expense_df.assign(month=expense_df.apply(to_month, axis=1)).groupby('month')['amount'].sum() if not expense_df.empty else pd.Series(dtype=float)
                                months = sorted(set(income_monthly.index).union(expense_monthly.index))
                                y_income = [float(income_monthly.get(m, 0)) for m in months]
                                y_exp = [float(expense_monthly.get(m, 0)) for m in months]
                                fig = make_subplots(rows=1, cols=1)
                                fig.add_trace(go.Scatter(x=months, y=y_income, mode='lines+markers', name='Income', line=dict(color='#2E8B57')))
                                fig.add_trace(go.Scatter(x=months, y=y_exp, mode='lines+markers', name='Expenses', line=dict(color='#DC143C')))
                                fig.update_layout(title_text="Monthly P&L Trend", height=400)
                                st.plotly_chart(fig, use_container_width=True)

                            # Category breakdown pies
                            if income_result.data:
                                inc_df = pd.DataFrame(income_result.data)
                                inc_by_cat = inc_df.groupby('income_type')['amount'].sum().reset_index() if 'income_type' in inc_df.columns else pd.DataFrame()
                            else:
                                inc_by_cat = pd.DataFrame()
                            if expense_result.data:
                                exp_df = pd.DataFrame(expense_result.data)
                                exp_by_cat = exp_df.groupby('expense_type')['amount'].sum().reset_index() if 'expense_type' in exp_df.columns else pd.DataFrame()
                            else:
                                exp_by_cat = pd.DataFrame()
                            c1, c2 = st.columns(2)
                            if not inc_by_cat.empty:
                                c1.plotly_chart(go.Figure(data=[go.Pie(labels=inc_by_cat['income_type'], values=inc_by_cat['amount'])]).update_layout(title_text="Income by Type"), use_container_width=True)
                            if not exp_by_cat.empty:
                                c2.plotly_chart(go.Figure(data=[go.Pie(labels=exp_by_cat['expense_type'], values=exp_by_cat['amount'])]).update_layout(title_text="Expenses by Type"), use_container_width=True)

                            # If download was clicked, return files
                            if download_pdf_clicked:
                                from reportlab.lib.pagesizes import letter
                                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                                from reportlab.platypus import Image as RLImage
                                from reportlab.lib.styles import getSampleStyleSheet
                                from reportlab.lib import colors
                                import io, base64
                                buffer = io.BytesIO()
                                doc = SimpleDocTemplate(buffer, pagesize=letter)
                                styles = getSampleStyleSheet()
                                story = []
                                story.append(Paragraph(f"{org_title} P&L — {period_text}", styles['Title']))
                                story.append(Spacer(1, 12))
                                summary_data = [
                                    ['Metric', 'Amount'],
                                    ['Total Income', f"${total_income:,.2f}"],
                                    ['Total Expenses', f"${total_expenses:,.2f}"],
                                    ['Net Profit', f"${net_profit:,.2f}"]
                                ]
                                t = Table(summary_data)
                                t.setStyle(TableStyle([
                                    ('BACKGROUND', (0,0), (-1,0), colors.grey),
                                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                                    ('GRID', (0,0), (-1,-1), 1, colors.black)
                                ]))
                                story.append(t)
                                story.append(Spacer(1, 16))

                                # Try to embed the same charts as images
                                try:
                                    import plotly.io as pio
                                    # Rebuild dataframes for this run
                                    income_df = pd.DataFrame(income_result.data)
                                    expense_df = pd.DataFrame(expense_result.data)

                                    # Monthly trend (only for Yearly and when data present)
                                    if report_type == "Yearly" and (not income_df.empty or not expense_df.empty):
                                        def to_month_str(ts):
                                            return str(ts)[:7]
                                        if not income_df.empty:
                                            income_df['month'] = income_df['transaction_date'].map(to_month_str)
                                            income_monthly = income_df.groupby('month')['amount'].sum()
                                        else:
                                            income_monthly = pd.Series(dtype=float)
                                        if not expense_df.empty:
                                            expense_df['month'] = expense_df['transaction_date'].map(to_month_str)
                                            expense_monthly = expense_df.groupby('month')['amount'].sum()
                                        else:
                                            expense_monthly = pd.Series(dtype=float)
                                        months = sorted(set(income_monthly.index).union(expense_monthly.index))
                                        y_income = [float(income_monthly.get(m, 0)) for m in months]
                                        y_exp = [float(expense_monthly.get(m, 0)) for m in months]
                                        trend_fig = make_subplots(rows=1, cols=1)
                                        trend_fig.add_trace(go.Scatter(x=months, y=y_income, mode='lines+markers', name='Income', line=dict(color='#2E8B57')))
                                        trend_fig.add_trace(go.Scatter(x=months, y=y_exp, mode='lines+markers', name='Expenses', line=dict(color='#DC143C')))
                                        trend_fig.update_layout(title_text="Monthly P&L Trend", height=400, width=700, margin=dict(l=20,r=20,t=40,b=20))
                                        img_bytes = pio.to_image(trend_fig, format='png', width=700, height=400)
                                        story.append(RLImage(io.BytesIO(img_bytes), width=500, height=285))
                                        story.append(Spacer(1, 12))

                                    # Income pie
                                    if not income_df.empty and 'income_type' in income_df.columns:
                                        inc_by_cat = income_df.groupby('income_type')['amount'].sum().reset_index()
                                        inc_fig = go.Figure(data=[go.Pie(labels=inc_by_cat['income_type'], values=inc_by_cat['amount'])])
                                        inc_fig.update_layout(title_text="Income by Type", height=350, width=350, margin=dict(l=10,r=10,t=30,b=10))
                                        inc_img = pio.to_image(inc_fig, format='png', width=350, height=350)
                                        story.append(RLImage(io.BytesIO(inc_img), width=260, height=260))
                                        story.append(Spacer(1, 8))

                                    # Expenses pie
                                    if not expense_df.empty and 'expense_type' in expense_df.columns:
                                        exp_by_cat = expense_df.groupby('expense_type')['amount'].sum().reset_index()
                                        exp_fig = go.Figure(data=[go.Pie(labels=exp_by_cat['expense_type'], values=exp_by_cat['amount'])])
                                        exp_fig.update_layout(title_text="Expenses by Type", height=350, width=350, margin=dict(l=10,r=10,t=30,b=10))
                                        exp_img = pio.to_image(exp_fig, format='png', width=350, height=350)
                                        story.append(RLImage(io.BytesIO(exp_img), width=260, height=260))
                                        story.append(Spacer(1, 8))
                                except Exception as export_err:
                                    story.append(Paragraph("Note: Charts omitted in PDF (install with: pip install kaleido).", styles['Italic']))
                                    story.append(Spacer(1, 8))

                                doc.build(story)
                                buffer.seek(0)
                                b64 = base64.b64encode(buffer.getvalue()).decode()
                                filename = f"{org_title.replace(' ', '_')}_PL_{period_text.replace(' ', '_').replace(':','')}.pdf"
                                st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📄 Click to download PDF</a>', unsafe_allow_html=True)

                            if download_xls_clicked:
                                import io
                                output = io.BytesIO()
                                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                    pd.DataFrame([
                                        ['Total Income', total_income],
                                        ['Total Expenses', total_expenses],
                                        ['Net Profit', net_profit]
                                    ], columns=['Metric','Amount']).to_excel(writer, sheet_name='Summary', index=False)
                                output.seek(0)
                                import base64
                                b64 = base64.b64encode(output.getvalue()).decode()
                                filename = f"{org_title.replace(' ', '_')}_PL_{period_text.replace(' ', '_').replace(':','')}.xlsx"
                                st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📊 Click to download Excel</a>', unsafe_allow_html=True)

                        else:
                            st.info("No financial data found for the selected period.")

                    except Exception as e:
                        st.error(f"Error generating P&L report: {str(e)}")
            else:
                st.warning("Please select an organization first to view reports.")

    elif sub_selected == "Transactions":
        # -------------------- Transactions Report --------------------
        st.markdown("## 📑 Transactions Report")
        if 'selected_organization' in st.session_state and st.session_state.selected_organization:
            selected_org_id = st.session_state.selected_organization
            org_name_txn = st.session_state.get('selected_org_name')
            if not org_name_txn:
                try:
                    org_obj = db.get_organization_by_id(selected_org_id)
                    org_name_txn = org_obj.name if org_obj else 'Unknown Organization'
                except Exception:
                    org_name_txn = 'Unknown Organization'

            # Preload properties for this organization for filter and name lookup
            props_res = db.supabase.table("properties").select("id,name,address").eq("organization_id", selected_org_id).execute()
            properties_list = props_res.data or []
            prop_map = {p['id']: (p.get('name') or p.get('address') or f"Property {p['id']}") for p in properties_list}
            prop_options = ["All"] + [prop_map[p['id']] for p in properties_list]

            # Filters row
            c1, c2, c3, c4 = st.columns([1,1,1,1])
            with c1:
                txn_report_type = st.selectbox("Report Type", ["Yearly", "Monthly", "Custom"], key="txn_report_type")
            with c2:
                # Date type filter (Year/Month/Custom)
                if txn_report_type == "Yearly":
                    txn_year = st.selectbox("Select Year",
                                         options=list(range(2020, date.today().year + 2)),
                                         index=date.today().year - 2020,
                                         key="txn_year_selector")
                    txn_start = date(txn_year, 1, 1)
                    txn_end = date(txn_year + 1, 1, 1)
                    txn_period_text = f"Year: {txn_year}"
                elif txn_report_type == "Monthly":
                    cur_year = date.today().year
                    month_opts = [
                        f"January {cur_year}", f"February {cur_year}", f"March {cur_year}",
                        f"April {cur_year}", f"May {cur_year}", f"June {cur_year}",
                        f"July {cur_year}", f"August {cur_year}", f"September {cur_year}",
                        f"October {cur_year}", f"November {cur_year}", f"December {cur_year}"
                    ]
                    txn_month_label = st.selectbox("Select Month", month_opts, index=date.today().month - 1, key="txn_month_selector")
                    m_num = month_opts.index(txn_month_label) + 1
                    txn_start = date(cur_year, m_num, 1)
                    txn_end = date(cur_year + 1, 1, 1) if m_num == 12 else date(cur_year, m_num + 1, 1)
                    txn_period_text = f"Month: {txn_month_label}"
                else:
                    d1, d2 = st.columns(2)
                    with d1:
                        txn_start = st.date_input("Start Date", value=date.today().replace(day=1), key="txn_start")
                    with d2:
                        txn_end = st.date_input("End Date", value=date.today(), key="txn_end")
                    txn_period_text = f"Period: {txn_start.strftime('%b %d, %Y')} - {txn_end.strftime('%b %d, %Y')}"
            with c3:
                selected_property_label = st.selectbox("Property", options=prop_options, index=0, key="txn_property_filter")
                # Resolve selected property id (None means All)
                selected_property_id = None
                if selected_property_label != "All":
                    # reverse lookup by label
                    for pid, pname in prop_map.items():
                        if pname == selected_property_label:
                            selected_property_id = pid
                            break
            with c4:
                txn_type_filter = st.selectbox("Transaction Type", ["All", "Income", "Expenses"], key="txn_type_filter")

            # Generate button
            gen_txn = st.button("Generate Transactions Report", key="generate_txn")
            if gen_txn:
                try:
                    rows = []

                    # Helper to apply property filter
                    def apply_common_filters(builder):
                        builder = builder.eq("organization_id", selected_org_id).gte("transaction_date", txn_start.isoformat()).lt("transaction_date", txn_end.isoformat())
                        if selected_property_id is not None:
                            builder = builder.eq("property_id", selected_property_id)
                        return builder

                    if txn_type_filter in ("All", "Income"):
                        inc_builder = db.supabase.table("income").select("*")
                        inc_res = apply_common_filters(inc_builder).execute()
                        for r in inc_res.data or []:
                            rows.append({
                                'S.No.': 0,  # will fill after sort
                                'Date': r.get('transaction_date'),
                                'Type': 'Income',
                                'Property': prop_map.get(r.get('property_id'), 'Unknown'),
                                'Description': r.get('description') or r.get('income_type') or '',
                                'Amount': float(r.get('amount', 0))
                            })

                    if txn_type_filter in ("All", "Expenses"):
                        exp_builder = db.supabase.table("expenses").select("*")
                        exp_res = apply_common_filters(exp_builder).execute()
                        for r in exp_res.data or []:
                            rows.append({
                                'S.No.': 0,  # will fill after sort
                                'Date': r.get('transaction_date'),
                                'Type': 'Expense',
                                'Property': prop_map.get(r.get('property_id'), 'Unknown'),
                                'Description': r.get('description') or r.get('expense_type') or '',
                                'Amount': float(r.get('amount', 0))
                            })

                    if rows:
                        df = pd.DataFrame(rows)
                        df.sort_values(by=['Date', 'Type'], inplace=True)
                        # Add serial number starting at 1
                        df['S.No.'] = range(1, len(df) + 1)
                        # Reorder columns: S.No., Date, Type, Property, Description, Amount
                        df = df[['S.No.', 'Date', 'Type', 'Property', 'Description', 'Amount']]
                        # Explicitly drop any id column if present
                        if 'id' in df.columns:
                            df = df.drop(columns=['id'])

                        # Add Total row
                        total_amount = df['Amount'].sum()
                        total_row = pd.DataFrame({
                            'S.No.': [0],  # Use 0 instead of empty string
                            'Date': [''],
                            'Type': [''],
                            'Property': [''],
                            'Description': ['**TOTAL**'],
                            'Amount': [total_amount]
                        })
                        df_with_total = pd.concat([df, total_row], ignore_index=True)

                        st.markdown(f"#### {org_name_txn} — {txn_period_text}")
                        st.dataframe(df_with_total, use_container_width=True, hide_index=True)

                        # Download buttons for Transactions Report
                        col1, col2 = st.columns(2)

                        with col1:
                            # PDF Download
                            if st.button("📄 Download PDF", key="download_txn_pdf"):
                                try:
                                    from reportlab.lib.pagesizes import letter
                                    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                                    from reportlab.lib.styles import getSampleStyleSheet
                                    from reportlab.lib import colors
                                    import io
                                    import base64

                                    buffer = io.BytesIO()
                                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                                    story = []
                                    styles = getSampleStyleSheet()

                                    # Title
                                    title = Paragraph(f"<b>Transactions Report - {org_name_txn}</b>", styles['Title'])
                                    story.append(title)
                                    story.append(Spacer(1, 12))

                                    # Period
                                    period = Paragraph(f"<b>Period:</b> {txn_period_text}", styles['Normal'])
                                    story.append(period)
                                    story.append(Spacer(1, 12))

                                    # Convert dataframe to table data
                                    table_data = [df_with_total.columns.tolist()]
                                    for _, row in df_with_total.iterrows():
                                        table_data.append(row.tolist())

                                    # Create table
                                    table = Table(table_data)
                                    table.setStyle(TableStyle([
                                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                                    ]))

                                    story.append(table)
                                    doc.build(story)

                                    buffer.seek(0)
                                    b64 = base64.b64encode(buffer.getvalue()).decode()
                                    filename = f"{org_name_txn.replace(' ', '_')}_Transactions_{txn_period_text.replace(' ', '_').replace(':', '')}.pdf"
                                    st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📄 Click to download PDF</a>', unsafe_allow_html=True)

                                except Exception as e:
                                    st.error(f"Error generating PDF: {str(e)}")

                        with col2:
                            # Excel Download
                            if st.button("📊 Download Excel", key="download_txn_excel"):
                                try:
                                    import io
                                    output = io.BytesIO()
                                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                        # Summary sheet
                                        summary_data = pd.DataFrame([
                                            ['Total Transactions', len(df)],
                                            ['Total Amount', f"${total_amount:,.2f}"],
                                            ['Period', txn_period_text]
                                        ], columns=['Metric', 'Value'])
                                        summary_data.to_excel(writer, sheet_name='Summary', index=False)

                                        # Transactions sheet
                                        df_with_total.to_excel(writer, sheet_name='Transactions', index=False)

                                    output.seek(0)
                                    b64 = base64.b64encode(output.getvalue()).decode()
                                    filename = f"{org_name_txn.replace(' ', '_')}_Transactions_{txn_period_text.replace(' ', '_').replace(':', '')}.xlsx"
                                    st.markdown(f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📊 Click to download Excel</a>', unsafe_allow_html=True)

                                except Exception as e:
                                    st.error(f"Error generating Excel: {str(e)}")
                    else:
                        st.info("No transactions found for the selected criteria.")
                except Exception as e:
                    st.error(f"Error generating Transactions report: {str(e)}")
        else:
            st.warning("Please select an organization first to view transactions.")
