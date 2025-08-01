#!/usr/bin/env python3
"""
Quick plugin syntax validation script
"""

import glob
import os
import py_compile


def test_plugin_directory(directory):
    """Test all Python files in a directory for syntax errors"""
    print(f"\n{'=' * 50}")
    print(f"Testing directory: {directory}")
    print(f"{'=' * 50}")

    if not os.path.exists(directory):
        print(f"❌ Directory {directory} does not exist")
        return False

    os.chdir(directory)
    files = glob.glob("*.py")

    if not files:
        print(f"❌ No Python files found in {directory}")
        return False

    print(f"Found {len(files)} Python files")

    all_passed = True
    for filename in sorted(files):
        try:
            py_compile.compile(filename, doraise=True)
            print(f"✅ {filename} - OK")
        except Exception as e:
            print(f"❌ {filename} - ERROR: {e}")
            all_passed = False

    return all_passed


def main():
    """Main test function"""
    print("Aetherra Plugin Syntax Validation")
    print("=" * 50)

    # Save original directory
    original_dir = os.getcwd()

    try:
        # Test both plugin directories
        dir1_passed = test_plugin_directory(
            os.path.join(original_dir, "Aetherra", "plugins")
        )
        os.chdir(original_dir)

        dir2_passed = test_plugin_directory(
            os.path.join(original_dir, "src", "aetherra", "plugins")
        )
        os.chdir(original_dir)

        print(f"\n{'=' * 50}")
        print("SUMMARY:")
        print(f"{'=' * 50}")

        if dir1_passed and dir2_passed:
            print("🎉 ALL PLUGIN FILES PASSED SYNTAX VALIDATION!")
            print("✅ Aetherra/plugins - All files OK")
            print("✅ src/aetherra/plugins - All files OK")
            return True
        else:
            print("❌ SOME PLUGIN FILES HAVE SYNTAX ERRORS!")
            print(f"❌ Aetherra/plugins - {'PASSED' if dir1_passed else 'FAILED'}")
            print(f"❌ src/aetherra/plugins - {'PASSED' if dir2_passed else 'FAILED'}")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
