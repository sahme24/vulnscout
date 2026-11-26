import json
import anthropic

client = anthropic.Anthropic()
system = open("triage/prompt.txt").read()
findings = json.load(open("results/findings.json"))
out, tokens_in, tokens_out = [], 0, 0

for f in findings:
    payload = {k: f[k] for k in ["tool", "file", "line", "rule", "message", "code_context"]}
    msg = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": json.dumps(payload)}],
    )
    tokens_in += msg.usage.input_tokens
    tokens_out += msg.usage.output_tokens
    text_block = next((b for b in msg.content if b.type == "text"), None)
    text = text_block.text.strip().removeprefix("```json").removesuffix("```").strip() if text_block else ""
    try:
        verdict = json.loads(text)
    except json.JSONDecodeError:
        verdict = {"verdict": "parse_error", "raw": text}
    out.append({**f, **verdict})
    print(f["id"], verdict.get("verdict"), verdict.get("confidence"))

json.dump(out, open("results/triaged.json", "w"), indent=2)
print(f"\ntokens in: {tokens_in}, tokens out: {tokens_out}")
