// backend/src/services/mlservice.js

const MODEL_URL = process.env.ML_MODEL_URL; // e.g., http://raspberrypi:5000/analyze

export async function analyzeSpectrum({ wavelengths, intensities }) {
  if (!Array.isArray(wavelengths) || !Array.isArray(intensities) || wavelengths.length !== intensities.length) {
    throw new Error('Invalid spectrum: wavelengths/intensities must be arrays of equal length');
  }

  // Mock fallback if no model URL configured
  if (!MODEL_URL) {
    const score = Math.round((70 + Math.random() * 30) * 100) / 100;
    return {
      purity_score: score,
      components: [
        { name: 'Compound A', percent: Math.round(score) },
        { name: 'Impurities', percent: 100 - Math.round(score) }
      ],
      model: 'mock',
    };
  }

  const resp = await fetch(MODEL_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wavelengths, intensities })
  });
  if (!resp.ok) {
    throw new Error(`ML model error: ${resp.status} ${await resp.text()}`);
  }
  const data = await resp.json();
  return data; // expected: { purity_score: number, components: [{name, percent}, ...] }
}

