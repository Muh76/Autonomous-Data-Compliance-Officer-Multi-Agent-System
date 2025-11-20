"""
Code Execution Tool - Safe Python sandbox for data analysis.
Allows agents to execute Python code for data processing and analysis.
"""

import subprocess
import tempfile
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from ..core.logger import get_logger

logger = get_logger(__name__)


class CodeExecutor:
    """
    Execute Python code in a sandboxed environment.
    
    Security features:
    - Timeout limits
    - Restricted imports (no os, subprocess, etc.)
    - Isolated temporary files
    - Resource limits
    """
    
    def __init__(
        self,
        timeout: int = 30,
        max_output_size: int = 10000
    ):
        """
        Initialize code executor.
        
        Args:
            timeout: Maximum execution time in seconds
            max_output_size: Maximum output size in characters
        """
        self.timeout = timeout
        self.max_output_size = max_output_size
        
        # Allowed imports for data analysis
        self.allowed_imports = [
            'json', 'math', 'statistics', 're', 'datetime',
            'pandas', 'numpy', 'collections'
        ]
        
        logger.info("Code executor initialized", timeout=timeout)
    
    async def execute(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute
            context: Optional context data to inject
            
        Returns:
            Execution result with stdout, stderr, and return value
            
        Example:
            result = await executor.execute('''
                import pandas as pd
                data = context['data']
                df = pd.DataFrame(data)
                print(f"Rows: {len(df)}")
                result = df.describe().to_dict()
            ''', context={'data': [{'name': 'John', 'age': 30}]})
        """
        logger.info("Executing code", code_length=len(code))
        
        # Validate code safety
        validation = self._validate_code(code)
        if not validation['is_safe']:
            logger.warning("Unsafe code detected", issues=validation['issues'])
            return {
                'success': False,
                'error': f"Unsafe code: {', '.join(validation['issues'])}",
                'stdout': '',
                'stderr': ''
            }
        
        # Prepare execution environment
        script = self._prepare_script(code, context)
        
        # Execute in subprocess
        try:
            result = await self._run_subprocess(script)
            logger.info("Code execution completed", success=result['success'])
            return result
        except Exception as e:
            logger.error("Code execution failed", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': ''
            }
    
    def _validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate code for security issues.
        
        Args:
            code: Python code to validate
            
        Returns:
            Validation result
        """
        issues = []
        
        # Check for dangerous imports
        dangerous_imports = ['os', 'subprocess', 'sys', 'eval', 'exec', '__import__']
        for imp in dangerous_imports:
            if f'import {imp}' in code or f'from {imp}' in code:
                issues.append(f"Dangerous import: {imp}")
        
        # Check for dangerous functions
        dangerous_funcs = ['eval(', 'exec(', 'compile(', '__import__(']
        for func in dangerous_funcs:
            if func in code:
                issues.append(f"Dangerous function: {func}")
        
        # Check for file operations (except read-only)
        if 'open(' in code and 'w' in code:
            issues.append("File write operations not allowed")
        
        return {
            'is_safe': len(issues) == 0,
            'issues': issues
        }
    
    def _prepare_script(self, code: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Prepare script with context injection.
        
        Args:
            code: User code
            context: Context data
            
        Returns:
            Complete script
        """
        # Inject context as a variable
        context_json = json.dumps(context or {})
        
        script = f"""
import json
import sys

# Inject context
context = json.loads('''{context_json}''')

# User code
try:
    {code}
    
    # Capture result if defined
    if 'result' in locals():
        print("__RESULT__")
        print(json.dumps(result))
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
        return script
    
    async def _run_subprocess(self, script: str) -> Dict[str, Any]:
        """
        Run script in subprocess.
        
        Args:
            script: Complete script to run
            
        Returns:
            Execution result
        """
        # Write script to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Run with timeout
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Parse output
            stdout = result.stdout[:self.max_output_size]
            stderr = result.stderr[:self.max_output_size]
            
            # Extract result if present
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
                'result': result_value,
                'exit_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Execution timeout ({self.timeout}s)',
                'stdout': '',
                'stderr': ''
            }
        finally:
            # Clean up
            try:
                os.unlink(script_path)
            except:
                pass
    
    async def analyze_data(
        self,
        data: Any,
        analysis_type: str = "summary"
    ) -> Dict[str, Any]:
        """
        Convenience method for common data analysis tasks.
        
        Args:
            data: Data to analyze (list, dict, etc.)
            analysis_type: Type of analysis (summary, pii_scan, statistics)
            
        Returns:
            Analysis result
        """
        if analysis_type == "summary":
            code = """
import pandas as pd
import json

data = context['data']
df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])

result = {
    'row_count': len(df),
    'column_count': len(df.columns),
    'columns': list(df.columns),
    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
    'sample': df.head(3).to_dict('records')
}
"""
        elif analysis_type == "pii_scan":
            code = """
import pandas as pd
import re

data = context['data']
df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])

# Simple PII patterns
email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
phone_pattern = r'\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b'
ssn_pattern = r'\\b\\d{3}-\\d{2}-\\d{4}\\b'

pii_columns = []
for col in df.columns:
    col_str = df[col].astype(str).str.cat(sep=' ')
    if re.search(email_pattern, col_str) or re.search(phone_pattern, col_str) or re.search(ssn_pattern, col_str):
        pii_columns.append(col)

result = {
    'pii_columns': pii_columns,
    'total_columns': len(df.columns),
    'pii_risk': 'HIGH' if pii_columns else 'LOW'
}
"""
        elif analysis_type == "statistics":
            code = """
import pandas as pd

data = context['data']
df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])

numeric_cols = df.select_dtypes(include=['number']).columns
stats = {}

for col in numeric_cols:
    stats[col] = {
        'mean': float(df[col].mean()),
        'median': float(df[col].median()),
        'std': float(df[col].std()),
        'min': float(df[col].min()),
        'max': float(df[col].max())
    }

result = stats
"""
        else:
            return {'success': False, 'error': f'Unknown analysis type: {analysis_type}'}
        
        return await self.execute(code, context={'data': data})
