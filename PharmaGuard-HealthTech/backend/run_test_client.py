import sys
import pathlib
import traceback

# Ensure project root (one level up) is on sys.path so 'backend' package can be imported
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app import create_app

from backend.services.vcf_parser import parse_vcf_file

# Create app and test client
app = create_app()
client = app.test_client()

# Load sample VCF
vcf_path = 'sample_data/sample.vcf'
with open(vcf_path, 'r') as f:
    vcf_content = f.read()

payload = {
    'vcf_file': vcf_content,
    'drugs': ['CODEINE']
}

try:
    resp = client.post('/api/analyze', json=payload)
    print('Status', resp.status_code)
    print('Data', resp.get_data(as_text=True))
except Exception as e:
    print('Exception during request:', e)
    traceback.print_exc()
