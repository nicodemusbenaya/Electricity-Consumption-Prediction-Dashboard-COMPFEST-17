import { Link } from 'react-router-dom';
import { Zap, Activity, CloudRain, ArrowRight } from 'lucide-react';

function LandingPage() {
  return (
    <div className="landing-container">
      <div className="landing-content">
        <div className="badge">COMPFEST-17 ACADEMY</div>
        
        <h1 className="hero-title">
          PREDIKSI KONSUMSI ENERGI <span className="highlight">MASA DEPAN</span>
        </h1>
        
        <p className="hero-subtitle">
          Platform intelijen cerdas yang menggabungkan kekuatan Machine Learning dengan live forecast cuaca untuk memprediksi kebutuhan listrik hingga 16 hari ke depan. Didesain khusus untuk efisiensi energi.
        </p>
        
        <div className="features">
          <div className="feature-item">
            <div className="feature-icon bg-yellow"><Zap size={24} /></div>
            <span>Prediksi Presisi Tinggi</span>
          </div>
          <div className="feature-item">
            <div className="feature-icon bg-blue"><CloudRain size={24} /></div>
            <span>Integrasi Live Weather</span>
          </div>
          <div className="feature-item">
            <div className="feature-icon bg-pink"><Activity size={24} /></div>
            <span>Dashboard Interaktif</span>
          </div>
        </div>

        <Link to="/dashboard" className="cta-button">
          MULAI ANALISIS <ArrowRight size={24} />
        </Link>
      </div>
      
      {/* Decorative Elements */}
      <div className="deco deco-1"></div>
      <div className="deco deco-2"></div>
      <div className="deco deco-3"></div>
    </div>
  );
}

export default LandingPage;
