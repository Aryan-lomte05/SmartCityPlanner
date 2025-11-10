# frontend/streamlit_app.py

import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd
import json
import time

BACKEND_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(layout="wide", page_title="🚨 Smart City Emergency Manager — GODMODE++", 
                   page_icon="🚨")

st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF4B4B 0%, #FF8E53 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🚨 Smart City Emergency Manager — GODMODE++</div>', 
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">⚡ 70 km/h Emergency Routing | 🎬 Multi-Vehicle Animation | 📊 Real-Time Analytics</div>', 
            unsafe_allow_html=True)

if 'incidents' not in st.session_state:
    st.session_state['incidents'] = []
if 'units' not in st.session_state:
    st.session_state['units'] = []
if 'sim_result' not in st.session_state:
    st.session_state['sim_result'] = None
if 'plan_result' not in st.session_state:
    st.session_state['plan_result'] = None
if 'current_frame' not in st.session_state:
    st.session_state['current_frame'] = 0
if 'auto_play' not in st.session_state:
    st.session_state['auto_play'] = False
if 'clicked_location' not in st.session_state:
    st.session_state['clicked_location'] = None
if 'show_click_dialog' not in st.session_state:
    st.session_state['show_click_dialog'] = False

with st.sidebar:
    st.header("⚙️ Control Panel")
    
    if st.button("🔄 Reset Dashboard", use_container_width=True):
        st.session_state['incidents'] = []
        st.session_state['units'] = []
        st.session_state['sim_result'] = None
        st.session_state['plan_result'] = None
        st.session_state['current_frame'] = 0
        st.session_state['auto_play'] = False
        st.session_state['clicked_location'] = None
        st.session_state['show_click_dialog'] = False
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("🎬 Playback Settings")
    playback_speed = st.slider("⚡ Speed Multiplier", 1, 20, 5, 
                              help="Higher = faster animation")
    
    st.markdown("---")
    
    st.subheader("📍 Quick Add")
    
    with st.expander("➕ Add Unit"):
        unit_id = st.text_input("Unit ID", value=f"U{len(st.session_state['units'])+1}")
        unit_type = st.selectbox("Type", ["ambulance", "fire", "police", "civilian"], key="unit_type_select")
        unit_lat = st.number_input("Latitude", value=19.0760, format="%.6f", key="unit_lat")
        unit_lon = st.number_input("Longitude", value=72.8777, format="%.6f", key="unit_lon")
        
        if st.button("Add Unit", use_container_width=True):
            st.session_state['units'].append({
                'id': unit_id,
                'type': unit_type,
                'lat': unit_lat,
                'lon': unit_lon,
                'available': True,
                'capacity': 1
            })
            st.success(f"✅ Added {unit_type} {unit_id}")
            st.rerun()
    
    with st.expander("🚨 Add Incident"):
        inc_id = st.text_input("Incident ID", value=f"I{len(st.session_state['incidents'])+1}")
        inc_type = st.selectbox("Incident Type", ["medical", "fire", "accident", "crime", "other"], key="inc_type_select")
        inc_severity = st.slider("Severity", 1, 5, 3)
        inc_lat = st.number_input("Incident Lat", value=19.1197, format="%.6f", key="inc_lat")
        inc_lon = st.number_input("Incident Lon", value=72.9053, format="%.6f", key="inc_lon")
        
        if st.button("Add Incident", use_container_width=True):
            st.session_state['incidents'].append({
                'id': inc_id,
                'type': inc_type,
                'severity': inc_severity,
                'lat': inc_lat,
                'lon': inc_lon
            })
            st.success(f"✅ Added {inc_type} incident {inc_id}")
            st.rerun()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Live Interactive Map (Click to Add)")
    
    base_map = folium.Map(location=[19.0760, 72.8777], zoom_start=12, 
                          tiles='OpenStreetMap')
    
    icon_config = {
        'ambulance': {'icon': '🚑', 'color': 'red'},
        'fire': {'icon': '🚒', 'color': 'orange'},
        'police': {'icon': '🚓', 'color': 'blue'},
        'civilian': {'icon': '👤', 'color': 'gray'}
    }
    
    incident_icons = {
        'medical': '🏥',
        'fire': '🔥',
        'accident': '💥',
        'crime': '⚠️',
        'other': '❓'
    }
    
    for unit in st.session_state['units']:
        icon_data = icon_config.get(unit['type'], {'icon': '🚗', 'color': 'gray'})
        icon_html = f'<div style="font-size: 28pt; text-align: center;">{icon_data["icon"]}</div>'
        
        folium.Marker(
            location=[unit['lat'], unit['lon']],
            icon=folium.DivIcon(html=icon_html),
            tooltip=f"<b>{unit['id']}</b><br>Type: {unit['type']}<br>Status: {'Available' if unit.get('available') else 'Busy'}",
            popup=f"{unit['id']} ({unit['type']})"
        ).add_to(base_map)
    
    for inc in st.session_state['incidents']:
        icon_symbol = incident_icons.get(inc['type'], '❓')
        icon_html = f'<div style="font-size: 28pt; text-align: center; filter: drop-shadow(0 0 3px rgba(255,0,0,0.8));">{icon_symbol}</div>'
        
        folium.Marker(
            location=[inc['lat'], inc['lon']],
            icon=folium.DivIcon(html=icon_html),
            tooltip=f"<b>INCIDENT: {inc['id']}</b><br>Type: {inc['type']}<br>Severity: {inc['severity']}/5",
            popup=f"Incident {inc['id']}"
        ).add_to(base_map)
    
    map_data = st_folium(base_map, width=900, height=500, returned_objects=["last_clicked"])
    
    if map_data and map_data.get("last_clicked"):
        click_lat = map_data["last_clicked"]["lat"]
        click_lon = map_data["last_clicked"]["lng"]
        
        st.session_state['clicked_location'] = {
            'lat': round(click_lat, 6),
            'lon': round(click_lon, 6)
        }
        st.session_state['show_click_dialog'] = True
    
    if st.session_state['show_click_dialog'] and st.session_state['clicked_location']:
        loc = st.session_state['clicked_location']
        
        st.markdown("---")
        st.info(f"📍 Clicked: ({loc['lat']}, {loc['lon']})")
        
        dialog_col1, dialog_col2, dialog_col3 = st.columns(3)
        
        with dialog_col1:
            if st.button("🚑 Add Unit Here", use_container_width=True):
                st.session_state['show_click_dialog'] = False
                st.session_state['units'].append({
                    'id': f"U{len(st.session_state['units'])+1}",
                    'type': 'ambulance',
                    'lat': loc['lat'],
                    'lon': loc['lon'],
                    'available': True,
                    'capacity': 1
                })
                st.success(f"✅ Added ambulance at ({loc['lat']}, {loc['lon']})")
                st.rerun()
        
        with dialog_col2:
            if st.button("🚒 Add Fire Here", use_container_width=True):
                st.session_state['show_click_dialog'] = False
                st.session_state['units'].append({
                    'id': f"U{len(st.session_state['units'])+1}",
                    'type': 'fire',
                    'lat': loc['lat'],
                    'lon': loc['lon'],
                    'available': True,
                    'capacity': 1
                })
                st.success(f"✅ Added fire unit at ({loc['lat']}, {loc['lon']})")
                st.rerun()
        
        with dialog_col3:
            if st.button("🚓 Add Police Here", use_container_width=True):
                st.session_state['show_click_dialog'] = False
                st.session_state['units'].append({
                    'id': f"U{len(st.session_state['units'])+1}",
                    'type': 'police',
                    'lat': loc['lat'],
                    'lon': loc['lon'],
                    'available': True,
                    'capacity': 1
                })
                st.success(f"✅ Added police at ({loc['lat']}, {loc['lon']})")
                st.rerun()
        
        incident_col1, incident_col2, incident_col3 = st.columns(3)
        
        with incident_col1:
            if st.button("🏥 Add Medical Here", use_container_width=True):
                st.session_state['show_click_dialog'] = False
                st.session_state['incidents'].append({
                    'id': f"I{len(st.session_state['incidents'])+1}",
                    'type': 'medical',
                    'severity': 3,
                    'lat': loc['lat'],
                    'lon': loc['lon']
                })
                st.success(f"✅ Added medical incident at ({loc['lat']}, {loc['lon']})")
                st.rerun()
        
        with incident_col2:
            if st.button("🔥 Add Fire Incident Here", use_container_width=True):
                st.session_state['show_click_dialog'] = False
                st.session_state['incidents'].append({
                    'id': f"I{len(st.session_state['incidents'])+1}",
                    'type': 'fire',
                    'severity': 4,
                    'lat': loc['lat'],
                    'lon': loc['lon']
                })
                st.success(f"✅ Added fire incident at ({loc['lat']}, {loc['lon']})")
                st.rerun()
        
        with incident_col3:
            if st.button("⚠️ Add Crime Here", use_container_width=True):
                st.session_state['show_click_dialog'] = False
                st.session_state['incidents'].append({
                    'id': f"I{len(st.session_state['incidents'])+1}",
                    'type': 'crime',
                    'severity': 2,
                    'lat': loc['lat'],
                    'lon': loc['lon']
                })
                st.success(f"✅ Added crime incident at ({loc['lat']}, {loc['lon']})")
                st.rerun()
        
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state['show_click_dialog'] = False
            st.rerun()

