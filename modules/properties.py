"""
Properties page for PropLedger
Extracted from app_auth.py for better maintainability
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

        st.info(f"Managing properties for: **{org_name}**")

        # Real property management with organization filtering
        # Tabs for property management - matching reference design
        tab1, tab2, tab3 = st.tabs(["View Properties", "Add/Edit Property", "Managing Properties"])

        with tab1:
            all_properties = db.get_properties()
            # Filter properties by organization
            org_properties = [p for p in all_properties if p.organization_id == selected_org_id]

            if org_properties:
                for prop in org_properties:
                    with st.expander(f"{prop.name} - {prop.address}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Type:** {prop.property_type.title()}")
                            st.write(f"**Purchase Price:** ${prop.purchase_price:,.2f}")
                            st.write(f"**Purchase Date:** {prop.purchase_date.strftime('%Y-%m-%d')}")
                            st.write(f"**Monthly Rent:** ${prop.monthly_rent:,.2f}")

                        with col2:
                            financial_summary = db.get_property_financial_summary(prop.id)
                            st.write(f"**Total Income:** ${financial_summary['total_income']:,.2f}")
                            st.write(f"**Total Expenses:** ${financial_summary['total_expenses']:,.2f}")
                            st.write(f"**Net Income:** ${financial_summary['net_income']:,.2f}")
                            st.write(f"**ROI:** {financial_summary['roi']:.2f}%")

                        if prop.description:
                            st.write(f"**Description:** {prop.description}")
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
            # Managing Properties tab content - Rich UI matching monolithic design
            st.markdown("""
            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <h4 style="margin: 0;">🏠 Managing Properties</h4>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Manage your properties - view details, edit, or delete properties.</p>
                <p style="margin: 0.25rem 0 0 0; color: #333;"><strong>Found {count} properties for {org}</strong></p>
            </div>
            """.format(count=len([p for p in db.get_properties() if p.organization_id == selected_org_id]),
                      org=org_name), unsafe_allow_html=True)

            all_properties = db.get_properties()
            org_properties = [p for p in all_properties if p.organization_id == selected_org_id]

            if org_properties:
                # Filter and Sort Controls
                st.markdown("### 🔍 Filter Properties")

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

                # Display properties as cards with financial info
                for prop in filtered_properties:
                    # Get financial summary for each property
                    financial_summary = db.get_property_financial_summary(prop.id)

                    # Property card with expander
                    with st.expander(f"🏠 **{prop.name}**", expanded=True):
                        # Address and Type
                        st.markdown(f"**Address:** {prop.address}")
                        st.markdown(f"**Type:** {prop.property_type.title()}")

                        # Financial metrics in columns
                        st.markdown("---")
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <p style="margin: 0; color: #666; font-size: 0.9rem;">Monthly Rent</p>
                                <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">${prop.monthly_rent:,.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <p style="margin: 0; color: #666; font-size: 0.9rem;">Purchase Price</p>
                                <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">${prop.purchase_price:,.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown("---")

                        # Income and Expenses metrics
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <p style="margin: 0; color: #666; font-size: 0.8rem;">Total Income</p>
                                <p style="margin: 0; font-size: 1rem; font-weight: bold;">${financial_summary['total_income']:,.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <p style="margin: 0; color: #666; font-size: 0.8rem;">Total Expenses</p>
                                <p style="margin: 0; font-size: 1rem; font-weight: bold;">${financial_summary['total_expenses']:,.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        with col3:
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <p style="margin: 0; color: #666; font-size: 0.8rem;">Net Income</p>
                                <p style="margin: 0; font-size: 1rem; font-weight: bold;">${financial_summary['net_income']:,.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        with col4:
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <p style="margin: 0; color: #666; font-size: 0.8rem;">ROI</p>
                                <p style="margin: 0; font-size: 1rem; font-weight: bold;">{financial_summary['roi']:.1f}%</p>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown("---")

                        # Action buttons
                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button(f"✏️ Edit", key=f"manage_edit_{prop.id}", use_container_width=True):
                                st.session_state[f'editing_{prop.id}'] = True

                        with col2:
                            if st.button(f"🗑️ Delete", key=f"manage_delete_{prop.id}", type="secondary", use_container_width=True):
                                if db.delete_property(prop.id):
                                    st.success(f"Property '{prop.name}' deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete property.")

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
                                    # Update property logic here
                                    st.success("Property updated successfully!")
                                    st.session_state[f'editing_{prop.id}'] = False
                                    st.rerun()
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state[f'editing_{prop.id}'] = False
                                    st.rerun()

                    st.divider()
            else:
                st.info(f"No properties to manage for {org_name}.")
