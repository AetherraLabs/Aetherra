import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import test from 'node:test'
import vm from 'node:vm'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import ts from 'typescript'
import * as THREE from 'three'

const require = createRequire(import.meta.url)

async function renderEvidence(name, metrics, live = true) {
    const source = await readFile(new URL('../src/SubsystemEvidence.tsx', import.meta.url), 'utf8')
        .catch(error => { if (error.code === 'ENOENT') return ''; throw error })
    const compiled = ts.transpileModule(source, { compilerOptions: {
        target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX,
    } })
    const module = { exports: {} }
    vm.runInNewContext(compiled.outputText, { module, exports: module.exports, require })
    assert.equal(typeof module.exports.default, 'function', 'Selected subsystem has no evidence renderer')
    return renderToStaticMarkup(React.createElement(module.exports.default, { name, metrics, live }))
}

test('Homeostasis renders effective mode independently of the requested mode and lifecycle badge', async () => {
    const html = await renderEvidence('homeostasis', {
        controller_mode: 'active', observe_only_requested: true,
        actuator_actions_attempted: 2, actuator_actions_executed: 1, actuator_actions_blocked: 1, restart_count: 4,
    })
    assert.match(html, /Effective mode<\/dt><dd>Active<\/dd>/)
    assert.match(html, /Observation requested<\/dt><dd>Yes<\/dd>/)
    assert.match(html, /Actuator attempts<\/dt><dd>2<\/dd>/)
    assert.match(html, /Actuator executions<\/dt><dd>1<\/dd>/)
    assert.match(html, /Orchestrator restarts<\/dt><dd>4<\/dd>/)
})

test('observed zero actuator counters render as zero while missing counters stay unknown', async () => {
    const html = await renderEvidence('homeostasis', {
        controller_mode: 'observe_only', actuator_actions_attempted: 0,
        actuator_actions_executed: 0, actuator_actions_blocked: null,
    })
    assert.match(html, /Effective mode<\/dt><dd>Observe only<\/dd>/)
    assert.match(html, /Actuator executions<\/dt><dd>0<\/dd>/)
    assert.match(html, /Actuator blocks<\/dt><dd>Unknown<\/dd>/)
    assert.match(html, /Orchestrator restarts<\/dt><dd>Unknown<\/dd>/)
})

test('a recorded proposal shows absence of approval and execution without manufacturing an audit relation', async () => {
    const html = await renderEvidence('maintenance', {
        cycle_count: 1, latest_cycle_present: true, latest_cycle_status: 'proposed',
        latest_observations: 1, latest_has_diagnosis: true, latest_has_proposal: true,
        latest_guardian_status: 'not_recorded', latest_execution_status: 'not_recorded',
        latest_security_enforced: false, latest_cycle_id_hash: '0123456789abcdef',
        latest_proposal_id_hash: 'abcdef0123456789', latest_guardian_audit_id_hash: null,
    })
    assert.match(html, /Latest in-process cycle<\/dt><dd>Proposed<\/dd>/)
    assert.match(html, /Diagnosis<\/dt><dd>Recorded<\/dd>/)
    assert.match(html, /Proposal<\/dt><dd>Recorded<\/dd>/)
    assert.match(html, /Guardian decision<\/dt><dd>Not recorded<\/dd>/)
    assert.match(html, /Execution<\/dt><dd>No execution recorded<\/dd>/)
    assert.match(html, /Guardian audit ref<\/dt><dd>Not recorded<\/dd>/)
    assert.doesNotMatch(html, /<button|<a\s|Approved|Executed/)
})

test('Guardian authorization is distinct from execution and real execution remains visible', async () => {
    const metrics = { latest_cycle_present: true, latest_guardian_status: 'allow',
        latest_execution_status: 'not_recorded', latest_guardian_audit_id_hash: 'fedcba9876543210' }
    const authorized = await renderEvidence('maintenance', metrics)
    assert.match(authorized, /Guardian decision<\/dt><dd>Allow<\/dd>/)
    assert.match(authorized, /Execution<\/dt><dd>No execution recorded<\/dd>/)
    assert.match(authorized, /Guardian audit ref<\/dt><dd>fedcba9876543210<\/dd>/)
    const applied = await renderEvidence('maintenance', { ...metrics, latest_execution_status: 'applied' })
    assert.match(applied, /Execution<\/dt><dd>Applied<\/dd>/)
})

test('an empty observed record is distinct from unavailable Maintenance data', async () => {
    const empty = await renderEvidence('maintenance', { cycle_count: 0, latest_cycle_present: false })
    assert.match(empty, /In-process cycles<\/dt><dd>0<\/dd>/)
    assert.match(empty, /Latest in-process cycle<\/dt><dd>No in-process cycle<\/dd>/)
    const missing = await renderEvidence('maintenance', {})
    assert.match(missing, /In-process cycles<\/dt><dd>Unknown<\/dd>/)
    assert.match(missing, /Latest in-process cycle<\/dt><dd>Unknown<\/dd>/)
    assert.doesNotMatch(missing, /No execution recorded|No in-process cycle/)
})

test('Guardian configuration reports effective mode and integrity without claiming individual approval', async () => {
    const html = await renderEvidence('guardian', { enabled: true, mode: 'enforcing', audit_integrity_ok: true })
    assert.match(html, /Effective mode<\/dt><dd>Enforcing<\/dd>/)
    assert.match(html, /Audit integrity<\/dt><dd>Verified<\/dd>/)
    assert.doesNotMatch(html, /Trust verified|Execution approved|Continuity verified/)
    assert.match(await renderEvidence('memory', { evidence: 'registry_heartbeat' }), /Continuity<\/dt><dd>Not verified<\/dd>/)
})

