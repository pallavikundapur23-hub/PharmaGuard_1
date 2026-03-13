import React, { useState } from 'react'
import RiskBadge from './RiskBadge'
import VariantTable from './VariantTable'
import LLMExplanation from './LLMExplanation'
import DownloadButton from './DownloadButton'
import '../styles/components.css'

function ResultsDisplay({ results }) {
  const [selectedDrug, setSelectedDrug] = useState(null)

  if (!results || results.length === 0) {
    return <div className="results-empty">No results available</div>
  }

  const openPanel = (result) => {
    setSelectedDrug(result)
  }

  const closePanel = () => {
    setSelectedDrug(null)
  }

  const selectedResult = selectedDrug ? results.find(r => r.drug === selectedDrug.drug) : null

  return (
    <div className="results-display" id="analysis-results">
      <div className="results-header">
        <h2>Analysis Results</h2>
        <DownloadButton results={results} />
      </div>

      <div className="results-list">
        {results.map((result, index) => (
          <div 
            key={index} 
            className="result-card"
            onClick={() => openPanel(result)}
          >
            <div className="result-summary">
              <div className="result-title">
                <h3>{result.drug}</h3>
                {!result.error && (
                  <RiskBadge
                    riskLabel={result.risk_assessment?.risk_label}
                    severity={result.risk_assessment?.severity}
                  />
                )}
              </div>

              {!result.error && (
                <div className="result-meta">
                  <div className="meta-item">
                    <span className="label">Phenotype:</span>
                    <span className="value">{result.pharmacogenomic_profile?.phenotype}</span>
                  </div>
                  <div className="meta-item">
                    <span className="label">Gene:</span>
                    <span className="value">{result.pharmacogenomic_profile?.primary_gene}</span>
                  </div>
                  <div className="meta-item">
                    <span className="label">Confidence:</span>
                    <span className="value">{(result.risk_assessment?.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                </div>
              )}

              {result.error && (
                <div className="result-error">
                  <p>{result.error}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Dark Overlay */}
      {selectedResult && (
        <div className="panel-overlay" onClick={closePanel} />
      )}

      {/* Side Panel */}
      {selectedResult && !selectedResult.error && (
        <div className="details-panel">
          <div className="panel-header">
            <h2>{selectedResult.drug}</h2>
            <button className="close-button" onClick={closePanel}>
              ✕
            </button>
          </div>

          <div className="panel-content">
            <div className="detail-section">
              <h4>Risk Assessment</h4>
              <div className="risk-info">
                <div className="risk-info-item">
                  <span className="label">Risk Level:</span>
                  <RiskBadge
                    riskLabel={selectedResult.risk_assessment?.risk_label}
                    severity={selectedResult.risk_assessment?.severity}
                  />
                </div>
                <div className="risk-info-item">
                  <span className="label">Confidence Score:</span>
                  <span className="value">{(selectedResult.risk_assessment?.confidence_score * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h4>Pharmacogenomic Profile</h4>
              <div className="profile-info">
                <div className="profile-item">
                  <span className="label">Primary Gene:</span>
                  <span className="value">{selectedResult.pharmacogenomic_profile?.primary_gene}</span>
                </div>
                <div className="profile-item">
                  <span className="label">Phenotype:</span>
                  <span className="value">{selectedResult.pharmacogenomic_profile?.phenotype}</span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h4>Clinical Recommendation</h4>
              <div className="recommendation-box">
                <p><strong>Action:</strong> {selectedResult.clinical_recommendation?.action}</p>
                <p><strong>Dosing:</strong> {selectedResult.clinical_recommendation?.cpic_guideline}</p>
                <p><strong>Monitoring:</strong> {selectedResult.clinical_recommendation?.monitoring}</p>
              </div>
            </div>

            {selectedResult.pharmacogenomic_profile?.detected_variants?.length > 0 && (
              <div className="detail-section">
                <h4>Detected Variants</h4>
                <VariantTable variants={selectedResult.pharmacogenomic_profile.detected_variants} />
              </div>
            )}

            {selectedResult.llm_generated_explanation && (
              <div className="detail-section">
                <LLMExplanation explanation={selectedResult.llm_generated_explanation} />
              </div>
            )}

            <div className="detail-section">
              <h4>Quality Metrics</h4>
              <div className="metrics-grid">
                <div className="metric">
                  <span>VCF Parse Success:</span>
                  <strong>{selectedResult.quality_metrics?.vcf_parsing_success ? '✓' : '✗'}</strong>
                </div>
                <div className="metric">
                  <span>Variant Confidence:</span>
                  <strong>{(selectedResult.quality_metrics?.variant_confidence * 100).toFixed(0)}%</strong>
                </div>
                <div className="metric">
                  <span>Completeness:</span>
                  <strong>{(selectedResult.quality_metrics?.completeness * 100).toFixed(0)}%</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="results-timestamp">
        {results[0]?.timestamp && (
          <p>Analysis performed: {new Date(results[0].timestamp).toLocaleString()}</p>
        )}
      </div>
    </div>
  )
}

export default ResultsDisplay