with col2:
    st.subheader("📊 Dashboard Metrics")
    
    met1, met2 = st.columns(2)
    with met1:
        st.metric("Active Units", len(st.session_state['units']))
    with met2:
        st.metric("Incidents", len(st.session_state['incidents']))
    
    # 🔥 DEBUG INFO SECTION
    if st.session_state['incidents']:
        with st.expander("🐛 Debug: Current Incidents"):
            for inc in st.session_state['incidents']:
                st.write(f"**{inc['id']}**: Type=`{inc['type']}`, Severity={inc['severity']}, Loc=({inc['lat']:.4f}, {inc['lon']:.4f})")
    
    if st.session_state['units']:
        with st.expander("🐛 Debug: Current Units"):
            for unit in st.session_state['units']:
                st.write(f"**{unit['id']}**: Type=`{unit['type']}`, Loc=({unit['lat']:.4f}, {unit['lon']:.4f})")
    
    if st.button("🎯 Generate Deployment Plan", use_container_width=True, type="primary"):
        if not st.session_state['incidents'] or not st.session_state['units']:
            st.error("❌ Need both incidents and units!")
        else:
            with st.spinner("🔄 Computing optimal routes..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/plan",
                        json={
                            'incidents': st.session_state['incidents'],
                            'units': st.session_state['units']
                        },
                        timeout=60
                    )
                    st.session_state['plan_result'] = response.json()
                    st.success("✅ Plan generated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Planning failed: {e}")
    
    if st.button("▶️ Run Simulation", use_container_width=True):
        if st.session_state['plan_result']:
            with st.spinner("🎬 Simulating emergency response..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/simulate",
                        json={
                            'incidents': st.session_state['incidents'],
                            'units': st.session_state['units']
                        },
                        params={'interval': 1.0, 'steps': 10},
                        timeout=90
                    )
                    st.session_state['sim_result'] = response.json()
                    st.session_state['current_frame'] = 0
                    st.success("✅ Simulation complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Simulation failed: {e}")
        else:
            st.warning("⚠️ Generate plan first!")

