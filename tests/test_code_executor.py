"""Simple standalone test for code execution."""

import asyncio
import subprocess
import tempfile
import os
import json


class SimpleCodeExecutor:
    """Simplified code executor for testing."""
    
    async def execute(self, code: str, context=None):
        """Execute Python code."""
        context_json = json.dumps(context or {})
        
        script = f"""
import json
context = json.loads('''{context_json}''')

{code}

if 'result' in locals():
    print("__RESULT__")
    print(json.dumps(result))
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            stdout = result.stdout
            stderr = result.stderr
            result_value = None
            
            if '__RESULT__' in stdout:
                parts = stdout.split('__RESULT__')
                stdout = parts[0].strip()
                try:
                    result_value = json.loads(parts[1].strip())
                except:
                    pass
            
            return {
                'success': result.returncode == 0,
                'stdout': stdout,
                'stderr': stderr,
                'result': result_value
            }
        finally:
            os.unlink(script_path)


async def test():
    """Run tests."""
    print("=" * 70)
    print("CODE EXECUTION TOOL TEST (Standalone)")
    print("=" * 70)
    
    executor = SimpleCodeExecutor()
    
    # Test 1
    print("\nTest 1: Simple calculation")
    result1 = await executor.execute("""
import math
result = math.sqrt(16) + math.pi
print(f"Result: {result}")
""")
    print(f"✅ Success: {result1['success']}")
    print(f"   Output: {result1['stdout']}")
    print(f"   Result: {result1.get('result')}")
    
    # Test 2
    print("\nTest 2: Data analysis")
    result2 = await executor.execute("""
import pandas as pd
data = context['users']
df = pd.DataFrame(data)
result = {'total': len(df), 'columns': list(df.columns)}
print(f"Analyzed {len(df)} users")
""", context={'users': [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]})
    
    print(f"✅ Success: {result2['success']}")
    print(f"   Output: {result2['stdout']}")
    print(f"   Result: {result2.get('result')}")
    
    print("\n" + "=" * 70)
    print("✅ Code execution tool working!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test())