test('fallback discards stale evidence and malformed values never become rendered status', async () => {
    const offline = await renderEvidence('homeostasis', { controller_mode: 'active', actuator_actions_executed: 7 }, false)
    assert.match(offline, /Effective mode<\/dt><dd>Unknown<\/dd>/)
    assert.match(offline, /Actuator executions<\/dt><dd>Unknown<\/dd>/)
    assert.doesNotMatch(offline, />Active<|>7</)
    const malformed = await renderEvidence('maintenance', { latest_cycle_present: true,
        cycle_count: true, latest_cycle_status: { private: 'value' }, latest_guardian_status: 'private',
        latest_execution_status: [], latest_proposal_id_hash: 'private', latest_has_diagnosis: 'private' })
    assert.doesNotMatch(malformed, /private|\[object Object\]|No execution recorded/)
    assert.match(malformed, /Guardian decision<\/dt><dd>Unknown<\/dd>/)
})

test('the selected-subsystem inspector mounts the real evidence renderer', async () => {
    async function compileModule(relative, imports = {}) {
        const source = await readFile(new URL(relative, import.meta.url), 'utf8')
        const compiled = ts.transpileModule(source, { compilerOptions: {
            target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX,
        } })
        const module = { exports: {} }
        vm.runInNewContext(compiled.outputText, { module, exports: module.exports,
            require: name => Object.hasOwn(imports, name) ? imports[name] : require(name) })
        return module.exports
    }
    const evidence = await compileModule('../src/SubsystemEvidence.tsx').catch(error => {
        if (error.code === 'ENOENT') return {}
        throw error
    })
    const app = await compileModule('../src/App.tsx', { './SubsystemEvidence': evidence, three: THREE })
    const html = renderToStaticMarkup(React.createElement(app.default))
    assert.match(html, /aria-label="Subsystem evidence"/)
    assert.match(html, /Effective mode<\/dt><dd>Unknown<\/dd>/)
    assert.match(html, /Read-only observatory/)
})

test('a recorded Guardian decision with a missing audit reference keeps that relation unknown', async () => {
    const html = await renderEvidence('maintenance', {
        latest_cycle_present: true, latest_guardian_status: 'allow',
        latest_guardian_audit_id_hash: null, latest_has_proposal: true,
        latest_proposal_id_hash: null, latest_cycle_id_hash: null,
    })
    assert.match(html, /Guardian decision<\/dt><dd>Allow<\/dd>/)
    assert.match(html, /Guardian audit ref<\/dt><dd>Unknown<\/dd>/)
    assert.match(html, /Proposal ref<\/dt><dd>Unknown<\/dd>/)
    assert.match(html, /Cycle ref<\/dt><dd>Unknown<\/dd>/)
})


test('failed persistence preserves in-process evidence without claiming the store is empty or durable', async () => {
    const empty = await renderEvidence('maintenance', {
        persistence_state: 'error', cycle_count: 0, latest_cycle_present: false,
    })
    assert.match(empty, /Persistence<\/dt><dd>Error; durability unknown<\/dd>/)
    assert.match(empty, /In-process cycles<\/dt><dd>0<\/dd>/)
    assert.match(empty, /Latest in-process cycle<\/dt><dd>No in-process cycle<\/dd>/)
    assert.doesNotMatch(empty, /No cycle recorded|Store empty|Durable|<button|<a\s/)
    const proposed = await renderEvidence('maintenance', {
        persistence_state: 'error', cycle_count: 1, latest_cycle_present: true,
        latest_cycle_status: 'proposed', latest_cycle_id_hash: '0123456789abcdef',
        latest_execution_status: 'not_recorded', latest_guardian_status: 'not_recorded',
    })
    assert.match(proposed, /Latest in-process cycle<\/dt><dd>Proposed<\/dd>/)
    assert.match(proposed, /Cycle ref<\/dt><dd>0123456789abcdef<\/dd>/)
    assert.match(proposed, /Execution<\/dt><dd>No execution recorded<\/dd>/)
    assert.match(proposed, /Persistence<\/dt><dd>Error; durability unknown<\/dd>/)
})

test('persistence configuration does not claim verified durability and absent or invalid metadata stays unknown', async () => {
    for (const [state, label] of [
        ['autosave_enabled', 'Autosave enabled; durability unverified'],
        ['autosave_disabled', 'Autosave disabled'],
        ['no_store', 'No store configured'],
        ['unknown', 'Unknown'], [undefined, 'Unknown'],
        ['private-path-error', 'Unknown'], [{ private: 'error' }, 'Unknown'],
    ]) {
        const html = await renderEvidence('maintenance', { persistence_state: state })
        assert.ok(html.includes(`Persistence</dt><dd>${label}</dd>`))
        assert.doesNotMatch(html, /private|\[object Object\]|Durability verified/)
    }
    const offline = await renderEvidence('maintenance', {
        persistence_state: 'error', cycle_count: 1, latest_cycle_present: true,
    }, false)
    assert.match(offline, /Persistence<\/dt><dd>Unknown<\/dd>/)
    assert.match(offline, /In-process cycles<\/dt><dd>Unknown<\/dd>/)
    assert.doesNotMatch(offline, /Error; durability unknown/)
})
