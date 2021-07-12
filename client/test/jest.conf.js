const path = require('path')

module.exports = {
  testEnvironment: 'node',
  rootDir: path.resolve(__dirname, '../'),
  testMatch: [
    '**/*Test.js'
  ],
  moduleFileExtensions: [
    'js',
    'json',
    'vue'
  ],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  transform: {
    '^.+\\.js$': '<rootDir>/node_modules/babel-jest',
    '.*\\.(vue)$': '<rootDir>/node_modules/vue-jest'
  },
  reporters: ['default', ['jest-junit', { suiteName: 'jest tests', outputName: '../junit_jsweb.xml' }]],
  snapshotSerializers: ['<rootDir>/node_modules/jest-serializer-vue'],
  setupFiles: ['<rootDir>/test/setup'],
  coverageDirectory: '<rootDir>/test/coverage',
  collectCoverageFrom: [
    'src/**/*.{js,vue}',
    '!src/main.js',
    '!**/node_modules/**'
  ],
  coverageReporters: [
	'lcov',
    'text'
  ]
}
