module.exports = {
  root: true,
  env: {
    node: true,
    browser: true
  },
  parserOptions: {
    project: './tsconfig.json',
    tsconfigRootDir: __dirname
  },
  extends: [
    './rules/eslint/js',
    './rules/eslint/import',
    './rules/eslint/react',
    './rules/eslint/ts',
    './rules/eslint/prettier'
  ],
  rules: {
    '@next/next/no-sync-scripts': 'off'
  }
};
