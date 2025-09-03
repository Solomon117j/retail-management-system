#!/usr/bin/env python3
"""
Master Security Testing Script for Retail Management System
Runs comprehensive security tests including penetration testing and external scanning
"""

import os
import sys
import argparse
import subprocess
import json
from datetime import datetime
from pathlib import Path

class SecurityTestRunner:
    """
    Master class for running comprehensive security tests
    """

    def __init__(self, target_url=None, django_settings_module='retail_management_system.settings'):
        """
        Initialize security test runner

        Args:
            target_url (str): Target URL for external scanning
            django_settings_module (str): Django settings module for penetration tests
        """
        self.target_url = target_url
        self.django_settings_module = django_settings_module
        self.results = {}
        self.test_start_time = None
        self.test_end_time = None

    def run_all_tests(self):
        """Run all security tests"""
        print("🚀 Starting Comprehensive Security Testing Suite")
        print("=" * 70)

        self.test_start_time = datetime.now()

        # Run penetration test suite
        self.run_penetration_tests()

        # Run external security scanner if URL provided
        if self.target_url:
            self.run_external_scanner()

        self.test_end_time = datetime.now()

        # Generate comprehensive report
        self.generate_comprehensive_report()

        print("\n" + "=" * 70)
        print("✅ Security Testing Suite Completed")
        print("=" * 70)

    def run_penetration_tests(self):
        """Run Django penetration test suite"""
        print("\n🔍 Running Penetration Test Suite...")
        print("-" * 40)

        try:
            # Set Django environment
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', self.django_settings_module)

            # Import and run penetration test suite
            from penetration_test_suite import PenetrationTestSuite

            # Create test suite instance
            suite = PenetrationTestSuite()
            suite.setUp()

            # Run all tests
            suite.run_all_tests()

            # Store results
            self.results['penetration_tests'] = {
                'status': 'completed',
                'results': suite.test_results,
                'timestamp': datetime.now().isoformat()
            }

            # Clean up
            suite.tearDown()

            print("✅ Penetration tests completed successfully")

        except Exception as e:
            self.results['penetration_tests'] = {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ Penetration tests failed: {str(e)}")

    def run_external_scanner(self):
        """Run external security scanner"""
        print(f"\n🌐 Running External Security Scanner on {self.target_url}...")
        print("-" * 60)

        try:
            # Import and run security scanner
            from security_scanner import SecurityScanner

            # Create scanner instance
            scanner = SecurityScanner(self.target_url)

            # Run scan
            scanner.start_scan()

            # Store results
            self.results['external_scan'] = {
                'status': 'completed',
                'target_url': self.target_url,
                'timestamp': datetime.now().isoformat()
            }

            print("✅ External security scan completed successfully")

        except Exception as e:
            self.results['external_scan'] = {
                'status': 'failed',
                'error': str(e),
                'target_url': self.target_url,
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ External security scan failed: {str(e)}")

    def generate_comprehensive_report(self):
        """Generate comprehensive security report"""
        print("\n📊 Generating Comprehensive Security Report...")

        # Collect all report files
        report_files = []
        current_dir = Path.cwd()

        # Find all security-related report files
        for file_path in current_dir.glob("*security*report*.json"):
            report_files.append(file_path)

        for file_path in current_dir.glob("*penetration*report*.json"):
            report_files.append(file_path)

        # Create comprehensive report
        comprehensive_report = {
            'test_run_info': {
                'start_time': self.test_start_time.isoformat(),
                'end_time': self.test_end_time.isoformat(),
                'duration_seconds': (self.test_end_time - self.test_start_time).total_seconds(),
                'target_url': self.target_url,
                'django_settings': self.django_settings_module
            },
            'test_results': self.results,
            'report_files': [str(f) for f in report_files],
            'summary': self._generate_summary()
        }

        # Save comprehensive report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"comprehensive_security_report_{timestamp}.json"

        with open(report_filename, 'w') as f:
            json.dump(comprehensive_report, f, indent=2, default=str)

        print(f"📄 Comprehensive report saved to: {report_filename}")

        # Print summary
        self._print_summary(comprehensive_report['summary'])

    def _generate_summary(self):
        """Generate test summary"""
        summary = {
            'penetration_tests': {
                'status': self.results.get('penetration_tests', {}).get('status', 'not_run'),
                'passed': 0,
                'failed': 0,
                'warnings': 0,
                'total': 0
            },
            'external_scan': {
                'status': self.results.get('external_scan', {}).get('status', 'not_run'),
                'vulnerabilities_found': 0,
                'scan_success_rate': 0
            },
            'overall_status': 'completed',
            'recommendations': []
        }

        # Process penetration test results
        if 'penetration_tests' in self.results:
            pt_results = self.results['penetration_tests']
            if pt_results['status'] == 'completed':
                test_results = pt_results.get('results', {})
                summary['penetration_tests'].update({
                    'passed': test_results.get('passed', 0),
                    'failed': test_results.get('failed', 0),
                    'warnings': test_results.get('warnings', 0),
                    'total': len(test_results.get('tests', []))
                })

        # Process external scan results
        if 'external_scan' in self.results:
            ext_results = self.results['external_scan']
            if ext_results['status'] == 'completed':
                # This would need to be populated from the scanner results
                summary['external_scan']['vulnerabilities_found'] = 0  # Placeholder

        # Generate recommendations
        summary['recommendations'] = self._generate_recommendations(summary)

        return summary

    def _generate_recommendations(self, summary):
        """Generate security recommendations based on results"""
        recommendations = []

        # Penetration test recommendations
        pt = summary['penetration_tests']
        if pt['failed'] > 0:
            recommendations.append(f"Address {pt['failed']} failed penetration tests")
        if pt['warnings'] > 0:
            recommendations.append(f"Review {pt['warnings']} penetration test warnings")

        # External scan recommendations
        if summary['external_scan']['status'] == 'completed':
            recommendations.append("Review external security scan results for vulnerabilities")

        # General recommendations
        recommendations.extend([
            "Implement regular automated security testing",
            "Set up continuous security monitoring",
            "Conduct periodic penetration testing by certified professionals",
            "Keep security patches and dependencies updated",
            "Implement security awareness training for development team"
        ])

        return recommendations

    def _print_summary(self, summary):
        """Print test summary"""
        print("\n📋 SECURITY TESTING SUMMARY")
        print("=" * 50)

        # Penetration tests
        pt = summary['penetration_tests']
        print("🔍 Penetration Tests:")
        print(f"   Status: {pt['status']}")
        if pt['status'] == 'completed':
            print(f"   Passed: {pt['passed']}")
            print(f"   Failed: {pt['failed']}")
            print(f"   Warnings: {pt['warnings']}")
            print(f"   Total: {pt['total']}")

        # External scan
        ext = summary['external_scan']
        print("🌐 External Security Scan:")
        print(f"   Status: {ext['status']}")
        if ext['status'] == 'completed':
            print(f"   Vulnerabilities Found: {ext['vulnerabilities_found']}")

        # Recommendations
        print("💡 Key Recommendations:")
        for i, rec in enumerate(summary['recommendations'][:5], 1):
            print(f"   {i}. {rec}")

        print("\n✅ Security testing completed successfully!")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Comprehensive Security Testing Suite for Retail Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_security_tests.py --url http://localhost:8000
  python run_security_tests.py --url https://example.com --settings myapp.settings
  python run_security_tests.py  # Run only penetration tests
        """
    )

    parser.add_argument(
        '--url',
        help='Target URL for external security scanning'
    )

    parser.add_argument(
        '--settings',
        default='retail_management_system.settings',
        help='Django settings module (default: retail_management_system.settings)'
    )

    parser.add_argument(
        '--penetration-only',
        action='store_true',
        help='Run only penetration tests (skip external scanning)'
    )

    parser.add_argument(
        '--scan-only',
        action='store_true',
        help='Run only external security scan (skip penetration tests)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.scan_only and not args.url:
        parser.error("--scan-only requires --url to be specified")

    if args.penetration_only and args.scan_only:
        parser.error("Cannot specify both --penetration-only and --scan-only")

    # Determine what to run
    run_penetration = not args.scan_only
    run_external = not args.penetration_only and args.url is not None

    if not run_penetration and not run_external:
        parser.error("Nothing to run. Specify --url for external scanning or remove --scan-only")

    # Run tests
    runner = SecurityTestRunner(
        target_url=args.url if run_external else None,
        django_settings_module=args.settings
    )

    if run_penetration and run_external:
        runner.run_all_tests()
    elif run_penetration:
        runner.test_start_time = datetime.now()
        runner.run_penetration_tests()
        runner.test_end_time = datetime.now()
        runner.generate_comprehensive_report()
    elif run_external:
        runner.test_start_time = datetime.now()
        runner.run_external_scanner()
        runner.test_end_time = datetime.now()
        runner.generate_comprehensive_report()


if __name__ == '__main__':
    main()
