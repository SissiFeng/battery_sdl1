#!/usr/bin/env python3
"""
Demo script for SDL1 Recovery System

This script demonstrates the checkpoint-based error recovery system
with hierarchical recovery strategies for different types of failures.
"""

import json
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_recovery_manager():
    """Demonstrate the recovery manager functionality"""
    print("🔄 Recovery Manager Demo")
    print("=" * 50)
    
    try:
        from recovery_manager import (
            RecoveryManager, RecoverableError, PipettingError, 
            ElectrodeError, ElectrochemicalError, CriticalSystemError,
            ErrorSeverity, RecoveryAction
        )
        from opentrons_functions import OpentronsController
        
        # Initialize controller and recovery manager
        controller = OpentronsController(dry_run=True)
        recovery_manager = RecoveryManager(controller)
        
        print("✅ Recovery manager initialized")
        
        # Start a test workflow
        workflow_id = "demo_workflow_001"
        recovery_manager.start_workflow(workflow_id)
        print(f"📋 Started workflow: {workflow_id}")
        
        # Demo 1: Successful operation with checkpoint
        print("\n--- Demo 1: Successful Operation with Checkpoint ---")
        
        def successful_operation(**kwargs):
            print("  🔧 Executing successful operation...")
            time.sleep(1)
            return {"status": "success", "data": "operation_complete"}
        
        result = recovery_manager.run_with_recovery(
            step_function=successful_operation,
            step_name="Test Operation",
            step_index=1,
            checkpoint_name="test_checkpoint_1"
        )
        
        print(f"  ✅ Operation result: {result['status']}")
        print(f"  📊 Checkpoints created: {len(recovery_manager.checkpoints)}")
        
        # Demo 2: Recoverable error with retry
        print("\n--- Demo 2: Recoverable Error with Retry ---")
        
        attempt_count = 0
        def failing_then_succeeding_operation(**kwargs):
            nonlocal attempt_count
            attempt_count += 1
            print(f"  🔧 Attempt {attempt_count}")
            
            if attempt_count < 3:
                raise PipettingError("Simulated pipetting failure")
            else:
                print("  ✅ Operation succeeded on retry")
                return {"status": "success", "attempts": attempt_count}
        
        try:
            result = recovery_manager.run_with_recovery(
                step_function=failing_then_succeeding_operation,
                step_name="Retry Test Operation",
                step_index=2,
                checkpoint_name="test_checkpoint_2",
                max_retries=3
            )
            print(f"  ✅ Final result: {result['status']} after {result['attempts']} attempts")
        except Exception as e:
            print(f"  ❌ Operation failed: {str(e)}")
        
        # Demo 3: Checkpoint restoration
        print("\n--- Demo 3: Checkpoint Restoration ---")
        
        # Get latest checkpoint
        latest_checkpoint = recovery_manager.get_latest_checkpoint()
        if latest_checkpoint:
            print(f"  📍 Latest checkpoint: {latest_checkpoint.name}")
            print(f"  🕐 Created at: {latest_checkpoint.timestamp}")
            
            # Simulate restoration
            restored = recovery_manager.restore_from_checkpoint(latest_checkpoint)
            print(f"  🔄 Restoration {'successful' if restored else 'failed'}")
        
        # Demo 4: Recovery statistics
        print("\n--- Demo 4: Recovery Statistics ---")
        stats = recovery_manager.get_recovery_statistics()
        print(f"  📊 Total errors: {stats['total_errors']}")
        print(f"  ✅ Successful recoveries: {stats['successful_recoveries']}")
        print(f"  ❌ Failed recoveries: {stats['failed_recoveries']}")
        print(f"  📈 Success rate: {stats['success_rate']}%")
        print(f"  📍 Total checkpoints: {stats['total_checkpoints']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Recovery manager not available: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return False

def demo_error_types():
    """Demonstrate different error types and their recovery strategies"""
    print("\n🚨 Error Types and Recovery Strategies Demo")
    print("=" * 60)
    
    try:
        from recovery_manager import (
            PipettingError, ElectrodeError, ElectrochemicalError, 
            CriticalSystemError, ErrorSeverity, RecoveryAction
        )
        
        # Demo different error types
        error_examples = [
            ("Pipetting Error", PipettingError("Tip pickup failed")),
            ("Electrode Error", ElectrodeError("Electrode placement verification failed")),
            ("Electrochemical Error", ElectrochemicalError("Measurement signal unstable")),
            ("Critical System Error", CriticalSystemError("Robot communication lost"))
        ]
        
        for error_name, error in error_examples:
            print(f"\n🔹 {error_name}:")
            print(f"   Severity: {error.severity.value}")
            print(f"   Suggested Action: {error.suggested_action.value}")
            print(f"   Message: {error}")
        
        return True
        
    except ImportError:
        print("❌ Error types not available")
        return False

def demo_sdl1_with_recovery():
    """Demonstrate SDL1 operations with recovery"""
    print("\n🧪 SDL1 Operations with Recovery Demo")
    print("=" * 50)
    
    try:
        from sdl1_operations import SDL1Operations
        from opentrons_functions import OpentronsController
        
        # Initialize with recovery enabled
        controller = OpentronsController(dry_run=True)
        sdl1_ops = SDL1Operations(controller, enable_recovery=True)
        
        print("✅ SDL1 operations initialized with recovery")
        
        # Test solution preparation with recovery
        print("\n--- Testing Solution Preparation with Recovery ---")
        
        solution_params = {
            "volume": 1000,
            "source_well": "A1",
            "target_well": "A1",
            "step_index": 1
        }
        
        result = sdl1_ops.sdl1SolutionPreparation(solution_params)
        print(f"  📊 Result: {result['status']}")
        
        if sdl1_ops.recovery_manager:
            stats = sdl1_ops.recovery_manager.get_recovery_statistics()
            print(f"  📈 Recovery stats: {stats['total_errors']} errors, {stats['success_rate']}% success rate")
        
        return True
        
    except ImportError as e:
        print(f"❌ SDL1 operations not available: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return False

def demo_workflow_with_recovery():
    """Demonstrate a complete workflow with recovery checkpoints"""
    print("\n🔄 Complete Workflow with Recovery Demo")
    print("=" * 50)
    
    try:
        from recovery_manager import RecoveryManager
        from opentrons_functions import OpentronsController
        
        controller = OpentronsController(dry_run=True)
        recovery_manager = RecoveryManager(controller)
        
        # Start workflow
        workflow_id = "complete_demo_workflow"
        recovery_manager.start_workflow(workflow_id)
        
        # Define workflow steps
        workflow_steps = [
            ("Experiment Setup", "experiment_setup_complete"),
            ("Solution Preparation", "solution_preparation_complete"),
            ("Electrode Setup", "electrode_setup_complete"),
            ("Electrochemical Measurement", "measurement_cycle_complete"),
            ("Cleaning", "cleaning_complete")
        ]
        
        print(f"📋 Executing workflow with {len(workflow_steps)} steps")
        
        for i, (step_name, checkpoint_name) in enumerate(workflow_steps):
            print(f"\n  Step {i+1}: {step_name}")
            
            def simulate_step(**kwargs):
                print(f"    🔧 Executing {step_name}...")
                time.sleep(0.5)  # Simulate work
                
                # Simulate occasional failures
                import random
                if random.random() < 0.2:  # 20% chance of failure
                    from recovery_manager import PipettingError
                    raise PipettingError(f"Simulated failure in {step_name}")
                
                return {"status": "success", "step": step_name}
            
            try:
                result = recovery_manager.run_with_recovery(
                    step_function=simulate_step,
                    step_name=step_name,
                    step_index=i,
                    checkpoint_name=checkpoint_name,
                    max_retries=2
                )
                print(f"    ✅ {step_name} completed: {result['status']}")
                
            except Exception as e:
                print(f"    ❌ {step_name} failed: {str(e)}")
                break
        
        # Final statistics
        stats = recovery_manager.get_recovery_statistics()
        print(f"\n📊 Workflow Statistics:")
        print(f"   Total checkpoints: {stats['total_checkpoints']}")
        print(f"   Total errors: {stats['total_errors']}")
        print(f"   Successful recoveries: {stats['successful_recoveries']}")
        print(f"   Success rate: {stats['success_rate']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow demo failed: {str(e)}")
        return False

def demo_checkpoint_management():
    """Demonstrate checkpoint management features"""
    print("\n📍 Checkpoint Management Demo")
    print("=" * 40)
    
    try:
        from recovery_manager import RecoveryManager, Checkpoint
        from opentrons_functions import OpentronsController
        
        controller = OpentronsController(dry_run=True)
        recovery_manager = RecoveryManager(controller)
        
        # Create some test checkpoints
        test_states = [
            {"step": "setup", "data": {"temperature": 25}},
            {"step": "preparation", "data": {"volume": 1000}},
            {"step": "measurement", "data": {"cycles": 3}}
        ]
        
        checkpoint_ids = []
        for i, state in enumerate(test_states):
            checkpoint_id = recovery_manager.save_checkpoint(
                name=f"test_checkpoint_{i+1}",
                step_index=i,
                state=state
            )
            checkpoint_ids.append(checkpoint_id)
            print(f"  📍 Created checkpoint: {checkpoint_id}")
        
        # Demonstrate checkpoint retrieval
        latest = recovery_manager.get_latest_checkpoint()
        print(f"  📋 Latest checkpoint: {latest.name if latest else 'None'}")
        
        specific = recovery_manager.get_latest_checkpoint("test_checkpoint_2")
        print(f"  🎯 Specific checkpoint: {specific.name if specific else 'None'}")
        
        # Demonstrate checkpoint persistence
        checkpoint_files = list(recovery_manager.checkpoint_dir.glob("*.json"))
        print(f"  💾 Checkpoint files created: {len(checkpoint_files)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Checkpoint demo failed: {str(e)}")
        return False

def main():
    """Run all recovery system demos"""
    print("🛡️  SDL1 Recovery System Demo")
    print("=" * 80)
    print("This demo shows the checkpoint-based error recovery system")
    print("with hierarchical recovery strategies for different failure types.")
    print()
    
    # Run demos
    demos = [
        ("Recovery Manager", demo_recovery_manager),
        ("Error Types", demo_error_types),
        ("SDL1 with Recovery", demo_sdl1_with_recovery),
        ("Workflow with Recovery", demo_workflow_with_recovery),
        ("Checkpoint Management", demo_checkpoint_management)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            print(f"❌ Demo '{demo_name}' failed: {str(e)}")
            results.append((demo_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Demo Summary")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Total demos: {total}")
    print(f"Successful: {passed}")
    print(f"Failed: {total - passed}")
    
    print(f"\n📋 Demo Results:")
    for demo_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"  {status} | {demo_name}")
    
    print(f"\n🎯 Key Features Demonstrated:")
    print(f"  • Checkpoint-based recovery system")
    print(f"  • Hierarchical error handling strategies")
    print(f"  • Automatic retry mechanisms")
    print(f"  • Recovery statistics and monitoring")
    print(f"  • Integration with SDL1 operations")
    
    print(f"\n💡 Recovery Strategies:")
    print(f"  • Minor errors → Automatic retry")
    print(f"  • Moderate errors → Restart from checkpoint")
    print(f"  • Severe errors → Safe stop with manual intervention")
    print(f"  • Critical errors → Emergency stop")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
