#!/usr/bin/env python3
"""
Generate app.yaml from config.yaml for Payer Star Ratings

Usage:
    python generate_app_yaml.py                    # Uses default environment
    python generate_app_yaml.py dev                # Specific environment
    python generate_app_yaml.py staging
    python generate_app_yaml.py prod
"""

import yaml
import sys
from pathlib import Path


def load_config(environment: str = None) -> dict:
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"config.yaml not found at {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Determine environment
    if environment is None:
        environment = config.get('default_environment', 'dev')
    
    if environment not in config['environments']:
        available = ', '.join(config['environments'].keys())
        raise ValueError(
            f"Environment '{environment}' not found in config.yaml!\n"
            f"Available: {available}"
        )
    
    return config, environment


def generate_app_yaml(config: dict, environment: str) -> str:
    """Generate app.yaml content from config"""
    
    env_config = config['environments'][environment]
    common_config = config['common']
    
    # Extract host without https://
    workspace_host = env_config['workspace_host'].replace('https://', '').replace('http://', '')
    
    # Build app.yaml content
    app_yaml_content = f"""# ✅ CORRECT - Official Microsoft Pattern
# 🤖 AUTO-GENERATED from config.yaml - DO NOT EDIT DIRECTLY!
# Run: python generate_app_yaml.py {environment}

command: ['streamlit', 'run', 'app.py']

env:
  # Core Databricks connection
  - name: 'DATABRICKS_HOST'
    value: '{workspace_host}'
  - name: 'DATABRICKS_WAREHOUSE_ID'
    value: '{env_config['warehouse_id']}'
  
  # Unity Catalog configuration
  - name: 'CATALOG_NAME'
    value: '{env_config['catalog']}'
  - name: 'SCHEMA_NAME'
    value: '{env_config['schema']}'
  
  # Vector Search configuration
  - name: 'VECTOR_ENDPOINT'
    value: '{env_config['vector_endpoint']}'
  
  # LLM configuration
  - name: 'LLM_ENDPOINT'
    value: '{env_config['llm_endpoint']}'
  
  # Genie Space ID (for Performance Dashboard page)
  - name: 'GENIE_SPACE_ID'
    value: '{env_config.get('genie_space_id', '')}'
  
  # Setup Resources URLs (for Setup Resources page)
  - name: 'NOTEBOOKS_FOLDER_URL'
    value: '{env_config.get('notebooks_folder_url', '')}'
  - name: 'SETUP_JOB_URL'
    value: '{env_config.get('setup_job_url', '')}'
  
  # Environment identifier
  - name: 'ENVIRONMENT'
    value: '{environment}'
  
  # Embedding model for vector search
  - name: 'EMBEDDING_MODEL'
    value: '{common_config['embedding_model']}'
"""
    
    return app_yaml_content


def write_app_yaml(content: str, app_yaml_path: Path):
    """Write app.yaml to disk"""
    app_yaml_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(app_yaml_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Generated: {app_yaml_path}")


def main():
    """Main execution"""
    # Get environment from command line or use default
    environment = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        # Load config
        config, resolved_env = load_config(environment)
        
        print("=" * 70)
        print("🤖 GENERATING app.yaml FROM config.yaml")
        print("=" * 70)
        print(f"Environment: {resolved_env}")
        print(f"Catalog:     {config['environments'][resolved_env]['catalog']}")
        print(f"Schema:      {config['environments'][resolved_env]['schema']}")
        print(f"Warehouse:   {config['environments'][resolved_env]['warehouse_id']}")
        print(f"LLM:         {config['environments'][resolved_env]['llm_endpoint']}")
        print("=" * 70)
        
        # Generate app.yaml content
        app_yaml_content = generate_app_yaml(config, resolved_env)
        
        # Write to app/app.yaml
        app_yaml_path = Path(__file__).parent / "app" / "app.yaml"
        write_app_yaml(app_yaml_content, app_yaml_path)
        
        print("\n✅ SUCCESS!")
        print("\nNext steps:")
        print("  1. Review: cat app/app.yaml")
        print("  2. Deploy: databricks bundle deploy")
        print("  3. Or use: ./deploy_with_config.sh")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
