import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import test from 'node:test'
import vm from 'node:vm'
import { ESLint } from 'eslint'
import postcss from 'postcss'
import tailwindcss from '@tailwindcss/postcss'
import ts from 'typescript'
import semver from 'semver'

const root = fileURLToPath(new URL('../', import.meta.url))

async function bootstrapHarness(fetch) {
    const source = await readFile(new URL('../src/App.tsx', import.meta.url), 'utf8')
    const tree = ts.createSourceFile('App.tsx', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX)
    const statements = tree.statements.filter(node =>
        (ts.isFunctionDeclaration(node) && ['loadBootstrap', 'normalizeBootstrap', 'summarizeCoreState'].includes(node.name?.text)) ||
        (ts.isVariableStatement(node) && node.declarationList.declarations.some(declaration =>
            ts.isIdentifier(declaration.name) && declaration.name.text === 'FALLBACK_BOOTSTRAP')))
    const compiled = ts.transpileModule(statements.map(node => node.getText(tree)).join('\n'), {
        compilerOptions: { target: ts.ScriptTarget.ES2022 },
    })
    return vm.runInNewContext(compiled.outputText + '\n({loadBootstrap, normalizeBootstrap, summarizeCoreState, FALLBACK_BOOTSTRAP})', { fetch, AbortSignal })
}