if st.session_state['plan_result']:
    st.markdown("---")
    st.subheader("📋 Deployment Plan Results")
    
    plan_data = st.session_state['plan_result']
    suggestions = plan_data.get('suggestions', {})
    route_details = plan_data.get('route_details', {})
    
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.metric("✅ Assigned", suggestions.get('assigned', 0))
    with mcol2:
        unassigned = suggestions.get('unassigned', 0)
        st.metric("⚠️ Unassigned", unassigned, 
                 delta=f"-{unassigned}" if unassigned > 0 else "All clear",
                 delta_color="inverse")
    with mcol3:
        avg_eta_min = suggestions.get('avg_eta_seconds', 0) / 60
        st.metric("⏱️ Avg ETA", f"{avg_eta_min:.1f} min")
    with mcol4:
        st.metric("🚗 Utilization", suggestions.get('unit_utilization', 'N/A'))
    
    if route_details:
        st.markdown("### 🛣️ Route Details")
        
        route_df = pd.DataFrame([
            {
                'Incident': inc_id,
                'Unit': details['unit_id'],
                'Type': details['unit_type'],
                'Distance (km)': details['distance_km'],
                'ETA (min)': details['eta_minutes'],
                'Segments': details['num_segments'],
                'Match': details.get('type_match', '—')
            }
            for inc_id, details in route_details.items()
        ])
        
        st.dataframe(route_df, use_container_width=True, hide_index=True)
        
        type_matches = suggestions.get('type_matches', 0)
        fallback_matches = suggestions.get('fallback_matches', 0)
        
        if type_matches > 0 or fallback_matches > 0:
            st.info(f"✓ **{type_matches}** optimal type matches | ⚠️ **{fallback_matches}** fallback assignments")

