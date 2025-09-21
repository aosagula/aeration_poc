import requests
import json

def test_health_endpoint():
    try:
        response = requests.get('http://localhost:5000/pdf/health')
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_pdf_endpoint(pdf_file_path):
    try:
        with open(pdf_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:5000/pdf/process', files=files)

        print(f"PDF processing status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Total pages processed: {result['total_pages']}")
            print("Extracted text preview:")
            for page in result['extracted_text'][:2]:  # Show first 2 pages
                print(f"Page {page['page']}: {page['text'][:200]}...")
        else:
            print(f"Error: {response.json()}")

        return response.status_code == 200
    except Exception as e:
        print(f"PDF processing test failed: {e}")
        return False

def test_swagger_docs():
    try:
        response = requests.get('http://localhost:5000/docs/')
        print(f"Swagger docs status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Swagger docs test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing PDF processor endpoint...")

    if test_health_endpoint():
        print("✓ Health endpoint working")
    else:
        print("✗ Health endpoint failed")

    if test_swagger_docs():
        print("✓ Swagger documentation accessible")
    else:
        print("✗ Swagger documentation failed")

    print("\n📖 Access Swagger docs at: http://localhost:5000/docs/")

    # Uncomment to test with a real PDF file
    # if test_pdf_endpoint("sample.pdf"):
    #     print("✓ PDF processing endpoint working")
    # else:
    #     print("✗ PDF processing endpoint failed")