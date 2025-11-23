"""
Parallel Retrieval Demo.
Demonstrates parallel fan-out/gather pattern with performance comparison.
"""

import asyncio
import time
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adk.rag.vector_store import VectorStore, get_vector_store
from adk.core.logger import get_logger

logger = get_logger(__name__)


class ParallelRetrievalDemo:
    """Demonstrate parallel vs sequential retrieval performance."""
    
    def __init__(self):
        """Initialize demo with vector store."""
        self.vector_store = get_vector_store()
        
    async def sequential_retrieval(
        self,
        queries: List[str],
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Retrieve documents sequentially (one after another).
        
        Args:
            queries: List of search queries
            top_k: Number of results per query
            
        Returns:
            Results and timing information
        """
        print("\n" + "=" * 70)
        print("SEQUENTIAL RETRIEVAL")
        print("=" * 70)
        
        start_time = time.time()
        results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\nQuery {i}/{len(queries)}: {query[:50]}...")
            query_start = time.time()
            
            try:
                # Sequential: wait for each query to complete
                docs = await self.vector_store.search(query, top_k=top_k)
                query_duration = time.time() - query_start
                
                results.append({
                    "query": query,
                    "documents": docs,
                    "duration": query_duration
                })
                
                print(f"  ✅ Found {len(docs)} documents in {query_duration:.3f}s")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results.append({
                    "query": query,
                    "error": str(e),
                    "duration": time.time() - query_start
                })
        
        total_duration = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"Total Duration: {total_duration:.3f}s")
        print(f"Average per Query: {total_duration/len(queries):.3f}s")
        print(f"{'='*70}")
        
        return {
            "pattern": "sequential",
            "queries": len(queries),
            "results": results,
            "total_duration": total_duration,
            "avg_duration": total_duration / len(queries)
        }
    
    async def parallel_retrieval(
        self,
        queries: List[str],
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Retrieve documents in parallel (all at once).
        
        Uses asyncio.gather for concurrent execution.
        
        Args:
            queries: List of search queries
            top_k: Number of results per query
            
        Returns:
            Results and timing information
        """
        print("\n" + "=" * 70)
        print("PARALLEL RETRIEVAL (Fan-Out/Gather)")
        print("=" * 70)
        
        print(f"\nLaunching {len(queries)} queries concurrently...")
        
        async def search_with_timing(query: str, index: int):
            """Helper to search with timing."""
            query_start = time.time()
            try:
                docs = await self.vector_store.search(query, top_k=top_k)
                duration = time.time() - query_start
                return {
                    "query": query,
                    "documents": docs,
                    "duration": duration,
                    "index": index
                }
            except Exception as e:
                duration = time.time() - query_start
                return {
                    "query": query,
                    "error": str(e),
                    "duration": duration,
                    "index": index
                }
        
        start_time = time.time()
        
        # Create tasks for all queries
        tasks = [
            search_with_timing(query, i)
            for i, query in enumerate(queries, 1)
        ]
        
        # Execute all tasks concurrently using asyncio.gather
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_duration = time.time() - start_time
        
        # Display results
        print(f"\n✅ All queries completed in {total_duration:.3f}s\n")
        
        for result in results:
            if isinstance(result, Exception):
                print(f"Query {result.get('index', '?')}: ❌ Error: {result}")
            else:
                query_preview = result['query'][:50] + "..." if len(result['query']) > 50 else result['query']
                doc_count = len(result.get('documents', []))
                duration = result.get('duration', 0)
                print(f"Query {result['index']}: {query_preview}")
                print(f"  ✅ {doc_count} documents in {duration:.3f}s")
        
        print(f"\n{'='*70}")
        print(f"Total Duration: {total_duration:.3f}s")
        print(f"Longest Query: {max(r.get('duration', 0) for r in results if isinstance(r, dict)):.3f}s")
        print(f"{'='*70}")
        
        return {
            "pattern": "parallel",
            "queries": len(queries),
            "results": results,
            "total_duration": total_duration,
            "longest_query": max(r.get('duration', 0) for r in results if isinstance(r, dict))
        }
    
    async def run_comparison(self, queries: List[str]) -> None:
        """
        Run both sequential and parallel retrieval and compare.
        
        Args:
            queries: List of search queries to test
        """
        print("=" * 70)
        print("PARALLEL vs SEQUENTIAL RETRIEVAL COMPARISON")
        print("=" * 70)
        print(f"\nTest Queries: {len(queries)}")
        print(f"Queries:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q[:60]}...")
        
        # Run sequential
        sequential_results = await self.sequential_retrieval(queries)
        
        # Small delay between tests
        await asyncio.sleep(1)
        
        # Run parallel
        parallel_results = await self.parallel_retrieval(queries)
        
        # Comparison
        print("\n" + "=" * 70)
        print("PERFORMANCE COMPARISON")
        print("=" * 70)
        
        seq_time = sequential_results['total_duration']
        par_time = parallel_results['total_duration']
        speedup = seq_time / par_time if par_time > 0 else 0
        
        print(f"\nSequential Total Time:  {seq_time:.3f}s")
        print(f"Parallel Total Time:    {par_time:.3f}s")
        print(f"\n🚀 Speedup: {speedup:.2f}x")
        print(f"⏱️  Time Saved: {seq_time - par_time:.3f}s ({((seq_time - par_time)/seq_time)*100:.1f}%)")
        
        # Visualization
        print(f"\n{'='*70}")
        print("TIMING VISUALIZATION")
        print(f"{'='*70}\n")
        
        print("Sequential (one after another):")
        bar_length = int(seq_time * 10)
        print(f"  {'█' * bar_length} {seq_time:.3f}s")
        
        print("\nParallel (concurrent):")
        bar_length = int(par_time * 10)
        print(f"  {'█' * bar_length} {par_time:.3f}s")
        
        print(f"\n{'='*70}")
        print("KEY INSIGHT")
        print(f"{'='*70}")
        print(f"""
Parallel execution using asyncio.gather() enables {speedup:.1f}x speedup by:
  ✓ Running all {len(queries)} queries concurrently
  ✓ Waiting only for the longest query (not sum of all)
  ✓ Maximizing I/O throughput for database/API calls

This pattern is implemented in workflow_patterns.py:136 for multi-agent coordination.
""")
        
        print(f"{'='*70}\n")


async def main():
    """Main demo entry point."""
    demo = ParallelRetrievalDemo()
    
    # Test queries for compliance regulations
    test_queries = [
        "GDPR data collection requirements",
        "HIPAA encryption standards for health records",
        "CCPA consumer rights and data deletion",
        "PCI DSS payment card security requirements",
        "SOC 2 access control policies"
    ]
    
    await demo.run_comparison(test_queries)
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\n✅ Parallel retrieval pattern demonstrated successfully!")
    print("\nThis same pattern is used in ADCO for:")
    print("  • Scanning multiple data sources concurrently")
    print("  • Parallel compliance checks across frameworks")
    print("  • Concurrent RAG retrieval from multiple collections")
    print("\nSee: adk/core/workflow_patterns.py for implementation")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
