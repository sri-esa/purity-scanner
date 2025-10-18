// backend/src/routes/upload.js
import express from 'express';
import multer from 'multer';
import { analyzeSpectrum } from '../services/mlservice.js';

const router = express.Router();

// Configure multer for file uploads (memory storage)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB limit
  },
  fileFilter: (req, file, cb) => {
    // Accept CSV and JSON files
    if (file.mimetype === 'text/csv' || 
        file.mimetype === 'application/json' ||
        file.originalname.toLowerCase().endsWith('.csv') ||
        file.originalname.toLowerCase().endsWith('.json')) {
      cb(null, true);
    } else {
      cb(new Error('Only CSV and JSON files are allowed'), false);
    }
  }
});

/**
 * Parse CSV content to extract spectrum data
 */
function parseCSV(content) {
  const lines = content.split('\n').filter(line => line.trim());
  const values = [];
  
  for (const line of lines) {
    const value = parseFloat(line.trim());
    if (!isNaN(value)) {
      values.push(value);
    }
  }
  
  return values;
}

/**
 * Parse JSON content to extract spectrum data
 */
function parseJSON(content) {
  try {
    const data = JSON.parse(content);
    
    // Handle different JSON formats
    if (Array.isArray(data)) {
      return data.map(v => typeof v === 'number' ? v : parseFloat(v)).filter(v => !isNaN(v));
    } else if (data.spectrum && Array.isArray(data.spectrum)) {
      return data.spectrum.map(v => typeof v === 'number' ? v : parseFloat(v)).filter(v => !isNaN(v));
    } else if (data.values && Array.isArray(data.values)) {
      return data.values.map(v => typeof v === 'number' ? v : parseFloat(v)).filter(v => !isNaN(v));
    } else if (data.intensities && Array.isArray(data.intensities)) {
      return data.intensities.map(v => typeof v === 'number' ? v : parseFloat(v)).filter(v => !isNaN(v));
    }
    
    return [];
  } catch (e) {
    throw new Error('Invalid JSON format');
  }
}

/**
 * Generate wavelength array for spectrum data
 */
function generateWavelengths(intensityCount, minWavelength = 400, maxWavelength = 1300) {
  const wavelengths = [];
  const step = (maxWavelength - minWavelength) / (intensityCount - 1);
  
  for (let i = 0; i < intensityCount; i++) {
    wavelengths.push(minWavelength + (i * step));
  }
  
  return wavelengths;
}

/**
 * POST /api/upload/analyze
 * Upload and analyze spectrum file
 */
router.post('/analyze', upload.single('spectrum'), async (req, res, next) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No file uploaded'
      });
    }

    const fileContent = req.file.buffer.toString('utf8');
    const fileName = req.file.originalname.toLowerCase();
    let intensities = [];

    // Parse file based on extension
    if (fileName.endsWith('.csv')) {
      intensities = parseCSV(fileContent);
    } else if (fileName.endsWith('.json')) {
      intensities = parseJSON(fileContent);
    } else {
      return res.status(400).json({
        success: false,
        error: 'Unsupported file format. Only CSV and JSON files are allowed.'
      });
    }

    // Validate parsed data
    if (intensities.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Could not parse spectrum data. Please ensure file contains valid numeric values.'
      });
    }

    if (intensities.length < 50) {
      return res.status(400).json({
        success: false,
        error: 'Spectrum data too short. Minimum 50 data points required.'
      });
    }

    // Generate corresponding wavelengths
    const wavelengths = generateWavelengths(intensities.length);

    // Call ML service for analysis
    const result = await analyzeSpectrum({ wavelengths, intensities });

    // Return results
    res.json({
      success: true,
      data: {
        fileName: req.file.originalname,
        dataPoints: intensities.length,
        purity: result.purity_score,
        confidence: result.confidence,
        contaminants: result.contaminants || [],
        model: result.model,
        processingTime: Date.now() - req.startTime
      }
    });

  } catch (error) {
    console.error('File upload analysis error:', error);
    
    if (error.message.includes('File too large')) {
      return res.status(413).json({
        success: false,
        error: 'File size too large. Maximum size is 5MB.'
      });
    }
    
    next(error);
  }
});

/**
 * POST /api/upload/validate
 * Validate spectrum file without analysis
 */
router.post('/validate', upload.single('spectrum'), async (req, res, next) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No file uploaded'
      });
    }

    const fileContent = req.file.buffer.toString('utf8');
    const fileName = req.file.originalname.toLowerCase();
    let intensities = [];

    // Parse file based on extension
    if (fileName.endsWith('.csv')) {
      intensities = parseCSV(fileContent);
    } else if (fileName.endsWith('.json')) {
      intensities = parseJSON(fileContent);
    } else {
      return res.status(400).json({
        success: false,
        error: 'Unsupported file format'
      });
    }

    // Return validation results
    res.json({
      success: true,
      data: {
        fileName: req.file.originalname,
        fileSize: req.file.size,
        dataPoints: intensities.length,
        valid: intensities.length >= 50,
        preview: intensities.slice(0, 10) // First 10 values for preview
      }
    });

  } catch (error) {
    console.error('File validation error:', error);
    next(error);
  }
});

// Error handler for multer
router.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(413).json({
        success: false,
        error: 'File too large. Maximum size is 5MB.'
      });
    }
  }
  
  res.status(400).json({
    success: false,
    error: error.message || 'File upload error'
  });
});

export default router;
