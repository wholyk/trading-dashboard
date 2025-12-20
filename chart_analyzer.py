"""
TradingView Chart Analyzer Module

This module provides functionality to analyze TradingView screenshots
and detect liquidity sweeps and Break of Structure (BOS) patterns.
"""

import hashlib
import logging
from datetime import datetime
from typing import Dict, Tuple, Optional
from io import BytesIO
import numpy as np
from PIL import Image
import cv2


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChartAnalyzer:
    """
    Analyzes TradingView screenshots to detect liquidity sweeps and BOS patterns.
    """
    
    def __init__(self):
        """Initialize the ChartAnalyzer."""
        self.analysis_log = []
    
    def calculate_image_hash(self, image_data: bytes) -> str:
        """
        Calculate SHA-256 hash of the screenshot.
        
        Args:
            image_data: Raw image data in bytes
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(image_data).hexdigest()
    
    def preprocess_image(self, image_data: bytes) -> Tuple[np.ndarray, Image.Image]:
        """
        Preprocess the image for analysis.
        
        Args:
            image_data: Raw image data in bytes
            
        Returns:
            Tuple of (OpenCV image array, PIL Image)
        """
        # Load image with PIL
        pil_image = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return cv_image, pil_image
    
    def detect_liquidity_sweep(self, cv_image: np.ndarray) -> Dict[str, float]:
        """
        Detect liquidity sweep patterns in the chart.
        
        A liquidity sweep typically involves:
        - Price moving beyond a key level (support/resistance)
        - Quick reversal back inside the range
        - Often appears as a wick or spike
        
        Args:
            cv_image: OpenCV image array
            
        Returns:
            Dictionary with detection metrics
        """
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Detect edges using Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find vertical lines (potential wicks/spikes)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, vertical_kernel)
        
        # Count potential wick patterns
        contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze contour characteristics
        wick_count = 0
        significant_wicks = 0
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter for thin, tall structures (wicks)
            if h > 20 and w < 10:
                wick_count += 1
                if h > 40:  # Significant wicks
                    significant_wicks += 1
        
        # Calculate liquidity sweep indicators
        total_pixels = gray.size
        edge_density = np.sum(edges > 0) / total_pixels if total_pixels > 0 else 0.0
        
        # Normalize scores
        wick_score = min(wick_count / 50.0, 1.0)  # Normalize to 0-1
        significant_wick_score = min(significant_wicks / 10.0, 1.0)
        edge_score = min(edge_density * 20, 1.0)
        
        return {
            'wick_count': wick_count,
            'significant_wicks': significant_wicks,
            'wick_score': wick_score,
            'significant_wick_score': significant_wick_score,
            'edge_density': edge_density,
            'edge_score': edge_score
        }
    
    def detect_bos(self, cv_image: np.ndarray) -> Dict[str, float]:
        """
        Detect Break of Structure (BOS) patterns in the chart.
        
        BOS typically involves:
        - Clear breaks above previous highs or below previous lows
        - Strong directional moves
        - Changes in market structure
        
        Args:
            cv_image: OpenCV image array
            
        Returns:
            Dictionary with detection metrics
        """
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Detect horizontal lines (potential support/resistance levels)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        edges = cv2.Canny(gray, 50, 150)
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, horizontal_kernel)
        
        # Find horizontal line patterns
        h_contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze for structure breaks
        horizontal_line_count = len(h_contours)
        
        # Detect strong directional moves using gradient analysis
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        
        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        avg_gradient = np.mean(gradient_magnitude)
        
        # Detect color changes (potential structure breaks shown in different colors)
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        
        # Look for green (bullish) and red (bearish) regions
        # Green range
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Red range
        lower_red1 = np.array([0, 40, 40])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 40, 40])
        upper_red2 = np.array([180, 255, 255])
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        # Calculate color presence
        total_pixels = gray.size
        green_presence = np.sum(green_mask > 0) / total_pixels if total_pixels > 0 else 0.0
        red_presence = np.sum(red_mask > 0) / total_pixels if total_pixels > 0 else 0.0
        color_contrast = abs(green_presence - red_presence)
        
        # Normalize scores
        structure_line_score = min(horizontal_line_count / 20.0, 1.0)
        gradient_score = min(avg_gradient / 50.0, 1.0)
        color_score = min(color_contrast * 10, 1.0)
        
        return {
            'horizontal_lines': horizontal_line_count,
            'avg_gradient': avg_gradient,
            'green_presence': green_presence,
            'red_presence': red_presence,
            'color_contrast': color_contrast,
            'structure_line_score': structure_line_score,
            'gradient_score': gradient_score,
            'color_score': color_score
        }
    
    def calculate_confidence_score(
        self,
        liquidity_metrics: Dict[str, float],
        bos_metrics: Dict[str, float]
    ) -> Tuple[float, float, float]:
        """
        Calculate overall confidence scores for detections.
        
        Args:
            liquidity_metrics: Metrics from liquidity sweep detection
            bos_metrics: Metrics from BOS detection
            
        Returns:
            Tuple of (liquidity_sweep_confidence, bos_confidence, overall_confidence)
        """
        # Calculate liquidity sweep confidence
        liquidity_confidence = (
            liquidity_metrics['wick_score'] * 0.4 +
            liquidity_metrics['significant_wick_score'] * 0.4 +
            liquidity_metrics['edge_score'] * 0.2
        )
        
        # Calculate BOS confidence
        bos_confidence = (
            bos_metrics['structure_line_score'] * 0.3 +
            bos_metrics['gradient_score'] * 0.4 +
            bos_metrics['color_score'] * 0.3
        )
        
        # Calculate overall confidence (both patterns present)
        overall_confidence = (liquidity_confidence + bos_confidence) / 2.0
        
        return liquidity_confidence, bos_confidence, overall_confidence
    
    def analyze_screenshot(self, image_data: bytes, filename: str = "unknown") -> Dict:
        """
        Main analysis function that processes a TradingView screenshot.
        
        Args:
            image_data: Raw image data in bytes
            filename: Optional filename for logging
            
        Returns:
            Dictionary containing analysis results
        """
        # Calculate hash
        image_hash = self.calculate_image_hash(image_data)
        
        # Preprocess image
        cv_image, pil_image = self.preprocess_image(image_data)
        
        # Detect patterns
        liquidity_metrics = self.detect_liquidity_sweep(cv_image)
        bos_metrics = self.detect_bos(cv_image)
        
        # Calculate confidence scores
        liquidity_confidence, bos_confidence, overall_confidence = \
            self.calculate_confidence_score(liquidity_metrics, bos_metrics)
        
        # Prepare results
        results = {
            'filename': filename,
            'image_hash': image_hash,
            'timestamp': datetime.now().isoformat(),
            'image_size': pil_image.size,
            'liquidity_sweep': {
                'confidence': round(liquidity_confidence, 3),
                'metrics': liquidity_metrics
            },
            'break_of_structure': {
                'confidence': round(bos_confidence, 3),
                'metrics': bos_metrics
            },
            'overall_confidence': round(overall_confidence, 3)
        }
        
        # Log the analysis
        self._log_analysis(results)
        
        return results
    
    def _log_analysis(self, results: Dict):
        """
        Log the analysis results.
        
        Args:
            results: Analysis results dictionary
        """
        log_entry = {
            'timestamp': results['timestamp'],
            'image_hash': results['image_hash'],
            'filename': results['filename'],
            'liquidity_sweep_confidence': results['liquidity_sweep']['confidence'],
            'bos_confidence': results['break_of_structure']['confidence'],
            'overall_confidence': results['overall_confidence']
        }
        
        self.analysis_log.append(log_entry)
        
        # Log to file/console
        logger.info(
            f"Analysis complete - Hash: {results['image_hash'][:16]}... | "
            f"Liquidity Sweep: {results['liquidity_sweep']['confidence']:.3f} | "
            f"BOS: {results['break_of_structure']['confidence']:.3f} | "
            f"Overall: {results['overall_confidence']:.3f}"
        )
    
    def get_analysis_log(self) -> list:
        """
        Get the complete analysis log.
        
        Returns:
            List of all analysis log entries
        """
        return self.analysis_log
    
    def clear_log(self):
        """Clear the analysis log."""
        self.analysis_log = []


def analyze_chart(image_data: bytes, filename: str = "unknown") -> Dict:
    """
    Convenience function to analyze a chart without creating an analyzer instance.
    
    Args:
        image_data: Raw image data in bytes
        filename: Optional filename for logging
        
    Returns:
        Dictionary containing analysis results
    """
    analyzer = ChartAnalyzer()
    return analyzer.analyze_screenshot(image_data, filename)
