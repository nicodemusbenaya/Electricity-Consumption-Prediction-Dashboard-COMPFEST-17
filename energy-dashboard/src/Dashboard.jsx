import { useState, useEffect, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { Zap, Thermometer, TrendingUp, TrendingDown, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <div className="label">{new Date(label).toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
        {payload.map((entry, index) => (
          <div key={index} className="intro" style={{ color: entry.color }}>
            <span>{entry.name}:</span>
            <span>{entry.value.toFixed(2)} {entry.name.includes('Suhu') ? '°C' : 'kWh'}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

const CLUSTERS = [
  { id: "cluster_1", name: "Jakarta Pusat" },
  { id: "cluster_2", name: "Jakarta Selatan" },
  { id: "cluster_3", name: "Jakarta Barat" },
  { id: "cluster_4", name: "Jakarta Timur" },
];

function Dashboard() {
  const [data, setData] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState('cluster_1');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    
    // Fetch live forecast from Python Backend
    fetch(`http://localhost:8005/api/forecast?cluster=${selectedCluster}`)
      .then(res => {
        if (!res.ok) throw new Error("Gagal mengambil data dari server");
        return res.json();
      })
      .then(jsonData => {
        if (jsonData.error) {
          throw new Error(jsonData.error);
        }
        setData(jsonData);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error loading data:", err);
        setError(err.message);
        setLoading(false);
      });
  }, [selectedCluster]);

  const kpis = useMemo(() => {
    if (data.length === 0) return { avgConsumption: 0, trend: 0, avgTemp: 0 };

    const totalConsumption = data.reduce((sum, item) => sum + item.electricity_consumption, 0);
    const avgConsumption = totalConsumption / data.length;

    const totalTemp = data.reduce((sum, item) => sum + item.temperature_2m_max, 0);
    const avgTemp = totalTemp / data.length;

    // Calculate trend: (last half avg - first half avg) / first half avg
    const half = Math.floor(data.length / 2);
    if (half > 0) {
      const firstHalf = data.slice(0, half).reduce((sum, item) => sum + item.electricity_consumption, 0) / half;
      const lastHalf = data.slice(-half).reduce((sum, item) => sum + item.electricity_consumption, 0) / half;
      const trend = ((lastHalf - firstHalf) / firstHalf) * 100;
      return { avgConsumption, trend, avgTemp };
    }

    return { avgConsumption, trend: 0, avgTemp };
  }, [data]);

  return (
    <div className="dashboard-container">
      
      {/* HEADER */}
      <header className="header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to="/" style={{ color: 'var(--text-main)', textDecoration: 'none' }}>
            <ArrowLeft size={28} />
          </Link>
          <h1>⚡ LIVE FORECAST (15 HARI)</h1>
        </div>
        <div className="controls">
          <label htmlFor="cluster-select" style={{ fontWeight: 700 }}>AREA:</label>
          <select 
            id="cluster-select"
            value={selectedCluster} 
            onChange={(e) => setSelectedCluster(e.target.value)}
          >
            {CLUSTERS.map(c => (
              <option key={c.id} value={c.id}>{c.name.toUpperCase()}</option>
            ))}
          </select>
        </div>
      </header>

      {error && (
        <div style={{ backgroundColor: 'var(--accent-pink)', padding: '1rem', border: '3px solid #1e1e1e', marginBottom: '1.5rem', fontWeight: 700 }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>MENGAMBIL DATA CUACA...</h1>
        </div>
      ) : (
        <>
          {/* KPI GRID */}
          <div className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-title"><Zap size={18} color="var(--accent-blue)" /> Rata-rata Konsumsi Harian</div>
              <div className="kpi-value">
                {kpis.avgConsumption.toFixed(1)} <span className="kpi-unit">kWh</span>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-title"><TrendingUp size={18} color="var(--accent-pink)" /> Tren Konsumsi (Periode Ini)</div>
              <div className="kpi-value" style={{ gap: '1rem' }}>
                {Math.abs(kpis.trend).toFixed(1)} <span className="kpi-unit">%</span>
                <div className={`trend-badge ${kpis.trend >= 0 ? 'trend-up' : 'trend-down'}`}>
                  {kpis.trend >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                  {kpis.trend >= 0 ? 'NAIK' : 'TURUN'}
                </div>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-title"><Thermometer size={18} color="var(--accent-green)" /> Rata-rata Suhu Maksimal</div>
              <div className="kpi-value">
                {kpis.avgTemp.toFixed(1)} <span className="kpi-unit">°C</span>
              </div>
            </div>
          </div>

          {/* MAIN CHART */}
          <div className="chart-container">
            <div className="chart-header">
              <h2 className="chart-title">Cuaca Live vs Prediksi Konsumsi Listrik</h2>
              <div className="legend-custom">
                <div className="legend-item">
                  <div className="legend-color" style={{ backgroundColor: 'var(--accent-blue)' }}></div>
                  <span>Konsumsi (kWh)</span>
                </div>
                <div className="legend-item">
                  <div className="legend-color" style={{ backgroundColor: 'var(--accent-pink)' }}></div>
                  <span>Suhu Max (°C)</span>
                </div>
              </div>
            </div>
            
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <LineChart
                  data={data}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" opacity={0.2} />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontWeight: 600, fontFamily: 'Space Grotesk' }} 
                    tickFormatter={(val) => {
                      const d = new Date(val);
                      return `${d.getDate()}/${d.getMonth()+1}`;
                    }}
                  />
                  <YAxis 
                    yAxisId="left" 
                    tick={{ fontWeight: 600, fontFamily: 'Space Grotesk' }} 
                  />
                  <YAxis 
                    yAxisId="right" 
                    orientation="right" 
                    tick={{ fontWeight: 600, fontFamily: 'Space Grotesk' }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line 
                    yAxisId="left"
                    type="monotone" 
                    dataKey="electricity_consumption" 
                    name="Konsumsi Listrik"
                    stroke="var(--accent-blue)" 
                    strokeWidth={4}
                    activeDot={{ r: 8, stroke: '#1e1e1e', strokeWidth: 2 }}
                    dot={false}
                  />
                  <Line 
                    yAxisId="right"
                    type="monotone" 
                    dataKey="temperature_2m_max" 
                    name="Suhu Max"
                    stroke="var(--accent-pink)" 
                    strokeWidth={4}
                    activeDot={{ r: 8, stroke: '#1e1e1e', strokeWidth: 2 }}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
      
    </div>
  );
}

export default Dashboard;
