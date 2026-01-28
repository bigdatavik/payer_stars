"""
Payer Star Ratings - Shared Configuration Module

This module reads config.yaml and provides configuration to:
- Setup notebooks (interactive or DAB)
- Agent notebooks
- Streamlit app

ALL configuration comes from config.yaml - change once, works everywhere!

Usage in notebooks:
    from shared.config import get_config, print_config
    cfg = get_config()
    CATALOG = cfg.catalog
    SCHEMA = cfg.schema

Usage in Streamlit app:
    from shared.config import get_config
    cfg = get_config()
    connection = sql.connect(
        server_hostname=cfg.workspace_host,
        http_path=f"/sql/1.0/warehouses/{cfg.warehouse_id}",
        ...
    )
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class StarRatingsConfig:
    """Configuration container with all settings"""
    
    def __init__(self, env_config: Dict[str, Any], common_config: Dict[str, Any]):
        # Environment-specific settings
        self.workspace_host = env_config['workspace_host']
        self.profile = env_config['profile']
        self.catalog = env_config['catalog']
        self.schema = env_config['schema']
        self.warehouse_id = env_config['warehouse_id']
        self.vector_endpoint = env_config['vector_endpoint']
        self.llm_endpoint = env_config['llm_endpoint']
        self.app_name = env_config['app_name']
        self.genie_space_id = env_config.get('genie_space_id', '')  # Optional, empty string if not set
        
        # Common settings
        self.spark_version = common_config['spark_version']
        self.node_type = common_config['node_type']
        self.num_workers = common_config['num_workers']
        self.num_measures = common_config['num_measures']
        self.gap_rate = common_config['gap_rate']
        self.genie_display_name = common_config['genie_space_display_name']
        self.genie_description = common_config['genie_space_description']
        self.embedding_model = common_config['embedding_model']
        self.sync_type = common_config['sync_type']
        
        # Computed values (automatically derived)
        self.volume = "hedis_knowledge_docs"
        self.volume_path = f"/Volumes/{self.catalog}/{self.schema}/{self.volume}"
        self.measures_table = f"{self.catalog}.{self.schema}.measures_data"
        self.member_table = f"{self.catalog}.{self.schema}.member_enrollments"
        self.hedis_guidelines_kb = f"{self.catalog}.{self.schema}.hedis_guidelines_kb"
        self.hedis_guidelines_index = f"{self.catalog}.{self.schema}.hedis_guidelines_index"
        self.config_table = f"{self.catalog}.{self.schema}.config_genie"
        self.star_analysis = f"{self.catalog}.{self.schema}.star_analysis"
        self.predictions_table = f"{self.catalog}.{self.schema}.star_predictions"
    
    def __repr__(self):
        return f"StarRatingsConfig(env={self.catalog}, warehouse={self.warehouse_id})"


def get_config(environment: Optional[str] = None) -> StarRatingsConfig:
    """
    Load configuration from config.yaml
    
    Environment resolution priority:
    1. Parameter passed to function
    2. DAB widget 'environment' (if running in notebook via DAB)
    3. Environment variable STARS_ENV
    4. Default environment from config.yaml
    
    Args:
        environment: Environment name (dev/staging/prod). If None, auto-detects.
    
    Returns:
        StarRatingsConfig object with all settings
    
    Example:
        cfg = get_config()  # Auto-detects environment
        cfg = get_config('staging')  # Force staging environment
    """
    
    # Find config.yaml (search up directory tree)
    current_dir = Path(__file__).parent
    config_path = None
    
    for parent in [current_dir] + list(current_dir.parents):
        candidate = parent / "config.yaml"
        if candidate.exists():
            config_path = candidate
            break
    
    if not config_path:
        raise FileNotFoundError(
            "config.yaml not found! Expected in project root.\n"
            "Make sure config.yaml exists and you're running from correct directory."
        )
    
    # Load config.yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Determine environment
    if environment is None:
        # Try DAB widget (only works in Databricks notebooks)
        try:
            # Check if dbutils is available
            import builtins
            if hasattr(builtins, 'dbutils'):
                environment = dbutils.widgets.get("environment")  # type: ignore
                print(f"✅ Using environment from DAB widget: {environment}")
        except:
            pass
    
    if environment is None:
        # Try environment variable
        environment = os.getenv("STARS_ENV")
        if environment:
            print(f"✅ Using environment from STARS_ENV: {environment}")
    
    if environment is None:
        # Use default from config
        environment = config.get('default_environment', 'dev')
        print(f"✅ Using default environment: {environment}")
    
    # Validate environment exists
    if environment not in config['environments']:
        available = ', '.join(config['environments'].keys())
        raise ValueError(
            f"Environment '{environment}' not found in config.yaml!\n"
            f"Available environments: {available}"
        )
    
    # Create config object
    env_config = config['environments'][environment]
    common_config = config['common']
    
    return StarRatingsConfig(env_config, common_config)


def print_config(cfg: StarRatingsConfig):
    """Pretty-print configuration for debugging"""
    print("=" * 80)
    print("PAYER STAR RATINGS CONFIGURATION")
    print("=" * 80)
    print(f"Catalog:           {cfg.catalog}")
    print(f"Schema:            {cfg.schema}")
    print(f"Warehouse ID:      {cfg.warehouse_id}")
    print(f"Vector Endpoint:   {cfg.vector_endpoint}")
    print(f"LLM Endpoint:      {cfg.llm_endpoint}")
    print(f"App Name:          {cfg.app_name}")
    print(f"Measures Table:    {cfg.measures_table}")
    print(f"Member Table:      {cfg.member_table}")
    print(f"Vector Index:      {cfg.hedis_guidelines_index}")
    print(f"Volume Path:       {cfg.volume_path}")
    print("=" * 80)
