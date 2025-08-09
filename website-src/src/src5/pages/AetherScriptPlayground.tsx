
import { useState } from "react";
import { CodeEditor } from "@/components/CodeEditor";
import { ScriptExecutionPanel } from "@/components/ScriptExecutionPanel";

export default function AetherScriptPlayground() {
  const [script, setScript] = useState("// Write your .aether script here");

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">.aether Script Playground</h1>
      <CodeEditor language="aether" code={script} onChange={setScript} />
      <ScriptExecutionPanel script={script} />
    </div>
  );
}
