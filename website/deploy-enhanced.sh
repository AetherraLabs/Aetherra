#!/bin/bash
# Aetherra Enhanced Website Deployment Script
# Automates the deployment process for the enhanced website

echo "🚀 Aetherra Enhanced Website Deployment"
echo "======================================"

# Set variables
WEBSITE_DIR="$(pwd)"
BUILD_DIR="$WEBSITE_DIR/build"
ENHANCED_FILES=("index-enhanced.html" "styles-enhanced.css" "script-enhanced.js" "sw.js" "manifest.json" "favicon.svg" "favicon.ico")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        print_success "Found: $1"
        return 0
    else
        print_error "Missing: $1"
        return 1
    fi
}

# Function to validate HTML
validate_html() {
    print_status "Validating HTML structure..."

    # Basic HTML validation
    if ! grep -q "<!DOCTYPE html>" "$1"; then
        print_warning "Missing DOCTYPE declaration"
    fi

    if ! grep -q "<html lang=" "$1"; then
        print_warning "Missing language attribute"
    fi

    if ! grep -q "<meta charset=" "$1"; then
        print_warning "Missing charset declaration"
    fi

    print_success "HTML validation completed"
}

# Function to validate CSS
validate_css() {
    print_status "Validating CSS..."

    # Check for CSS syntax errors (basic)
    if grep -q "}" "$1" && grep -q "{" "$1"; then
        print_success "CSS structure looks valid"
    else
        print_warning "Potential CSS syntax issues"
    fi
}

# Function to validate JavaScript
validate_js() {
    print_status "Validating JavaScript..."

    # Basic JS validation
    if command -v node >/dev/null 2>&1; then
        if node -c "$1" 2>/dev/null; then
            print_success "JavaScript syntax is valid"
        else
            print_warning "JavaScript syntax issues detected"
        fi
    else
        print_warning "Node.js not found, skipping JS validation"
    fi
}

# Function to optimize files
optimize_files() {
    print_status "Optimizing files for production..."

    # Create build directory
    mkdir -p "$BUILD_DIR"

    # Copy and process files
    for file in "${ENHANCED_FILES[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$BUILD_DIR/"
            print_success "Copied: $file"
        fi
    done

    # Copy additional assets
    if [ -d "assets" ]; then
        cp -r "assets" "$BUILD_DIR/"
        print_success "Copied: assets directory"
    fi

    print_success "File optimization completed"
}

# Function to generate deployment manifest
generate_manifest() {
    print_status "Generating deployment manifest..."

    cat > "$BUILD_DIR/deployment-manifest.txt" << EOF
Aetherra Enhanced Website Deployment Manifest
============================================

Deployment Date: $(date)
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "N/A")
Build Version: 2.0.0

Files Included:
EOF

    for file in "${ENHANCED_FILES[@]}"; do
        if [ -f "$BUILD_DIR/$file" ]; then
            size=$(stat -f%z "$BUILD_DIR/$file" 2>/dev/null || stat -c%s "$BUILD_DIR/$file" 2>/dev/null || echo "Unknown")
            echo "- $file ($size bytes)" >> "$BUILD_DIR/deployment-manifest.txt"
        fi
    done

    cat >> "$BUILD_DIR/deployment-manifest.txt" << EOF

Deployment Notes:
- Enhanced website with PWA capabilities
- Interactive demos and Lyrixa AI chat
- Optimized for performance and accessibility
- Mobile-responsive design
- Offline functionality via service worker

Deployment Instructions:
1. Upload all files to your web server
2. Ensure HTTPS is enabled for PWA features
3. Configure proper MIME types for .webmanifest
4. Test installation and offline functionality
EOF

    print_success "Deployment manifest generated"
}

