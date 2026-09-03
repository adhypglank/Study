#!/usr/bin/env python3
"""Test Charta connections and configuration."""

import sys
import logging
from datetime import datetime

from charta_config import get_config
from charta_connection_manager import get_connection_manager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("charta_test.log"),
    ],
)

logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def test_config():
    """Test configuration loading."""
    print_section("1️⃣  CONFIGURATION TEST")

    try:
        config = get_config()
        config.validate_all()
        
        print("✅ Configuration loaded successfully!\n")
        print(f"   Vault Path: {config.vault.path}")
        print(f"   MT5 Server: {config.mt5.server}")
        print(f"   MT5 Login: {config.mt5.login}")
        print(f"   MT5 Timeout: {config.mt5.timeout}s")
        print(f"   ZeroMQ Endpoint: {config.zeromq.server_endpoint}")
        print(f"   Debug Mode: {config.debug}")
        print(f"   Log Level: {config.log_level}\n")
        
        health = config.health_check()
        print("Health Status:")
        for component, status in health.items():
            status_str = "✅ Configured" if status else "⚠️  Missing"
            print(f"   {component.replace('_', ' ').title()}: {status_str}")
        
        return True

    except Exception as e:
        print(f"❌ Configuration error: {e}\n")
        return False


def test_mt5_connection():
    """Test MetaTrader 5 connection."""
    print_section("2️⃣  METATRADER 5 CONNECTION TEST")

    try:
        mgr = get_connection_manager()
        status = mgr.mt5.connect()

        print(f"   {status}\n")

        if status.is_connected:
            account = mgr.mt5.get_account_info()
            if account:
                print("   Account Information:")
                for key, value in account.items():
                    if key in ("balance", "equity", "profit"):
                        print(f"      {key.title()}: ${value:,.2f}")
                    else:
                        print(f"      {key.title()}: {value}")
                print()
            return True
        else:
            print(f"   Error Details: {status.error}\n")
            return False

    except Exception as e:
        print(f"❌ MT5 connection error: {e}\n")
        return False


def test_zeromq_connection():
    """Test ZeroMQ bridge connection."""
    print_section("3️⃣  ZEROMQ BRIDGE TEST")

    try:
        mgr = get_connection_manager()
        status = mgr.zeromq.connect()

        print(f"   {status}\n")

        if status.is_connected:
            test_msg = "PING_TEST"
            if mgr.zeromq.send_message(test_msg):
                print(f"   ✅ Test message sent: '{test_msg}'\n")
                return True
            else:
                print("   ⚠️  Failed to send test message\n")
                return False
        else:
            print(f"   Error Details: {status.error}\n")
            print("   Note: ZeroMQ server must be running in MetaTrader 5\n")
            return False

    except Exception as e:
        print(f"⚠️  ZeroMQ test warning: {e}\n")
        print("   (This is expected if MT5 ZeroMQ server is not running)\n")
        return False


def test_all_connections():
    """Test all connections together."""
    print_section("4️⃣  FULL CONNECTION TEST")

    try:
        mgr = get_connection_manager()
        statuses = mgr.connect_all()
        health = mgr.health_check()

        print("\nConnection Summary:")
        print(f"   MT5: {'✅ Connected' if health['mt5'] else '❌ Disconnected'}")
        print(f"   ZeroMQ: {'✅ Connected' if health['zeromq'] else '⚠️  Not Ready'}")
        print(f"   Overall: {'✅ All Systems OK' if health['all_connected'] else '⚠️  Partial Connection'}\n")

        return health.get("all_connected", False)

    except Exception as e:
        print(f"❌ Full connection test error: {e}\n")
        return False


def print_recommendations():
    """Print recommendations based on test results."""
    print_section("📋 RECOMMENDATIONS")
    
    print("""
1. ✅ Configuration
   - Verify all required environment variables are set
   - Use 'python charta_config.py' to validate
   
2. ✅ MetaTrader 5
   - Ensure MT5 terminal is running
   - Check login credentials are correct
   - Verify demo/live server is correct
   - Check firewall allows MT5 connections

3. ✅ ZeroMQ Bridge
   - Start MT5 Expert Advisor with charta_bridge.mqh
   - Ensure ports 5555/5556 are not blocked by firewall
   - Check ZEROMQ_SERVER_ENDPOINT matches MT5 setting

4. ✅ Cloud Services (Optional)
   - QWen API: Get key from Alibaba DashScope
   - OSS: Configure Alibaba Object Storage Service
   - NGROK: Enable for public tunnel access

5. ✅ Logging & Monitoring
   - Check 'charta.log' for detailed errors
   - Enable DEBUG_MODE=true for verbose output
   - Use 'tail -f charta.log' to monitor in real-time

6. ✅ Security
   - NEVER commit .env.local to git
   - Keep CHARTA_MASTER_KEY private
   - Rotate keys regularly
   - Use different credentials for dev/prod
    """)


def main():
    """Run all tests."""
    print("\n" + "🔍 CHARTA CONNECTION DIAGNOSTIC ".center(70, "="))
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = {
        "Configuration": test_config(),
        "MetaTrader 5": test_mt5_connection(),
        "ZeroMQ Bridge": test_zeromq_connection(),
        "All Connections": test_all_connections(),
    }

    print_section("📊 TEST RESULTS SUMMARY")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "⚠️  CHECK"
        print(f"   {test_name}: {status}")

    print_recommendations()

    print_section("✨ TEST COMPLETE")
    overall_pass = all(results.values())
    if overall_pass:
        print("✅ All tests passed! Your Charta system is ready to go.\n")
        return 0
    else:
        print("⚠️  Some tests need attention. Please review recommendations above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
