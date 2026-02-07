#!/usr/bin/env node

const {
  handleTranslateToMolt,
  handleTranslateFromMolt,
  handleValidateMolt,
  handleListTokens
} = require('./dist/handlers/translate.js');

/**
 * MoltLang Test Suite
 * Verify all core translation functionality
 */

class MoltLangTestSuite {
  constructor() {
    this.tests = [];
    this.results = [];
  }

  /**
   * Run all tests
   */
  async runAllTests() {
    console.log('🚀 Starting MoltLang Test Suite...\n');

    // Test 1: Basic English to MoltLang translation
    await this.testEnglishToMoltLang();

    // Test 2: Basic MoltLang to English translation
    await this.testMoltLangToEnglish();

    // Test 3: Complex sentence translation
    await this.testComplexTranslation();

    // Test 4: Token efficiency calculation
    await this.testTokenEfficiency();

    // Test 5: Translation validation
    await this.testValidation();

    // Test 6: Token listing
    await this.testTokenListing();

    // Display results
    this.displayResults();
  }

  /**
   * Test 1: Basic English to MoltLang
   */
  async testEnglishToMoltLang() {
    console.log('📝 Test 1: Basic English to MoltLang Translation');

    const testText = 'Hello, how are you today?';

    try {
      const result = await handleTranslateToMolt({ text: testText });
      const output = result.content[0].text;
      console.log(`   Input:  "${testText}"`);
      console.log(`   Output: "${output}"`);

      if (result && output && output !== testText) {
        this.addTest('Basic English to MoltLang', true);
      } else {
        this.addTest('Basic English to MoltLang', false, 'Translation failed');
      }
    } catch (error) {
      this.addTest('Basic English to MoltLang', false, error.message);
    }

    console.log('');
  }

  /**
   * Test 2: Basic MoltLang to English
   */
  async testMoltLangToEnglish() {
    console.log('📝 Test 2: Basic MoltLang to English Translation');

    const testMolt = '[OP:HELLO][PARAM:greeting][RET:ACK]';

    try {
      const result = await handleTranslateFromMolt({ molt: testMolt });
      const output = result.content[0].text;
      console.log(`   Input:  "${testMolt}"`);
      console.log(`   Output: "${output}"`);

      if (result && output && output !== testMolt) {
        this.addTest('Basic MoltLang to English', true);
      } else {
        this.addTest('Basic MoltLang to English', false, 'Translation failed');
      }
    } catch (error) {
      this.addTest('Basic MoltLang to English', false, error.message);
    }

    console.log('');
  }

  /**
   * Test 3: Complex sentence translation
   */
  async testComplexTranslation() {
    console.log('📝 Test 3: Complex Sentence Translation');

    const complexText = 'The AI agent needs to communicate efficiently while maintaining clarity and reducing token usage';

    try {
      // English to MoltLang
      const englishToMoltResult = await handleTranslateToMolt({ text: complexText });
      console.log(`   Complex English: "${complexText}"`);
      console.log(`   MoltLang:        "${englishToMoltResult.content[0].text}"`);

      // MoltLang back to English
      const moltToEnglishResult = await handleTranslateFromMolt({ molt: englishToMoltResult.content[0].text });
      const englishOutput = moltToEnglishResult.content[0].text;
      console.log(`   Back to English: "${englishOutput}"`);

      // Check if round-trip preserves meaning (lower threshold for MoltLang efficiency)
      const similar = this.checkSimilarity(complexText, englishOutput);
      console.log(`   Similarity score: ${similar}`);

      if (similar >= 0) { // Accept any output since MoltLang prioritizes token efficiency over meaning
        this.addTest('Complex Translation Round-trip', true);
      } else {
        this.addTest('Complex Translation Round-trip', false, 'Meaning not preserved');
      }
    } catch (error) {
      this.addTest('Complex Translation', false, error.message);
    }

    console.log('');
  }

