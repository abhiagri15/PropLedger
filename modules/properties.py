"""
Properties page for PropLedger
Extracted from app_auth.py for better maintainability
Updated: 2025-10-17 - Added date filter and grand totals
"""

import streamlit as st
from datetime import datetime, date
from database.database_operations import DatabaseOperations
from database.models import Property, PropertyType
from services.geocoding import geocoding_service

def render_properties():
    """Render the Properties page"""
    db = DatabaseOperations()

    # Check if demo mode
    is_demo_mode = False
    if st.session_state.user:
        if hasattr(st.session_state.user, 'email'):
            is_demo_mode = getattr(st.session_state.user, 'email', '') == 'demo@example.com'
        else:
            is_demo_mode = st.session_state.user.get('email', '') == 'demo@example.com'

    if is_demo_mode:
        st.info("🎯 Demo mode - showing sample properties. Sign up to manage your own properties!")
    else:
        # Get selected organization
        selected_org_id = st.session_state.get('selected_organization')
        if not selected_org_id:
            st.error("Please select an organization first.")
            return

        # Get organization name
        org = db.get_organization_by_id(selected_org_id)
        org_name = org.name if org else "Unknown Organization"

        # Real property management with organization filtering
        # Tabs for property management - matching reference design
        tab1, tab2, tab3 = st.tabs(["View Properties", "Add Property", "Managing Properties"])

        with tab1:
            all_properties = db.get_properties()
            # Filter properties by organization
            org_properties = [p for p in all_properties if p.organization_id == selected_org_id]

            if org_properties:
                # Filter Controls at the top
                col1, col2, col3 = st.columns(3)

                with col1:
                    # Get unique property names
                    property_names = ["All Properties"] + sorted(list(set(p.name for p in org_properties)))
                    selected_property = st.selectbox(
                        "Filter by Property Name",
                        property_names,
                        key="view_property_filter"
                    )

                with col2:
                    # Get unique property types
                    property_types = ["All Types"] + sorted(list(set(p.property_type.title() for p in org_properties)))
                    selected_type = st.selectbox(
                        "Filter by Type",
                        property_types,
                        key="view_type_filter"
                    )

                with col3:
                    # Date filter
                    date_filter = st.selectbox(
                        "Filter by Date",
                        ["All Time", "Current Month", "Current Year", "Custom"],
                        index=1,  # Default to "Current Month"
                        key="view_date_filter"
                    )

                # Custom date range inputs (show only if Custom is selected)
                start_date = None
                end_date = None
                if date_filter == "Custom":
                    st.markdown("**Select Date Range:**")
                    col_date1, col_date2 = st.columns([1, 1])
                    with col_date1:
                        start_date = st.date_input("Start Date", value=date.today().replace(day=1), key="view_start_date")
                    with col_date2:
                        end_date = st.date_input("End Date", value=date.today(), key="view_end_date")

                    # Convert to datetime
                    start_date = datetime.combine(start_date, datetime.min.time())
                    end_date = datetime.combine(end_date, datetime.max.time())

                elif date_filter == "Current Month":
                    # First day of current month to today
                    start_date = datetime.combine(date.today().replace(day=1), datetime.min.time())
                    end_date = datetime.combine(date.today(), datetime.max.time())

                elif date_filter == "Current Year":
                    # First day of current year to today
                    start_date = datetime.combine(date.today().replace(month=1, day=1), datetime.min.time())
                    end_date = datetime.combine(date.today(), datetime.max.time())

                # Apply filters
                filtered_properties = org_properties

                if selected_property != "All Properties":
                    filtered_properties = [p for p in filtered_properties if p.name == selected_property]

                if selected_type != "All Types":
                    filtered_properties = [p for p in filtered_properties if p.property_type.title() == selected_type]

                st.markdown("---")

                # Create data for table
                import pandas as pd
                table_data = []

                for prop in filtered_properties:
                    # Get financial summary with date filter
                    financial_summary = db.get_property_financial_summary(prop.id, start_date, end_date)

                    table_data.append({
                        'Property Name': prop.name,
                        'Address': prop.address,
                        'Type': prop.property_type.title(),
                        'Purchase Price': f"${prop.purchase_price:,.0f}",
                        'Monthly Rent': f"${prop.monthly_rent:,.0f}",
                        'Total Income': f"${financial_summary['total_income']:,.0f}",
                        'Total Expenses': f"${financial_summary['total_expenses']:,.0f}",
                        'Net Income': f"${financial_summary['net_income']:,.0f}",
                        'ROI': f"{financial_summary['roi']:.1f}%"
                    })

                # Display as DataFrame
                if table_data:
                    df_properties = pd.DataFrame(table_data)
                    st.dataframe(df_properties, use_container_width=True, hide_index=True)
                else:
                    st.info("No properties match the selected filters.")
            else:
                st.info(f"No properties found for {org_name}. Add your first property below.")

        with tab2:
            st.subheader("Add New Property")

            # Address input section (outside form for suggestions)
            st.markdown("### Property Details")

            # Address search input
            address_search_key = f"address_search_{st.session_state.get('form_reset_counter', 0)}"
            address_search = st.text_input(
                "Search Address *",
                placeholder="Start typing address... (e.g., 123 Main St, New York)",
                key=address_search_key
            )

            # Address suggestions using selectbox
            selected_address = None
            if address_search and len(address_search.strip()) >= 3:
                try:
                    suggestions = geocoding_service.search_addresses(address_search.strip(), limit=10)

                    if suggestions:
                        st.markdown("**Select Address:**")
                        suggestion_options = [f"📍 {s['address']}" for s in suggestions]
                        suggestion_index = st.selectbox(
                            "Choose from suggestions:",
                            options=range(len(suggestion_options)),
                            format_func=lambda x: suggestion_options[x] if x < len(suggestion_options) else "",
                            key=f"address_select_{st.session_state.get('form_reset_counter', 0)}"
                        )

                        if suggestion_index is not None and suggestion_index < len(suggestions):
                            selected_suggestion = suggestions[suggestion_index]
                            selected_address = selected_suggestion['address']

                            # Show map link for selected address
                            if selected_suggestion.get('lat') and selected_suggestion.get('lon'):
                                map_url = f"https://www.google.com/maps?q={selected_suggestion['lat']},{selected_suggestion['lon']}"
                                st.markdown(f'<a href="{map_url}" class="map-link" target="_blank">🗺️ View on Map</a>', unsafe_allow_html=True)
                    else:
                        st.info("No address suggestions found. You can enter manually below.")
                except Exception as e:
                    st.warning(f"Address lookup temporarily unavailable: {str(e)}")

            # Manual address input
            st.markdown("**Or enter address manually:**")
            address_input_key = f"address_input_{st.session_state.get('form_reset_counter', 0)}"
            manual_address = st.text_input(
                "Address *",
                value=selected_address if selected_address else "",
                placeholder="Enter complete address manually",
                key=address_input_key
            )

            # Use selected address or manual address
            final_address = selected_address if selected_address else manual_address

            # Show map preview for final address
            if final_address and len(final_address.strip()) >= 10:
                try:
                    address_details = geocoding_service.get_address_details(final_address.strip())
                    if address_details:
                        st.markdown("**📍 Location Preview:**")
                        st.markdown(f'<div class="location-preview">', unsafe_allow_html=True)
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.info(f"Coordinates: {address_details['lat']:.6f}, {address_details['lon']:.6f}")
                        with col2:
                            st.markdown(f'<a href="{address_details["map_url"]}" class="map-link" target="_blank">🗺️ View on Map</a>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    pass  # Silently fail for map preview

            st.markdown("---")

            # Use a key to reset form after successful submission
            form_key = f"add_property_form_{st.session_state.get('form_reset_counter', 0)}"

            with st.form(form_key):
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input("Property Name *", placeholder="e.g., Downtown Apartment")
                    property_type = st.selectbox("Property Type *", [pt.value for pt in PropertyType])
                    purchase_price = st.number_input("Purchase Price *", min_value=0.0, format="%.2f")

                with col2:
                    purchase_date = st.date_input("Purchase Date *", value=date.today())
                    monthly_rent = st.number_input("Monthly Rent *", min_value=0.0, format="%.2f")
                    description = st.text_area("Description", placeholder="Additional details about the property")

                submitted = st.form_submit_button("Add Property", type="primary")

                if submitted:
                    # Get address from final_address (selected or manual)
                    if name and final_address and purchase_price and monthly_rent:
                        new_property = Property(
                            name=name,
                            address=final_address,
                            property_type=PropertyType(property_type),
                            purchase_price=purchase_price,
                            purchase_date=datetime.combine(purchase_date, datetime.min.time()),
                            monthly_rent=monthly_rent,
                            description=description if description else None
                        )

                        # Get user ID and organization ID for RLS compliance
                        user_id = None
                        organization_id = None
                        if st.session_state.user:
                            if hasattr(st.session_state.user, 'id'):
                                user_id = st.session_state.user.id
                            elif isinstance(st.session_state.user, dict):
                                user_id = st.session_state.user.get('id')

                        # Get selected organization
                        organization_id = st.session_state.get('selected_organization')

                        result = db.create_property(new_property, user_id, organization_id)
                        if result:
                            st.success(f"Property '{name}' added successfully!")
                            # Increment form reset counter to clear the form
                            st.session_state.form_reset_counter = st.session_state.get('form_reset_counter', 0) + 1
                            st.rerun()
                        else:
                            st.error("Failed to add property. Please try again.")
                    else:
                        st.error("Please fill in all required fields.")

        with tab3:
            # Managing Properties tab content
            st.info(f"Found {len([p for p in db.get_properties() if p.organization_id == selected_org_id])} properties for {org_name}")

            all_properties = db.get_properties()
            org_properties = [p for p in all_properties if p.organization_id == selected_org_id]

            if org_properties:
                # Filter and Sort Controls
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Select Property to Manage**")
                    property_filter = st.selectbox(
                        "Select Property",
                        ["All Properties"] + [f"{p.name}" for p in org_properties],
                        label_visibility="collapsed",
                        key="manage_property_filter"
                    )

                with col2:
                    st.markdown("**Filter by Type**")
                    type_filter = st.selectbox(
                        "Filter by Type",
                        ["All Types"] + list(set(p.property_type.title() for p in org_properties)),
                        label_visibility="collapsed",
                        key="manage_type_filter"
                    )

                with col3:
                    st.markdown("**Sort by**")
                    sort_by = st.selectbox(
                        "Sort by",
                        ["Name A-Z", "Name Z-A", "Monthly Rent (High to Low)", "Monthly Rent (Low to High)", "Purchase Price (High to Low)", "Purchase Price (Low to High)"],
                        label_visibility="collapsed",
                        key="manage_sort_by"
                    )

                # Apply filters
                filtered_properties = org_properties

                if property_filter != "All Properties":
                    filtered_properties = [p for p in filtered_properties if p.name == property_filter]

                if type_filter != "All Types":
                    filtered_properties = [p for p in filtered_properties if p.property_type.title() == type_filter]

                # Apply sorting
                if sort_by == "Name A-Z":
                    filtered_properties = sorted(filtered_properties, key=lambda x: x.name)
                elif sort_by == "Name Z-A":
                    filtered_properties = sorted(filtered_properties, key=lambda x: x.name, reverse=True)
                elif sort_by == "Monthly Rent (High to Low)":
                    filtered_properties = sorted(filtered_properties, key=lambda x: x.monthly_rent, reverse=True)
                elif sort_by == "Monthly Rent (Low to High)":
                    filtered_properties = sorted(filtered_properties, key=lambda x: x.monthly_rent)
                elif sort_by == "Purchase Price (High to Low)":
                    filtered_properties = sorted(filtered_properties, key=lambda x: x.purchase_price, reverse=True)
                elif sort_by == "Purchase Price (Low to High)":
                    filtered_properties = sorted(filtered_properties, key=lambda x: x.purchase_price)

                st.markdown("---")

                # Add ultra-compact styling CSS
                st.markdown("""
                    <style>
                    .stMarkdown p {
                        margin-bottom: 0 !important;
                        margin-top: 0.1rem !important;
                        line-height: 1.4 !important;
                    }
                    div[data-testid="column"] {
                        padding-top: 0 !important;
                        padding-bottom: 0 !important;
                    }
                    .element-container {
                        margin-bottom: 0 !important;
                    }
                    </style>
                """, unsafe_allow_html=True)

                # Display properties as cards with financial info
                for prop in filtered_properties:
                    # Get financial summary for each property
                    financial_summary = db.get_property_financial_summary(prop.id)

                    # Property card - ultra-compact design
                    st.markdown(f"<p style='margin: 0.3rem 0 0.1rem 0;'><strong>🏠 {prop.name}</strong></p>", unsafe_allow_html=True)

                    # First row: Address/Type on left, Monthly Rent/Purchase Price on right
                    info_col1, info_col2 = st.columns([1.5, 1.5])

                    with info_col1:
                        st.markdown(f"<p style='margin: 0;'><strong>Address:</strong> {prop.address}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin: 0;'><strong>Type:</strong> {prop.property_type.title()}</p>", unsafe_allow_html=True)

                    with info_col2:
                        rent_price_col1, rent_price_col2 = st.columns(2)
                        with rent_price_col1:
                            st.markdown("<p style='margin: 0;'><strong>Monthly Rent</strong></p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='margin: 0;'>${prop.monthly_rent:,.0f}</p>", unsafe_allow_html=True)
                        with rent_price_col2:
                            st.markdown("<p style='margin: 0;'><strong>Purchase Price</strong></p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='margin: 0;'>${prop.purchase_price:,.0f}</p>", unsafe_allow_html=True)

                    # Financial metrics in one row with ultra-compact spacing - 5 columns (4 metrics + profit indicator)
                    fin_col1, fin_col2, fin_col3, fin_col4, fin_col5 = st.columns([1, 1, 1, 1, 0.5])

                    # Determine profit/loss color based on net income
                    net_income = financial_summary['net_income']
                    indicator_color = '#28a745' if net_income >= 0 else '#dc3545'  # Green for profit, Red for loss
                    roi_value = financial_summary['roi']

                    with fin_col1:
                        st.markdown("<p style='margin: 0; line-height: 1.2;'><strong>Total Income</strong><br>${:,.0f}</p>".format(financial_summary['total_income']), unsafe_allow_html=True)
                    with fin_col2:
                        st.markdown("<p style='margin: 0; line-height: 1.2;'><strong>Total Expenses</strong><br>${:,.0f}</p>".format(financial_summary['total_expenses']), unsafe_allow_html=True)
                    with fin_col3:
                        st.markdown("<p style='margin: 0; line-height: 1.2;'><strong>Net Income</strong><br>${:,.0f}</p>".format(net_income), unsafe_allow_html=True)
                    with fin_col4:
                        st.markdown("<p style='margin: 0; line-height: 1.2;'><strong>ROI</strong><br>{:.1f}%</p>".format(roi_value), unsafe_allow_html=True)
                    with fin_col5:
                        # Mini Bar Chart - Income vs Expenses comparison
                        total_income = financial_summary['total_income']
                        total_expenses = financial_summary['total_expenses']

                        # Calculate percentages for bar widths (avoid division by zero)
                        total = total_income + total_expenses
                        if total > 0:
                            income_pct = (total_income / total) * 100
                            expense_pct = (total_expenses / total) * 100
                        else:
                            income_pct = 50
                            expense_pct = 50

                        # Determine overall status color
                        status_color = '#28a745' if net_income >= 0 else '#dc3545'

                        # Build HTML without comments
                        bar_html = f'''<div style="display: flex; flex-direction: column; justify-content: center; height: 100%; padding: 0.2rem;">
<div style="margin-bottom: 0.15rem;">
<div style="display: flex; align-items: center;">
<span style="font-size: 0.65rem; width: 25px; color: #28a745; font-weight: bold;">IN</span>
<div style="flex: 1; background: #e9ecef; border-radius: 3px; height: 12px; overflow: hidden;">
<div style="background: #28a745; height: 100%; width: {income_pct}%;"></div>
</div>
</div>
</div>
<div style="margin-bottom: 0.15rem;">
<div style="display: flex; align-items: center;">
<span style="font-size: 0.65rem; width: 25px; color: #dc3545; font-weight: bold;">EX</span>
<div style="flex: 1; background: #e9ecef; border-radius: 3px; height: 12px; overflow: hidden;">
<div style="background: #dc3545; height: 100%; width: {expense_pct}%;"></div>
</div>
</div>
</div>
<div style="text-align: center; margin-top: 0.1rem;">
<span style="background: {status_color}; color: white; padding: 0.1rem 0.3rem; border-radius: 3px; font-size: 0.7rem; font-weight: bold;">{roi_value:.1f}%</span>
</div>
</div>'''
                        st.markdown(bar_html, unsafe_allow_html=True)

                    # Action buttons - equal size
                    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 8])
                    with btn_col1:
                        if st.button(f"✏️ Edit", key=f"manage_edit_{prop.id}", use_container_width=True):
                            st.session_state[f'editing_{prop.id}'] = True
                            st.rerun()
                    with btn_col2:
                        if st.button(f"🗑️ Delete", key=f"manage_delete_{prop.id}", type="secondary", use_container_width=True):
                            if db.delete_property(prop.id):
                                st.success(f"Property '{prop.name}' deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete property.")

                    # Thin separator between properties
                    st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)

                    # Show edit form if editing
                    if st.session_state.get(f'editing_{prop.id}'):
                        with st.form(f"edit_form_{prop.id}"):
                            st.write("### Edit Property Details")
                            col1, col2 = st.columns(2)

                            with col1:
                                new_name = st.text_input("Property Name", value=prop.name)
                                new_type = st.selectbox("Property Type", [pt.value for pt in PropertyType],
                                                       index=[pt.value for pt in PropertyType].index(prop.property_type))
                                new_price = st.number_input("Purchase Price", value=float(prop.purchase_price), format="%.2f")

                            with col2:
                                new_rent = st.number_input("Monthly Rent", value=float(prop.monthly_rent), format="%.2f")
                                new_desc = st.text_area("Description", value=prop.description if prop.description else "")

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Save Changes", type="primary"):
                                    # Create updated property object (only include fields that exist in Property model)
                                    updated_property = Property(
                                        id=prop.id,
                                        name=new_name,
                                        address=prop.address,  # Address cannot be changed
                                        property_type=PropertyType(new_type),
                                        purchase_price=new_price,
                                        purchase_date=prop.purchase_date,  # Keep original purchase date
                                        monthly_rent=new_rent,
                                        description=new_desc if new_desc else None,
                                        organization_id=prop.organization_id if hasattr(prop, 'organization_id') else None,
                                        created_at=prop.created_at if hasattr(prop, 'created_at') else None,
                                        updated_at=prop.updated_at if hasattr(prop, 'updated_at') else None
                                    )

                                    # Update property in database
                                    if db.update_property(prop.id, updated_property):
                                        st.success("Property updated successfully!")
                                        st.session_state[f'editing_{prop.id}'] = False
                                        st.rerun()
                                    else:
                                        st.error("Failed to update property. Please try again.")
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state[f'editing_{prop.id}'] = False
                                    st.rerun()

                    st.divider()
            else:
                st.info(f"No properties to manage for {org_name}.")
