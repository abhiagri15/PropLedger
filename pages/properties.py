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

    st.markdown('<h1 class="main-header">🏠 Property Management</h1>', unsafe_allow_html=True)

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
        # Tabs for property management
        tab1, tab2 = st.tabs(["View Properties", "Add/Edit Property"])

        with tab1:
            properties = db.get_properties()
            # Filter properties by organization
            org_properties = [p for p in properties if p.organization_id == selected_org_id]

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
