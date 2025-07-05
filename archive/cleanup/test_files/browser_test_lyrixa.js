
// === LYRIXA LIVE WEBSITE TEST ===
console.log("🧪 Starting Lyrixa Live Website Test...");

let testResults = {
    timestamp: new Date().toISOString(),
    tests: {},
    summary: {
        total: 0,
        passed: 0,
        failed: 0,
        warnings: 0
    }
};

function logResult(testName, status, message) {
    testResults.tests[testName] = { status, message };
    testResults.summary.total++;
    
    if (status === 'PASS') {
        testResults.summary.passed++;
        console.log(`✅ ${testName}: ${message}`);
    } else if (status === 'FAIL') {
        testResults.summary.failed++;
        console.log(`❌ ${testName}: ${message}`);
    } else if (status === 'WARNING') {
        testResults.summary.warnings++;
        console.log(`⚠️ ${testName}: ${message}`);
    } else {
        console.log(`ℹ️ ${testName}: ${message}`);
    }
}

// Test 1: Function Existence
try {
    if (typeof showLyrixaDemo === 'function') {
        logResult('Function_Existence', 'PASS', 'showLyrixaDemo function is available');
    } else {
        logResult('Function_Existence', 'FAIL', 'showLyrixaDemo function not found');
    }
} catch (error) {
    logResult('Function_Existence', 'FAIL', `Error checking function: ${error.message}`);
}

// Test 2: Button Existence
const lyrixaButton = document.querySelector('a[onclick*="showLyrixaDemo"]');
if (lyrixaButton) {
    logResult('Button_Existence', 'PASS', `Lyrixa button found: "${lyrixaButton.textContent.trim()}"`);
} else {
    logResult('Button_Existence', 'FAIL', 'Lyrixa button not found in navigation');
}

// Test 3: Target Elements
const targetElements = [
    document.getElementById('lyrixa'),
    document.querySelector('.ai-assistant-preview'),
    document.querySelector('.interactive-demo'),
    document.querySelector('#features')
];

const validTargets = targetElements.filter(el => el !== null);
if (validTargets.length > 0) {
    logResult('Target_Elements', 'PASS', `Found ${validTargets.length} valid scroll targets`);
} else {
    logResult('Target_Elements', 'FAIL', 'No valid scroll targets found');
}

// Test 4: CSS Animation
const styleSheets = Array.from(document.styleSheets);
let foundHighlightDemo = false;
let foundKeyframes = false;

try {
    styleSheets.forEach(sheet => {
        try {
            Array.from(sheet.cssRules || []).forEach(rule => {
                if (rule.selectorText && rule.selectorText.includes('highlight-demo')) {
                    foundHighlightDemo = true;
                }
                if (rule.name === 'highlight-pulse') {
                    foundKeyframes = true;
                }
            });
        } catch (e) {
            // Cross-origin - skip
        }
    });
    
    if (foundHighlightDemo && foundKeyframes) {
        logResult('CSS_Animation', 'PASS', 'Highlight animation CSS found');
    } else if (foundHighlightDemo) {
        logResult('CSS_Animation', 'WARNING', 'Highlight CSS found but keyframes may be missing');
    } else {
        logResult('CSS_Animation', 'FAIL', 'Highlight animation CSS not found');
    }
} catch (error) {
    logResult('CSS_Animation', 'WARNING', 'Could not fully check CSS due to cross-origin restrictions');
}

// Test 5: Functional Test (simulate button click)
if (lyrixaButton && typeof showLyrixaDemo === 'function') {
    try {
        const initialScrollPos = window.pageYOffset;
        
        // Execute the function
        showLyrixaDemo();
        
        // Check if any element got the highlight class
        setTimeout(() => {
            const highlightedElement = document.querySelector('.highlight-demo');
            if (highlightedElement) {
                logResult('Functional_Test', 'PASS', 'Function executed and applied highlight effect');
            } else {
                logResult('Functional_Test', 'WARNING', 'Function executed but no highlight effect visible');
            }
            
            // Generate final report
            setTimeout(() => {
                console.log("\n🧪 === LYRIXA TEST RESULTS ===");
                console.log(`Total Tests: ${testResults.summary.total}`);
                console.log(`Passed: ${testResults.summary.passed} ✅`);
                console.log(`Failed: ${testResults.summary.failed} ❌`);
                console.log(`Warnings: ${testResults.summary.warnings} ⚠️`);
                
                const successRate = (testResults.summary.passed / testResults.summary.total * 100).toFixed(1);
                console.log(`Success Rate: ${successRate}%`);
                
                if (testResults.summary.failed === 0) {
                    console.log("🎉 ALL TESTS PASSED! Lyrixa is functioning perfectly!");
                } else if (testResults.summary.failed <= 1) {
                    console.log("⚠️ Minor issues detected. Lyrixa mostly functional.");
                } else {
                    console.log("❌ Multiple issues found. Lyrixa needs attention.");
                }
                
                console.log("\n📋 Detailed Results:", testResults);
                
                // Save results to localStorage for later retrieval
                localStorage.setItem('lyrixaTestResults', JSON.stringify(testResults));
                console.log("💾 Results saved to localStorage as 'lyrixaTestResults'");
            }, 1000);
        }, 500);
        
    } catch (error) {
        logResult('Functional_Test', 'FAIL', `Error during function execution: ${error.message}`);
    }
} else {
    logResult('Functional_Test', 'FAIL', 'Cannot test function - button or function missing');
}

console.log("⏳ Testing in progress... Results in a few seconds...");
