#!/usr/bin/env python3
"""Simple script to run the AI Business Saathi app."""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app."""
    print("🚀 Starting AI Business Saathi...")
    print("📊 Retail Analytics Dashboard with AI-Powered Insights")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app/streamlit_app.py"):
        print("❌ Error: Please run this script from the project root directory")
        print("   Expected: Buildathon/run_app.py")
        print("   Current:", os.getcwd())
        sys.exit(1)
    
    # Check if sample data exists
    if not os.path.exists("sample_data/shop_sample.csv"):
        print("📝 Generating sample data...")
        try:
            subprocess.run([sys.executable, "scripts/generate_sample_data.py"], check=True)
            print("✅ Sample data generated successfully!")
        except subprocess.CalledProcessError:
            print("⚠️  Warning: Could not generate sample data. App will still work.")
    
    print("\n🌐 Starting Streamlit server...")
    print("   Local URL: http://localhost:8501")
    print("   Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app/streamlit_app.py",
            "--server.headless", "false",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
