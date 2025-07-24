#!/usr/bin/env python3
"""
Test Runner for Battery SDL1 Workflow Mapper

Runs all tests in the correct order and provides a comprehensive report.
"""

import sys
import os
import subprocess
import time
from datetime import datetime

def run_test(test_file, description):
    """Run a single test file and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        success = result.returncode == 0
        
        print(f"Exit Code: {result.returncode}")
        print(f"Duration: {duration:.2f}s")
        
        if result.stdout:
            print(f"\nSTDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr}")
        
        return {
            "test_file": test_file,
            "description": description,
            "success": success,
            "duration": duration,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
    except subprocess.TimeoutExpired:
        print(f"❌ Test timed out after 120 seconds")
        return {
            "test_file": test_file,
            "description": description,
            "success": False,
            "duration": 120,
            "exit_code": -1,
            "stdout": "",
            "stderr": "Test timed out"
        }
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return {
            "test_file": test_file,
            "description": description,
            "success": False,
            "duration": 0,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e)
        }

def main():
    """Run all tests and generate a report"""
    print("🧪 Battery SDL1 Workflow Mapper - Test Suite")
    print(f"Started at: {datetime.now().isoformat()}")
    print("="*80)
    
    # Define tests in order of execution
    tests = [
        ("test_new_json_format.py", "Basic JSON Format Analysis"),
        ("test_json_compatibility.py", "Comprehensive JSON Compatibility"),
        ("final_integration_test.py", "Complete Integration Test"),
        ("test_api_new_format.py", "API Endpoint Testing (requires server)"),
        ("test_canvas_workflow.py", "Canvas Workflow Testing (requires dependencies)")
    ]
    
    results = []
    total_start_time = time.time()
    
    # Run each test
    for test_file, description in tests:
        if os.path.exists(test_file):
            result = run_test(test_file, description)
            results.append(result)
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results.append({
                "test_file": test_file,
                "description": description,
                "success": False,
                "duration": 0,
                "exit_code": -1,
                "stdout": "",
                "stderr": "File not found"
            })
    
    total_duration = time.time() - total_start_time
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY REPORT")
    print(f"{'='*80}")
    
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    print(f"Total Duration: {total_duration:.2f}s")
    
    print(f"\n📋 Individual Test Results:")
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"  {status} | {result['description']} ({result['duration']:.2f}s)")
        if not result["success"] and result["stderr"]:
            print(f"    Error: {result['stderr'][:100]}...")
    
    # Detailed results for failed tests
    failed_tests = [r for r in results if not r["success"]]
    if failed_tests:
        print(f"\n❌ Failed Test Details:")
        for result in failed_tests:
            print(f"\n--- {result['test_file']} ---")
            print(f"Description: {result['description']}")
            print(f"Exit Code: {result['exit_code']}")
            if result['stderr']:
                print(f"Error: {result['stderr']}")
            if result['stdout']:
                print(f"Output: {result['stdout'][:500]}...")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if passed == len(results):
        print("  🎉 All tests passed! The system is working correctly.")
    else:
        print("  🔧 Some tests failed. Check the details above.")
        if any("requires server" in r["description"] for r in failed_tests):
            print("  📡 API tests failed - make sure the API server is running")
        if any("requires dependencies" in r["description"] for r in failed_tests):
            print("  📦 Dependency tests failed - install missing packages")
    
    # Save detailed report
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(f"Battery SDL1 Test Report\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Total Duration: {total_duration:.2f}s\n")
        f.write(f"Success Rate: {(passed/len(results)*100):.1f}%\n\n")
        
        for result in results:
            f.write(f"Test: {result['test_file']}\n")
            f.write(f"Description: {result['description']}\n")
            f.write(f"Success: {result['success']}\n")
            f.write(f"Duration: {result['duration']:.2f}s\n")
            f.write(f"Exit Code: {result['exit_code']}\n")
            if result['stdout']:
                f.write(f"STDOUT:\n{result['stdout']}\n")
            if result['stderr']:
                f.write(f"STDERR:\n{result['stderr']}\n")
            f.write(f"{'-'*40}\n")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if passed == len(results) else 1)

if __name__ == "__main__":
    main()