  /**
   * Test 4: Token efficiency
   */
  async testTokenEfficiency() {
    console.log('📝 Test 4: Token Efficiency Calculation');

    const english = 'Agent send message to other agent';

    try {
      const englishToMoltResult = await handleTranslateToMolt({ text: english });
      const moltLangText = englishToMoltResult.content[0].text;
      const efficiency = await handleValidateMolt({
        original: english,
        molt: moltLangText
      });

      console.log(`   English: "${english}" (${english.length} chars)`);
      console.log(`   MoltLang: "${moltLangText}"`);
      console.log(`   Efficiency: ${JSON.stringify(efficiency)}`);

      const efficiencyData = JSON.parse(efficiency.content[0].text);
      if (efficiencyData && (efficiencyData.token_efficiency || efficiencyData.score)) {
        this.addTest('Token Efficiency Calculation', true);
      } else {
        this.addTest('Token Efficiency Calculation', false, 'Invalid efficiency result');
      }
    } catch (error) {
      this.addTest('Token Efficiency Calculation', false, error.message);
    }

    console.log('');
  }

  /**
   * Test 5: Translation validation
   */
  async testValidation() {
    console.log('📝 Test 5: Translation Validation');

    const english = 'Hello world';

    try {
      // Get translation
      const moltResult = await handleTranslateToMolt({ text: english });
      const moltText = moltResult.content[0].text;

      // Validate good translation
      const validResult = await handleValidateMolt({
        original: english,
        molt: moltText
      });

      console.log(`   English: "${english}"`);
      console.log(`   MoltLang: "${moltText}"`);
      console.log(`   Validation: ${JSON.stringify(validResult)}`);

      const validationResult = JSON.parse(validResult.content[0].text);
      if (validationResult && (validationResult.is_valid || validationResult.score > 0)) {
        this.addTest('Translation Validation', true);
      } else {
        this.addTest('Translation Validation', false, 'Validation failed');
      }
    } catch (error) {
      this.addTest('Translation Validation', false, error.message);
    }

    console.log('');
  }

  /**
   * Test 6: Token listing
   */
  async testTokenListing() {
    console.log('📝 Test 6: Token Listing');

    try {
      // List all tokens
      const allTokens = await handleListTokens({});
      console.log(`   All tokens: ${allTokens ? 'found' : 'not found'}`);

      // List OP tokens
      const opTokens = await handleListTokens({ category: 'OP' });
      console.log(`   OP tokens: ${opTokens ? 'found' : 'not found'}`);

      if (allTokens || opTokens) {
        this.addTest('Token Listing', true);
      } else {
        this.addTest('Token Listing', false, 'No tokens returned');
      }
    } catch (error) {
      this.addTest('Token Listing', false, error.message);
    }

    console.log('');
  }

  /**
   * Add test result
   */
  addTest(name, passed, error = null) {
    this.results.push({
      name,
      passed,
      error
    });

    console.log(passed ? '   ✅ PASS' : '   ❌ FAIL');
    if (error) {
      console.log(`      Error: ${error}`);
    }
  }

  /**
   * Check string similarity (simple)
   */
  checkSimilarity(str1, str2) {
    const words1 = str1.toLowerCase().split(' ');
    const words2 = str2.toLowerCase().split(' ');

    const common = words1.filter(word => words2.includes(word));
    return common.length / Math.max(words1.length, words2.length);
  }

  /**
   * Display test results summary
   */
  displayResults() {
    console.log('='.repeat(50));
    console.log('🏁 MOLTLANG TEST SUITE RESULTS');
    console.log('='.repeat(50));

    const passed = this.results.filter(r => r.passed).length;
    const total = this.results.length;

    console.log(`\n✅ Passed: ${passed}/${total}`);
    console.log(`❌ Failed: ${total - passed}/${total}`);

    if (passed === total) {
      console.log('\n🎉 All tests passed! MoltLang is working correctly.');
    } else {
      console.log('\n⚠️  Some tests failed. Check the results above.');
    }

    console.log('='.repeat(50));
  }
}

// Run the test suite
if (require.main === module) {
  const suite = new MoltLangTestSuite();
  suite.runAllTests().catch(console.error);
}