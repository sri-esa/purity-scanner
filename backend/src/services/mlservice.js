import axios from 'axios';

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8001';

class MLService {
  /**
   * Analyze Raman spectrum for purity
   * @param {Array<number>} wavelengths - Array of wavelength values
   * @param {Array<number>} intensities - Array of intensity values
   * @returns {Promise<Object>} Analysis result with purity percentage
   */
  async analyzePurity(wavelengths, intensities) {
    try {
      const response = await axios.post(
        `${ML_SERVICE_URL}/api/ml/analyze`,
        {
          wavelengths,
          intensities
        },
        {
          timeout: 30000, // 30 second timeout
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('ML Service Error:', error.message);
      
      return {
        success: false,
        error: error.response?.data?.detail || 'ML service unavailable',
        statusCode: error.response?.status || 500
      };
    }
  }

  /**
   * Check ML service health
   * @returns {Promise<boolean>} Health status
   */
  async checkHealth() {
    try {
      const response = await axios.get(
        `${ML_SERVICE_URL}/api/ml/health`,
        { timeout: 5000 }
      );
      
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('ML Service health check failed:', error.message);
      return false;
    }
  }

  /**
   * Get available models
   * @returns {Promise<Array>} List of available models
   */
  async getAvailableModels() {
    try {
      const response = await axios.get(
        `${ML_SERVICE_URL}/api/ml/models`,
        { timeout: 5000 }
      );
      
      return response.data;
    } catch (error) {
      console.error('Failed to fetch models:', error.message);
      return [];
    }
  }
}

const mlServiceInstance = new MLService();

// Export both the class instance and the legacy function for backward compatibility
export const analyzeSpectrum = async ({ wavelengths, intensities }) => {
  const result = await mlServiceInstance.analyzePurity(wavelengths, intensities);
  
  if (result.success) {
    // Transform to match expected legacy format
    return {
      purity_score: result.data.purity_percentage,
      components: [
        { name: 'Primary Compound', percent: Math.round(result.data.purity_percentage) },
        { name: 'Impurities', percent: 100 - Math.round(result.data.purity_percentage) }
      ],
      model: result.data.model_used,
      confidence: result.data.confidence_score,
      contaminants: result.data.contaminants || []
    };
  } else {
    throw new Error(result.error || 'ML analysis failed');
  }
};

// Export the service instance as default
export default mlServiceInstance;

// Export for ES modules only (remove CommonJS exports)

