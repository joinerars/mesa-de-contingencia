import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix leaflet default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:       "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:     "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

// Coordenadas por defecto: Facultad de Medicina UCV, Caracas
const DEFAULT_LAT = 10.4880;
const DEFAULT_LNG = -66.8792;

export default function MapaPicker({ value, onChange }) {
  const containerRef = useRef(null);
  const mapRef       = useRef(null);
  const markerRef    = useRef(null);
  const [address, setAddress] = useState(value?.address || "");
  const [searching, setSearching] = useState(false);

  // value = { lat, lng, address }
  const lat = value?.lat || DEFAULT_LAT;
  const lng = value?.lng || DEFAULT_LNG;

  useEffect(() => {
    if (mapRef.current) return; // ya inicializado
    const map = L.map(containerRef.current).setView([lat, lng], 15);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
    }).addTo(map);

    const marker = L.marker([lat, lng], { draggable: true }).addTo(map);
    markerRef.current = marker;
    mapRef.current = map;

    const onMove = async (e) => {
      const { lat, lng } = e.target.getLatLng();
      const addr = await reverseGeocode(lat, lng);
      setAddress(addr);
      onChange({ lat, lng, address: addr });
    };
    marker.on("dragend", onMove);

    map.on("click", async (e) => {
      const { lat, lng } = e.latlng;
      marker.setLatLng([lat, lng]);
      const addr = await reverseGeocode(lat, lng);
      setAddress(addr);
      onChange({ lat, lng, address: addr });
    });

    // Geocode inicial si ya hay valor
    if (!value?.address && value?.lat) {
      reverseGeocode(lat, lng).then(addr => {
        setAddress(addr);
        onChange({ lat, lng, address: addr });
      });
    }

    return () => { map.remove(); mapRef.current = null; };
  }, []);

  const buscar = async () => {
    if (!address.trim()) return;
    setSearching(true);
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`,
        { headers: { "Accept-Language": "es" } }
      );
      const data = await res.json();
      if (data.length > 0) {
        const { lat: la, lon: lo, display_name } = data[0];
        const nlat = parseFloat(la), nlng = parseFloat(lo);
        mapRef.current.setView([nlat, nlng], 16);
        markerRef.current.setLatLng([nlat, nlng]);
        setAddress(display_name);
        onChange({ lat: nlat, lng: nlng, address: display_name });
      }
    } finally { setSearching(false); }
  };

  return (
    <div className="mapa-picker">
      <div className="mapa-search">
        <input
          value={address}
          placeholder="Buscar dirección o hacer clic en el mapa..."
          onChange={e => setAddress(e.target.value)}
          onKeyDown={e => e.key === "Enter" && (e.preventDefault(), buscar())}
        />
        <button type="button" className="btn-secondary" onClick={buscar} disabled={searching}>
          {searching ? "..." : "🔍"}
        </button>
      </div>
      <div ref={containerRef} className="mapa-container" />
      {value?.lat && (
        <p className="mapa-coords">
          📍 {value.lat.toFixed(5)}, {value.lng.toFixed(5)}
        </p>
      )}
    </div>
  );
}

async function reverseGeocode(lat, lng) {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
      { headers: { "Accept-Language": "es" } }
    );
    const data = await res.json();
    return data.display_name || `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
  } catch {
    return `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
  }
}
