#!/usr/bin/env python3
"""
Compressed JSONL I/O utilities using zstandard for 90% space savings.
Streaming read/write for memory efficiency on large datasets.
"""

import zstandard as zstd
import orjson as json
from pathlib import Path
from typing import Iterator, Any, Iterable
import logging

logger = logging.getLogger(__name__)


def write_jsonl_zst(filepath: Path, data_iterable: Iterable[Any], compression_level: int = 3) -> None:
    """
    Write data to compressed JSONL file (.jsonl.zst) with streaming compression.

    Args:
        filepath: Output file path (will add .zst if not present)
        data_iterable: Iterable of objects to write as JSON lines
        compression_level: Zstandard compression level (1-22, default 3 for speed/size balance)
    """
    try:
        # Ensure .zst extension
        if not str(filepath).endswith('.zst'):
            filepath = Path(str(filepath) + '.zst')

        # Create parent directory if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "wb") as f:
            cctx = zstd.ZstdCompressor(level=compression_level)
            with cctx.stream_writer(f) as compressor:
                for item in data_iterable:
                    # Use orjson for 2-5x faster JSON encoding
                    line = json.dumps(item).decode('utf-8') + "\n"
                    compressor.write(line.encode("utf-8"))

        logger.info(f"Successfully wrote compressed JSONL to {filepath}")

    except Exception as e:
        logger.error(f"Error writing compressed JSONL to {filepath}: {e}")
        raise


def read_jsonl_zst(filepath: Path) -> Iterator[Any]:
    """
    Read data from compressed JSONL file (.jsonl.zst) with streaming decompression.

    Args:
        filepath: Input file path (.jsonl.zst)

    Yields:
        Parsed JSON objects from each line
    """
    try:
        with open(filepath, "rb") as f:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(f) as reader:
                buffer = ""
                while True:
                    # Read in chunks for memory efficiency
                    chunk = reader.read(8192)
                    if not chunk:
                        break

                    buffer += chunk.decode("utf-8")

                    # Process complete lines
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if line.strip():
                            try:
                                # Use orjson for 2-5x faster JSON parsing
                                yield json.loads(line.strip())
                            except json.JSONDecodeError as e:
                                logger.warning(f"Skipping invalid JSON line: {line[:100]}... Error: {e}")

                # Process final line if buffer has content
                if buffer.strip():
                    try:
                        yield json.loads(buffer.strip())
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping invalid JSON in final buffer: {buffer[:100]}... Error: {e}")

    except Exception as e:
        logger.error(f"Error reading compressed JSONL from {filepath}: {e}")
        raise


def append_jsonl_zst(filepath: Path, data_iterable: Iterable[Any], compression_level: int = 3) -> None:
    """
    Append data to existing compressed JSONL file or create new one.

    Args:
        filepath: Target file path (.jsonl.zst)
        data_iterable: Iterable of objects to append as JSON lines
        compression_level: Zstandard compression level (1-22, default 3)
    """
    try:
        # Ensure .zst extension
        if not str(filepath).endswith('.zst'):
            filepath = Path(str(filepath) + '.zst')

        # If file doesn't exist, just write normally
        if not filepath.exists():
            write_jsonl_zst(filepath, data_iterable, compression_level)
            return

        # Read existing data, append new data, and rewrite
        # Note: This isn't truly streaming append due to zstd format limitations
        # For high-frequency appends, consider using uncompressed temporary files
        existing_data = list(read_jsonl_zst(filepath))

        # Combine existing and new data
        combined_data = existing_data + list(data_iterable)

        # Rewrite with combined data
        write_jsonl_zst(filepath, combined_data, compression_level)

        logger.info(f"Successfully appended to compressed JSONL {filepath}")

    except Exception as e:
        logger.error(f"Error appending to compressed JSONL {filepath}: {e}")
        raise


def get_compression_stats(original_filepath: Path, compressed_filepath: Path) -> dict:
    """
    Calculate compression statistics for reporting.

    Args:
        original_filepath: Path to uncompressed file
        compressed_filepath: Path to compressed file

    Returns:
        Dictionary with compression statistics
    """
    try:
        if not original_filepath.exists() or not compressed_filepath.exists():
            return {"error": "One or both files do not exist"}

        original_size = original_filepath.stat().st_size
        compressed_size = compressed_filepath.stat().st_size

        if original_size == 0:
            return {"error": "Original file is empty"}

        compression_ratio = compressed_size / original_size
        space_savings = (1 - compression_ratio) * 100

        return {
            "original_size_bytes": original_size,
            "compressed_size_bytes": compressed_size,
            "compression_ratio": compression_ratio,
            "space_savings_percent": space_savings,
            "size_reduction_factor": original_size / compressed_size if compressed_size > 0 else float('inf')
        }

    except Exception as e:
        logger.error(f"Error calculating compression stats: {e}")
        return {"error": str(e)}


def compress_existing_jsonl(input_filepath: Path, output_filepath: Path = None,
                          compression_level: int = 3, remove_original: bool = False) -> dict:
    """
    Compress an existing uncompressed JSONL file.

    Args:
        input_filepath: Path to uncompressed JSONL file
        output_filepath: Path for compressed output (default: input + .zst)
        compression_level: Zstandard compression level (1-22)
        remove_original: Whether to delete original file after compression

    Returns:
        Dictionary with compression statistics
    """
    try:
        if output_filepath is None:
            output_filepath = Path(str(input_filepath) + '.zst')

        # Read uncompressed JSONL and write compressed
        def read_uncompressed_jsonl():
            with open(input_filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            yield json.loads(line.strip())
                        except json.JSONDecodeError as e:
                            logger.warning(f"Skipping invalid JSON line: {line[:100]}... Error: {e}")

        # Write compressed version
        write_jsonl_zst(output_filepath, read_uncompressed_jsonl(), compression_level)

        # Calculate compression stats
        stats = get_compression_stats(input_filepath, output_filepath)

        # Remove original if requested
        if remove_original and stats.get("space_savings_percent", 0) > 0:
            input_filepath.unlink()
            logger.info(f"Removed original file {input_filepath}")
            stats["original_removed"] = True

        logger.info(f"Compressed {input_filepath} -> {output_filepath} "
                   f"(saved {stats.get('space_savings_percent', 0):.1f}%)")

        return stats

    except Exception as e:
        logger.error(f"Error compressing JSONL file {input_filepath}: {e}")
        return {"error": str(e)}


# Convenience functions for common use cases
def save_crawl_data_compressed(data: Iterable[Any], run_date: str, filename: str = "scraped_data") -> Path:
    """
    Save crawl data to compressed JSONL in standard data_runs structure.

    Args:
        data: Crawl data to save
        run_date: Date string (YYYYMMDD format)
        filename: Base filename (without extension)

    Returns:
        Path to saved compressed file
    """
    output_dir = Path(f"crawl_ops/data_runs/{run_date}")
    output_file = output_dir / f"{filename}.jsonl.zst"

    write_jsonl_zst(output_file, data)
    return output_file


def load_crawl_data_compressed(run_date: str, filename: str = "scraped_data") -> Iterator[Any]:
    """
    Load crawl data from compressed JSONL in standard data_runs structure.

    Args:
        run_date: Date string (YYYYMMDD format)
        filename: Base filename (without extension)

    Yields:
        Crawl data objects
    """
    input_file = Path(f"crawl_ops/data_runs/{run_date}/{filename}.jsonl.zst")

    if not input_file.exists():
        logger.warning(f"Compressed crawl data not found: {input_file}")
        return

    yield from read_jsonl_zst(input_file)
