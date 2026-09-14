import streamlit as st
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.title("🩺 Find Doctors Near You")
st.caption("Powered by LocationIQ")

LOCATIONIQ_KEY = st.secrets["LOCATIONIQ_KEY"]

location = st.text_input("Enter your area, locality, or city", placeholder="e.g. Rajendra Nagar, Bareilly")

if st.button("Search Nearby Doctors") and location:
    with st.spinner("Searching..."):
        try:
            geo_resp = requests.get(
                "https://us1.locationiq.com/v1/search",
                params={"key": LOCATIONIQ_KEY, "q": location, "format": "json", "limit": 1},
                timeout=10,
                verify=False
            )

            if geo_resp.status_code != 200 or not geo_resp.text.strip():
                st.error(f"Location service returned an error (status {geo_resp.status_code}). Try again shortly.")
                st.stop()

            geo_data = geo_resp.json()
            if not geo_data:
                st.error("Couldn't find that location. Try being more specific (e.g. 'Area, City').")
                st.stop()

            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]

            tags_to_search = ["hospital", "clinic", "doctors"]
            radii_to_try = [3000, 5000, 10000, 20000]
            results = []
            used_radius = None

            for radius in radii_to_try:
                combined = []
                for tag in tags_to_search:
                    nearby_resp = requests.get(
                        "https://us1.locationiq.com/v1/nearby",
                        params={
                            "key": LOCATIONIQ_KEY,
                            "lat": lat,
                            "lon": lon,
                            "tag": tag,
                            "radius": radius,
                            "format": "json",
                            "limit": 20
                        },
                        timeout=15,
                        verify=False
                    )
                    if nearby_resp.status_code == 200 and nearby_resp.text.strip():
                        data = nearby_resp.json()
                        if isinstance(data, list):
                            combined.extend(data)

                if combined:
                    seen = set()
                    unique_results = []
                    for place in combined:
                        pid = place.get("place_id")
                        if pid not in seen:
                            seen.add(pid)
                            unique_results.append(place)
                    results = unique_results
                    used_radius = radius
                    break

            if not results:
                st.warning("No doctors/clinics found nearby, even within 20km. Try a nearby larger town or city name.")
            else:
                km = used_radius / 1000
                st.success(f"Found {len(results)} nearby doctors/clinics within {km:.0f} km")
                for place in results:
                    name = place.get("name", place.get("display_name", "Unnamed clinic/hospital"))
                    address = place.get("display_name", "Address not listed")
                    place_lat = place.get("lat")
                    place_lon = place.get("lon")

                    with st.container():
                        st.markdown(f"### {name}")
                        st.write(f"📍 {address}")
                        if place_lat and place_lon:
                            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={place_lat},{place_lon}"
                            st.markdown(f"[🧭 Get Directions]({maps_url})")
                        st.divider()

        except requests.exceptions.Timeout:
            st.error("Search timed out. Try again.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

















































































































































































































































































































































































































































































































































































































            