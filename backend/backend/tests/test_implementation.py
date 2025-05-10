import requests
import os
from pathlib import Path

def test_health_check():
    """Test the health check endpoint."""
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    print("✅ Health check test passed")

def test_analyze_profile():
    """Test the profile analysis endpoint with sample files."""
    # Create test files directory if it doesn't exist
    test_files_dir = Path("test_files")
    test_files_dir.mkdir(exist_ok=True)
    
    # Create sample PDF files
    sample_transcript = test_files_dir / "sample_transcript.pdf"
    sample_resume = test_files_dir / "sample_resume.pdf"
    
    # Create simple PDF files for testing
    with open(sample_transcript, "w") as f:
        f.write("Sample transcript content")
    with open(sample_resume, "w") as f:
        f.write("Sample resume content")
    
    # Prepare the request
    files = {
        "transcript": ("sample_transcript.pdf", open(sample_transcript, "rb"), "application/pdf"),
        "resume": ("sample_resume.pdf", open(sample_resume, "rb"), "application/pdf")
    }
    data = {
        "desired_position": "Data Scientist",
        "github_profile": "https://github.com/testuser"
    }
    
    # Make the request
    response = requests.post(
        "http://localhost:8000/analyze-profile",
        files=files,
        data=data
    )
    
    # Clean up test files
    os.remove(sample_transcript)
    os.remove(sample_resume)
    os.rmdir(test_files_dir)
    
    # Check response
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert "data" in result
    assert "experience_level" in result["data"]
    assert "skills" in result["data"]
    assert "education" in result["data"]
    assert "recommendations" in result["data"]
    print("✅ Profile analysis test passed")

if __name__ == "__main__":
    print("Starting tests...")
    try:
        test_health_check()
        test_analyze_profile()
        print("\n🎉 All tests passed successfully!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}") 