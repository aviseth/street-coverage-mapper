"""
Parallel processing utilities for improved performance.
"""
import multiprocessing as mp
from pathlib import Path
from typing import List, Dict, Optional
import logging
from ..data.walk_processor import parse_tcx_file
from .logging_config import setup_logging

logger = setup_logging()

def process_tcx_file_wrapper(file_path: str) -> Optional[Dict[str, any]]:
    """Wrapper function for parallel processing of TCX files."""
    try:
        return parse_tcx_file(file_path)
    except Exception as e:
        logger.error(f"Error in parallel processing of {file_path}: {e}")
        return None

def parallel_process_walk_files(directory: str, n_workers: Optional[int] = None) -> List[Dict[str, any]]:
    """Process walk files in parallel for improved performance."""
    tcx_files = list(Path(directory).glob('*.tcx'))
    
    if not tcx_files:
        return []
    
    # Determine number of workers
    if n_workers is None:
        n_workers = min(mp.cpu_count(), len(tcx_files))
    
    logger.info(f"Processing {len(tcx_files)} TCX files using {n_workers} workers")
    
    # Process files in parallel
    with mp.Pool(processes=n_workers) as pool:
        results = pool.map(process_tcx_file_wrapper, [str(f) for f in tcx_files])
    
    # Filter out None results
    walks = [r for r in results if r is not None]
    
    logger.info(f"Parallel processing completed: {len(walks)} valid walks found")
    
    return walks