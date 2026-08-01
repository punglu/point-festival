import js from '@eslint/js';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  {
    ignores: ['dist', 'node_modules', 'coverage', 'playwright-report', 'test-results'],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    // MONGLE-W3-WAGLE-REALTIME-PUSH-RECOVERY-PIN-001: the Wagle Push service
    // worker runs in the ServiceWorkerGlobalScope, where `self` is the global.
    // Without this it lints as browser code and every `self` is an undefined
    // variable. Scoped to the one file rather than loosening `no-undef`.
    files: ['public/sw.js'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: { ...globals.serviceworker, ...globals.browser },
    },
  },
  {
    files: ['src/**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    },
  },
);
