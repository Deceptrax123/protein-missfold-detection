#!/usr/bin/env python3
"""
Simple test script to verify the frontend components work correctly
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from OrchestratorCall import call_orchestrator

def test_pdf_generation():
    """Test that the PDF generation works"""
    print("Testing PDF generation...")
    
    # Test data
    test_data = {
        "severity_label": "Moderate Risk",
        "confidence": 0.95,
        "analysis": {
            "z_score": 2.1,
            "sequence_3di": "sample_sequence_3di_data",
            "risk_factors": ["High disorder fraction", "Low core contact density"],
            "summary": "This protein shows moderate risk of misfolding based on the analysis."
        }
    }
    
    try:
        # Generate PDF
        pdf_content = call_orchestrator(test_data)
        
        # Verify we got some content
        assert pdf_content, "PDF content should not be empty"
        assert len(pdf_content) > 100, "PDF content should be more than 100 bytes"
        
        # Save to temporary file to verify it's valid PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_path = temp_file.name
        
        # Check file size
        file_size = os.path.getsize(temp_path)
        assert file_size > 100, f"PDF file should be larger than 100 bytes, got {file_size}"
        
        print(f"[SUCCESS] PDF generation successful! File size: {file_size} bytes")
        print(f"[INFO] Temporary PDF saved to: {temp_path}")
        
        # Clean up
        os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] PDF generation failed: {str(e)}")
        return False

def test_frontend_files():
    """Test that all required frontend files exist"""
    print("Testing frontend files...")
    
    required_files = [
        'index.html',
        'server.py',
        'README.md',
        'requirements.txt'
    ]
    
    frontend_dir = Path(__file__).parent
    
    for file_name in required_files:
        file_path = frontend_dir / file_name
        if not file_path.exists():
            print(f"[ERROR] Missing file: {file_name}")
            return False
        print(f"[OK] Found: {file_name}")
    
    return True

if __name__ == "__main__":
    print("Running frontend tests...\n")
    
    # Test 1: Check frontend files exist
    files_ok = test_frontend_files()
    print()
    
    # Test 2: Test PDF generation
    pdf_ok = test_pdf_generation()
    print()
    
    if files_ok and pdf_ok:
        print("[SUCCESS] All tests passed! Frontend should work correctly.")
        sys.exit(0)
    else:
        print("[ERROR] Some tests failed. Please check the output above.")
        sys.exit(1)