if st.session_state['sim_result']:
    st.markdown("---")
    st.subheader("🎬 Multi-Vehicle Playback Animation")
    
    events = st.session_state['sim_result'].get('events', [])
    if events:
        latest_event = events[-1]
        sim_data = latest_event.get('simulation_data', {})
        timeline = sim_data.get('timeline', [])
        max_frames = sim_data.get('max_frames', 0)
        
        if max_frames > 0:
            col_play, col_reset = st.columns([4, 1])
            with col_play:
                auto_play = st.checkbox("▶️ Auto-Play", value=st.session_state['auto_play'], key='autoplay_check')
                st.session_state['auto_play'] = auto_play
            with col_reset:
                if st.button("🔄 Reset", key='reset_animation'):
                    st.session_state['current_frame'] = 0
                    st.session_state['auto_play'] = False
                    st.rerun()
            
            # 🔥 FIXED AUTO-PLAY LOGIC
            if auto_play:
                if st.session_state['current_frame'] < max_frames - 1:
                    st.session_state['current_frame'] += min(playback_speed, max_frames - 1 - st.session_state['current_frame'])
                    time.sleep(0.15)
                    st.rerun()
                else:
                    st.session_state['current_frame'] = 0
                    time.sleep(0.5)
                    st.rerun()
            
            frame_idx = st.slider("🎞️ Playback Frame", 0, max_frames-1, 
                                 st.session_state['current_frame'], 
                                 key='playback_slider')
            st.session_state['current_frame'] = frame_idx
            
            color_scheme = {
                'ambulance': '#FF1744',
                'fire': '#FF6F00',
                'police': '#2979FF',
                'civilian': '#9E9E9E'
            }
            
            anim_map = folium.Map(location=[19.0760, 72.8877], zoom_start=12, 
                                 tiles='CartoDB positron')
            
            for unit_track in timeline:
                positions = unit_track['positions']
                unit_id = unit_track['unit_id']
                unit_type = unit_track['unit_type']
                path = unit_track['path']
                
                route_color = color_scheme.get(unit_type, '#9E9E9E')
                
                if path and len(path) > 1:
                    if frame_idx < len(positions):
                        path_progress_idx = int((frame_idx / len(positions)) * len(path))
                        
                        completed_path = path[:max(1, path_progress_idx + 1)]
                        if len(completed_path) > 1:
                            folium.PolyLine(
                                completed_path,
                                color=route_color,
                                weight=8,
                                opacity=0.9,
                                popup=f"{unit_id} - Completed"
                            ).add_to(anim_map)
                        
                        remaining_path = path[path_progress_idx:]
                        if len(remaining_path) > 1:
                            folium.PolyLine(
                                remaining_path,
                                color=route_color,
                                weight=6,
                                opacity=0.4,
                                dash_array='10, 5',
                                popup=f"{unit_id} - Remaining"
                            ).add_to(anim_map)
                    else:
                        folium.PolyLine(
                            path,
                            color=route_color,
                            weight=8,
                            opacity=0.9
                        ).add_to(anim_map)
                
                if frame_idx < len(positions):
                    pos = positions[frame_idx]
                    icon_symbol = icon_config.get(unit_type, {}).get('icon', '🚗')
                    
                    progress_html = f'''
                    <div style="position: relative; text-align: center;">
                        <div style="font-size: 32pt; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));">
                            {icon_symbol}
                        </div>
                        <div style="
                            position: absolute;
                            top: -5px;
                            right: -10px;
                            background: {route_color};
                            color: white;
                            font-size: 11pt;
                            font-weight: bold;
                            padding: 4px 8px;
                            border-radius: 12px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.4);
                        ">
                            {pos['progress']:.0f}%
                        </div>
                    </div>
                    '''
                    
                    folium.Marker(
                        location=[pos['lat'], pos['lon']],
                        icon=folium.DivIcon(html=progress_html),
                        tooltip=f"<b>{unit_id}</b><br>Type: {unit_type}<br>ETA: {pos['remaining_time']:.0f}s<br>Progress: {pos['progress']:.1f}%"
                    ).add_to(anim_map)
                
                start_pos = unit_track['start_pos']
                start_icon_html = f'<div style="font-size: 20pt; opacity: 0.5;">{icon_config.get(unit_type, {}).get("icon", "🚗")}</div>'
                folium.Marker(
                    location=[start_pos['lat'], start_pos['lon']],
                    icon=folium.DivIcon(html=start_icon_html),
                    tooltip=f"🏁 {unit_id} Start"
                ).add_to(anim_map)
                
                end_pos = unit_track['end_pos']
                folium.Marker(
                    location=[end_pos['lat'], end_pos['lon']],
                    icon=folium.Icon(color='red', icon='flag', prefix='fa'),
                    tooltip=f"🎯 Destination: {unit_track['incident_id']}"
                ).add_to(anim_map)
            
            st_folium(anim_map, width=1400, height=650, key=f'anim_map_{frame_idx}')
            
            progress_pct = (frame_idx / max_frames) * 100
            st.progress(progress_pct / 100)
            
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            with mcol1:
                st.metric("📍 Frame", f"{frame_idx+1}/{max_frames}")
            with mcol2:
                st.metric("📊 Progress", f"{progress_pct:.1f}%")
            with mcol3:
                avg_remaining = sum(
                    t['positions'][min(frame_idx, len(t['positions'])-1)]['remaining_time']
                    for t in timeline
                ) / len(timeline)
                st.metric("⏱️ Avg ETA Remaining", f"{avg_remaining:.0f}s")
            with mcol4:
                active_units = sum(1 for t in timeline if frame_idx < len(t['positions']))
                st.metric("🚗 Active Units", f"{active_units}/{len(timeline)}")