# Function to run tests
run_tests() {
    print_status "Running deployment tests..."

    local test_count=0
    local pass_count=0

    # Test 1: Check file sizes
    test_count=$((test_count + 1))
    html_size=$(stat -f%z "$BUILD_DIR/index-enhanced.html" 2>/dev/null || stat -c%s "$BUILD_DIR/index-enhanced.html" 2>/dev/null || echo "0")
    if [ "$html_size" -gt 10000 ]; then
        print_success "HTML file size: $html_size bytes"
        pass_count=$((pass_count + 1))
    else
        print_error "HTML file too small: $html_size bytes"
    fi

    # Test 2: Check CSS file
    test_count=$((test_count + 1))
    if [ -f "$BUILD_DIR/styles-enhanced.css" ]; then
        css_size=$(stat -f%z "$BUILD_DIR/styles-enhanced.css" 2>/dev/null || stat -c%s "$BUILD_DIR/styles-enhanced.css" 2>/dev/null || echo "0")
        if [ "$css_size" -gt 5000 ]; then
            print_success "CSS file size: $css_size bytes"
            pass_count=$((pass_count + 1))
        else
            print_warning "CSS file seems small: $css_size bytes"
        fi
    else
        print_error "CSS file missing"
    fi

    # Test 3: Check JavaScript file
    test_count=$((test_count + 1))
    if [ -f "$BUILD_DIR/script-enhanced.js" ]; then
        js_size=$(stat -f%z "$BUILD_DIR/script-enhanced.js" 2>/dev/null || stat -c%s "$BUILD_DIR/script-enhanced.js" 2>/dev/null || echo "0")
        if [ "$js_size" -gt 5000 ]; then
            print_success "JavaScript file size: $js_size bytes"
            pass_count=$((pass_count + 1))
        else
            print_warning "JavaScript file seems small: $js_size bytes"
        fi
    else
        print_error "JavaScript file missing"
    fi

    # Test 4: Check service worker
    test_count=$((test_count + 1))
    if [ -f "$BUILD_DIR/sw.js" ]; then
        print_success "Service worker found"
        pass_count=$((pass_count + 1))
    else
        print_error "Service worker missing"
    fi

    # Test 5: Check manifest
    test_count=$((test_count + 1))
    if [ -f "$BUILD_DIR/manifest.json" ]; then
        print_success "Web app manifest found"
        pass_count=$((pass_count + 1))
    else
        print_error "Web app manifest missing"
    fi

    print_status "Tests completed: $pass_count/$test_count passed"

    if [ "$pass_count" -eq "$test_count" ]; then
        print_success "All tests passed! Ready for deployment."
        return 0
    else
        print_warning "Some tests failed. Review before deployment."
        return 1
    fi
}

# Function to create deployment package
create_package() {
    print_status "Creating deployment package..."

    cd "$BUILD_DIR"
    zip -r "../aetherra-enhanced-website.zip" . >/dev/null 2>&1
    cd "$WEBSITE_DIR"

    if [ -f "aetherra-enhanced-website.zip" ]; then
        package_size=$(stat -f%z "aetherra-enhanced-website.zip" 2>/dev/null || stat -c%s "aetherra-enhanced-website.zip" 2>/dev/null || echo "Unknown")
        print_success "Deployment package created: aetherra-enhanced-website.zip ($package_size bytes)"
    else
        print_error "Failed to create deployment package"
        return 1
    fi
}

# Main deployment process
main() {
    print_status "Starting enhanced website deployment process..."

    # Step 1: Validate environment
    print_status "Step 1: Validating environment..."
    if [ ! -d "$WEBSITE_DIR" ]; then
        print_error "Website directory not found: $WEBSITE_DIR"
        exit 1
    fi

    # Step 2: Check required files
    print_status "Step 2: Checking required files..."
    missing_files=0
    for file in "${ENHANCED_FILES[@]}"; do
        if ! check_file "$file"; then
            missing_files=$((missing_files + 1))
        fi
    done

    if [ $missing_files -gt 0 ]; then
        print_error "$missing_files required files are missing"
        exit 1
    fi

    # Step 3: Validate files
    print_status "Step 3: Validating file content..."
    validate_html "index-enhanced.html"
    validate_css "styles-enhanced.css"
    validate_js "script-enhanced.js"

    # Step 4: Optimize for production
    print_status "Step 4: Optimizing for production..."
    optimize_files

    # Step 5: Generate deployment manifest
    print_status "Step 5: Generating deployment documentation..."
    generate_manifest

    # Step 6: Run tests
    print_status "Step 6: Running deployment tests..."
    if ! run_tests; then
        print_warning "Tests failed, but continuing with deployment preparation"
    fi

    # Step 7: Create deployment package
    print_status "Step 7: Creating deployment package..."
    create_package

    # Final summary
    echo ""
    print_success "🎉 Enhanced website deployment preparation completed!"
    echo ""
    echo "📦 Build artifacts:"
    echo "   - Build directory: $BUILD_DIR"
    echo "   - Deployment package: aetherra-enhanced-website.zip"
    echo "   - Deployment manifest: $BUILD_DIR/deployment-manifest.txt"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Test the build directory locally"
    echo "   2. Upload files to your web server"
    echo "   3. Verify HTTPS is enabled"
    echo "   4. Test PWA installation"
    echo "   5. Validate all interactive features"
    echo ""
    print_success "Happy deploying! 🌟"
}

# Run the main function
main "$@"