test('bootstrap uses the existing read-only request and publishes its real result', async () => {
    const requests = []
    let syntheticPayload
    const harness = await bootstrapHarness(async (url, options) => {
        requests.push({ url, headers: options.headers, method: options.method })
        return { ok: true, json: async () => syntheticPayload }
    })
    syntheticPayload = { ...harness.FALLBACK_BOOTSTRAP, ok: true,
        observatory: { ...harness.FALLBACK_BOOTSTRAP.observatory, core_label: 'SYNTHETIC', generated_at: new Date().toISOString() } }
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

test('unreachable runtime never presents a healthy system or fabricated activity', async () => {
    const harness = await bootstrapHarness(async () => { throw new Error('offline') })
    const { payload } = await harness.loadBootstrap()
    assert.notEqual(harness.summarizeCoreState(payload), 'System Online')
    assert.equal(payload.observatory.subsystems.every(item => item.status === 'unknown' || item.status === 'offline'), true)
    assert.equal(payload.observatory.subsystems.every(item => item.activity === 0), true)
    assert.equal(payload.activity.events.length, 0)
    assert.equal(payload.ok, false)
})

test('missing subsystem evidence cannot produce System Online', async () => {
    const harness = await bootstrapHarness(() => {})
    const payload = { ...harness.FALLBACK_BOOTSTRAP, ok: true,
        observatory: { ...harness.FALLBACK_BOOTSTRAP.observatory, subsystems: [
            { name: 'kernel', status: 'active' }, { name: 'memory', status: 'unknown' },
        ] } }
    assert.notEqual(harness.summarizeCoreState(payload), 'System Online')
    payload.observatory.subsystems = []
    assert.notEqual(harness.summarizeCoreState(payload), 'System Online')
})

test('stale, undated and structurally invalid responses fall back instead of looking live', async () => {
    let payload
    const harness = await bootstrapHarness(async () => ({ ok: true, json: async () => payload }))
    for (const generated_at of ['2000-01-01T00:00:00Z', undefined, 'invalid']) {
        payload = { ...harness.FALLBACK_BOOTSTRAP, ok: true,
            observatory: { ...harness.FALLBACK_BOOTSTRAP.observatory, generated_at } }
        assert.equal((await harness.loadBootstrap()).source, 'fallback')
    }
    payload = { ok: true, read_only: true }
    assert.equal((await harness.loadBootstrap()).source, 'fallback')
    payload = { ...harness.FALLBACK_BOOTSTRAP, ok: true,
        observatory: { ...harness.FALLBACK_BOOTSTRAP.observatory, generated_at: new Date().toISOString(),
            subsystems: [{ name: 'kernel', status: 'imaginary-healthy' }] } }
    assert.equal((await harness.loadBootstrap()).source, 'fallback')
})

test('missing subsystem metrics cannot publish an unrenderable API response', async () => {
    let payload
    const harness = await bootstrapHarness(async () => ({ ok: true, json: async () => payload }))
    for (const metrics of [undefined, null, []]) {
        payload = { ...harness.FALLBACK_BOOTSTRAP, ok: true,
            observatory: { ...harness.FALLBACK_BOOTSTRAP.observatory, generated_at: new Date().toISOString(),
                subsystems: [{ name: 'guardian', label: 'Guardian', status: 'active', activity: 0, metrics }] } }
        assert.equal((await harness.loadBootstrap()).source, 'fallback')
    }
})

test('a stalled bootstrap expires so previously visible health cannot remain indefinitely', async () => {
    const harness = await bootstrapHarness((_url, { signal }) => new Promise((_resolve, reject) => {
        signal?.addEventListener('abort', () => reject(new Error('request expired')), { once: true })
    }))
    // Keep this Node test alive while the platform's unref'ed AbortSignal timer runs.
    const keepAlive = setInterval(() => {}, 1000)
    try {
        const result = await harness.loadBootstrap()
        assert.equal(result.source, 'fallback')
        assert.equal(result.payload.ok, false)
    } finally {
        clearInterval(keepAlive)
    }
})

test('malformed scene and rendered text fall back without publishing an unsafe payload', async () => {
    let payload
    const harness = await bootstrapHarness(async () => ({ ok: true, json: async () => payload }))
    const node = { name: 'guardian', label: 'Guardian', group: 'governance', x: 0, y: 1, z: 0,
        radius: 0.1, emphasis: 0.5, status: 'active', accessibility_label: 'Guardian active' }
    const connection = { source: 'guardian', target: 'memory', label: 'Observes', status: 'unknown', pulse: 0, thickness: 1 }
    for (const mutate of [
        p => { p.scene.nodes = [null] },
        p => { p.scene.nodes = [{ ...node, x: 'invalid' }] },
        p => { p.scene.nodes = [{ ...node, radius: -1 }] },
        p => { p.scene.nodes = [{ ...node, emphasis: null }] },
        p => { p.scene.nodes = [{ ...node, status: 'imaginary-healthy' }] },
        p => { p.scene.connections = [null] },
        p => { p.scene.connections = [{ ...connection, pulse: 'invalid' }] },
        p => { p.scene.connections = [{ ...connection, source: {} }] },
        p => { p.observatory.subsystems[0].summary = { message: 'invalid React child' } },
        p => { p.observatory.subsystems[0].activity = 'invalid' },
        p => { p.activity.events = [{ source: 'guardian', event_type: 'status', summary: {} }] },
        p => { p.observatory.events = [{ source: 'guardian', event_type: 'status', summary: {} }] },
        p => { p.manifest.contract_version = {} },
    ]) {
        payload = structuredClone(harness.FALLBACK_BOOTSTRAP)
        payload.ok = true
        payload.observatory.generated_at = new Date().toISOString()
        mutate(payload)
        const result = await harness.loadBootstrap()
        assert.equal(result.source, 'fallback', mutate.toString())
        assert.equal(harness.summarizeCoreState(result.payload), 'Runtime unavailable')
    }
    payload = structuredClone(harness.FALLBACK_BOOTSTRAP)
    payload.ok = true
    payload.observatory.generated_at = new Date().toISOString()
    payload.scene.nodes = [node, { ...node, name: 'memory' }]
    payload.scene.connections = [connection]
    assert.equal((await harness.loadBootstrap()).source, 'api')
})

test('canonical API observation events get visible titles and distinct renderer keys', async () => {
    const harness = await bootstrapHarness(() => {})
    const event = { source: 'guardian', event_type: 'guardian_decision', summary: 'Bounded observation',
        severity: 'notice', visual_channel: 'governance', occurred_at: '2026-11-22T07:00:00Z',
        action_required: false, details: { view: 'summary_only' } }
    const result = harness.normalizeBootstrap({ ...harness.FALLBACK_BOOTSTRAP,
        activity: { events: [event, { ...event }], limit: 8, total: 2 } })
    const events = result.activity.events
    assert.equal(events[0].title, 'guardian decision')
    assert.equal(events[0].summary, 'Bounded observation')
    assert.equal(typeof events[0].id, 'string')
    assert.notEqual(events[0].id, events[1].id)
    assert.equal(events[0].severity, 'unknown')
})

test('the lockfile matches both manifest dependency sections', async () => {
    const manifest = JSON.parse(await readFile(new URL('../package.json', import.meta.url)))
    const lock = JSON.parse(await readFile(new URL('../package-lock.json', import.meta.url)))
    for (const section of ['dependencies', 'devDependencies']) {
        assert.deepEqual(lock.packages[''][section], manifest[section])
    }
})

test('known vulnerable selector and brace paths are removed or patched', async () => {
    const lock = JSON.parse(await readFile(new URL('../package-lock.json', import.meta.url)))
    for (const [name, vulnerable] of [
        ['postcss-selector-parser', '<7.1.6'],
        ['brace-expansion', '>=4.0.0 <5.0.12'],
        ['braces', '<=3.0.3'],
    ]) {
        const instances = Object.entries(lock.packages).filter(([location]) =>
            location.endsWith(`/node_modules/${name}`) || location === `node_modules/${name}`)
        for (const [location, dependency] of instances) {
            assert.ok(semver.valid(dependency.version), `${location}: invalid version`)
            assert.equal(semver.satisfies(dependency.version, vulnerable), false, `${location}: ${dependency.version}`)
        }
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
    const css = await readFile(from, 'utf8') + '\n@source inline("text-red-500 text-aetherra-green");'
    const result = await postcss([
        tailwindcss({ base: root }),
    ]).process(css, { from })
    assert.equal(result.warnings().length, 0)
    assert.doesNotMatch(result.css, /@tailwind\s/)
    assert.match(result.css, /\.text-red-500\s*\{/)
    assert.match(result.css, /\.text-aetherra-green\s*\{/)
    assert.match(result.css, /\.observatory-shell\s*\{/)
})
