import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import test from 'node:test'
import vm from 'node:vm'
import { ESLint } from 'eslint'
import postcss from 'postcss'
import tailwindcss from 'tailwindcss'
import ts from 'typescript'
import tailwindConfig from '../tailwind.config.js'

const root = fileURLToPath(new URL('../', import.meta.url))

async function bootstrapHarness(fetch) {
    const source = await readFile(new URL('../src/App.tsx', import.meta.url), 'utf8')
    const tree = ts.createSourceFile('App.tsx', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX)
    const statements = tree.statements.filter(node =>
        (ts.isFunctionDeclaration(node) && ['loadBootstrap', 'normalizeBootstrap'].includes(node.name?.text)) ||
        (ts.isVariableStatement(node) && node.declarationList.declarations.some(declaration =>
            ts.isIdentifier(declaration.name) && declaration.name.text === 'FALLBACK_BOOTSTRAP')))
    assert.equal(statements.length, 3)
    const compiled = ts.transpileModule(statements.map(node => node.getText(tree)).join('\n'), {
        compilerOptions: { target: ts.ScriptTarget.ES2022 },
    })
    return vm.runInNewContext(compiled.outputText + '\n({loadBootstrap, FALLBACK_BOOTSTRAP})', { fetch })
}

test('bootstrap uses the existing read-only request and publishes its real result', async () => {
    const requests = []
    let syntheticPayload
    const harness = await bootstrapHarness(async (url, options) => {
        requests.push({ url, headers: options.headers, method: options.method })
        return { ok: true, json: async () => syntheticPayload }
    })
    syntheticPayload = { ...harness.FALLBACK_BOOTSTRAP,
        observatory: { ...harness.FALLBACK_BOOTSTRAP.observatory, core_label: 'SYNTHETIC' } }
    const result = await harness.loadBootstrap()
    assert.equal(result.source, 'api')
    assert.equal(result.payload.observatory.core_label, 'SYNTHETIC')
    assert.equal(result.payload.read_only, true)
    assert.equal(requests.length, 1)
    assert.equal(requests[0].url, '/api/runtime-ui/bootstrap?mode=first_launch&user=Tim&limit=8')
    assert.equal(requests[0].headers.Accept, 'application/json')
    assert.equal(requests[0].method, undefined)
})

for (const [name, fetch] of [
    ['network rejection', async () => { throw new Error('synthetic network failure') }],
    ['synchronous transport failure', () => { throw new Error('synthetic transport failure') }],
    ['HTTP failure', async () => ({ ok: false, status: 503 })],
    ['invalid JSON', async () => ({ ok: true, json: async () => { throw new SyntaxError('synthetic JSON failure') } })],
]) {
    test(`bootstrap resolves ${name} asynchronously as fallback`, async () => {
        const harness = await bootstrapHarness(fetch)
        const pending = harness.loadBootstrap()
        assert.equal(typeof pending.then, 'function')
        const result = await pending
        assert.equal(result.source, 'fallback')
        assert.equal(result.payload.read_only, true)
        assert.equal(result.payload.manifest.controls_enabled, false)
        assert.equal(result.payload.observatory.core_label, harness.FALLBACK_BOOTSTRAP.observatory.core_label)
    })
}

test('the lockfile matches both manifest dependency sections', async () => {
    const manifest = JSON.parse(await readFile(new URL('../package.json', import.meta.url)))
    const lock = JSON.parse(await readFile(new URL('../package-lock.json', import.meta.url)))
    for (const section of ['dependencies', 'devDependencies']) {
        assert.deepEqual(lock.packages[''][section], manifest[section])
    }
})

test('TypeScript linting rejects unused bindings and explicit any', async () => {
    const eslint = new ESLint({ cwd: root })
    const [result] = await eslint.lintText('const unused: any = 1;', {
        filePath: 'src/toolchain-probe.ts',
    })
    assert.ok(result.messages.some(message => message.ruleId === '@typescript-eslint/no-unused-vars'))
    assert.ok(result.messages.some(message => message.ruleId === '@typescript-eslint/no-explicit-any'))
})

test('TSX linting enforces hooks and component refresh rules', async () => {
    const eslint = new ESLint({ cwd: root })
    const config = await eslint.calculateConfigForFile(path.join(root, 'src/App.tsx'))
    assert.equal(config.rules['react-hooks/rules-of-hooks'][0], 2)
    assert.equal(config.rules['react-hooks/exhaustive-deps'][0], 1)
    assert.equal(config.rules['react-refresh/only-export-components'][0], 1)
})

test('the active Observatory source passes every configured lint rule', async () => {
    const eslint = new ESLint({ cwd: root })
    const results = await eslint.lintFiles(['src/**/*.{ts,tsx}'])
    assert.ok(results.length > 0)
    for (const result of results) {
        assert.equal(result.errorCount, 0, JSON.stringify(result.messages))
        assert.equal(result.warningCount, 0, JSON.stringify(result.messages))
    }
})

test('Tailwind compiles existing CSS directives and retains Observatory styles', async () => {
    const from = path.join(root, 'src/index.css')
    const css = await readFile(from, 'utf8')
    const result = await postcss([
        tailwindcss({ ...tailwindConfig, content: [{ raw: '<div class="text-red-500" />' }] }),
    ]).process(css, { from })
    assert.equal(result.warnings().length, 0)
    assert.doesNotMatch(result.css, /@tailwind\s/)
    assert.match(result.css, /\.text-red-500\s*\{/)
    assert.match(result.css, /\.observatory-shell\s*\{/)
})
