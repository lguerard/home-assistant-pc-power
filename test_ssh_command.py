#!/usr/bin/env python3
"""Test script for SSH command functionality."""

import asyncio
import os
import sys

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "custom_components"))

from pc_power_control.switch import PCPowerSwitch


async def test_ssh_command():
    """Test the SSH command functionality."""
    # Test configuration (replace with your actual values)
    TEST_CONFIG = {
        "name": "Test PC",
        "host": "192.168.1.100",  # Replace with your PC's IP
        "mac": "00:11:22:33:44:55",  # Replace with your PC's MAC
        "username": "testuser",  # Replace with your SSH username
        "password": "testpass",  # Replace with your SSH password
        "ssh_port": 22,
        "ssh_timeout": 30,
    }

    print("Creating PC Power Switch instance...")
    switch = PCPowerSwitch(
        TEST_CONFIG["name"],
        TEST_CONFIG["host"],
        TEST_CONFIG["mac"],
        TEST_CONFIG["username"],
        TEST_CONFIG["password"],
        TEST_CONFIG["ssh_port"],
        TEST_CONFIG["ssh_timeout"],
    )

    print("Testing SSH command: 'echo Hello from Home Assistant'")
    result = await switch.async_send_ssh_command("echo Hello from Home Assistant")

    print("\n=== SSH Command Result ===")
    print(f"Success: {result['success']}")
    print(f"Return Code: {result['return_code']}")
    print(f"Stdout: {result['stdout']}")
    print(f"Stderr: {result['stderr']}")

    if result["success"] and result["stdout"].strip() == "Hello from Home Assistant":
        print("\n✅ SSH command test PASSED!")
    else:
        print("\n❌ SSH command test FAILED!")
        return False

    return True


if __name__ == "__main__":
    print("PC Power Control SSH Command Test")
    print("=" * 40)
    print("\n⚠️  BEFORE RUNNING THIS TEST:")
    print("1. Update the TEST_CONFIG dictionary above with your actual PC details")
    print("2. Ensure your PC has SSH server running and accessible")
    print("3. Make sure the credentials are correct")
    print("\nContinue? (y/N): ", end="")

    response = input().strip().lower()
    if response == "y":
        try:
            success = asyncio.run(test_ssh_command())
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            sys.exit(1)
    else:
        print("Test cancelled.")
        sys.exit(0)
