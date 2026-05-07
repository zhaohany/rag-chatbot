# Prompt V2 Homework (Simple Version)

## Goal

Upgrade prompt template from v1 to v2, so output is more stable and safer.

Scope for this homework:

- Only improve prompt engineering.

## What Students Need to Build

1. Use `query_prompt_v2.txt` as the new template.
2. Fill runtime placeholders in prompt:
   - `{top_k}`
   - `{company_policy_version}`
   - `{response_language}`
3. Keep existing placeholders working:
   - `{context_blocks}`
   - `{question}`

## Files to Change

- `app/services/generation_service.py`
- `app/core/config.py` (optional, if you want env-configurable defaults)

## Suggested Implementation Steps

1. **Homework: switch template path in config (keep repo default runnable on v1 first)**
   - Current default should stay as v1 in `app/core/config.py`:
     - `prompt_template_path = Path("data/prompts/query_prompt_v1.txt")`
   - Student task: change that line to v2:
     - `prompt_template_path = Path("data/prompts/query_prompt_v2.txt")`
   - Do this change only when testing homework output.

2. **Implement the homework function first (clear code location)**
   - Open `app/services/generation_service.py`.
   - Find `GenerationService.build_prompt_v2_homework(...)`.
   - Implement this function with the same input/output as `build_prompt(...)`:
     - Input: `question`, `retrieved_chunks`
     - Output: rendered prompt string
   - Pass all placeholders into `template.format(...)`:
     - `context_blocks`, `question`, `top_k`, `company_policy_version`, `response_language`
   - Recommended starter values:
     - `top_k`: `settings.top_k`
     - `company_policy_version`: `"v1"`
     - `response_language`: `"en-US"`

3. **Switch to the new function in one line (when ready)**
   - In `app/services/generation_service.py`, inside `build_prompt(...)`, replace default v1 path with:
   - `return self.build_prompt_v2_homework(question, retrieved_chunks)`
   - This line is already documented as a homework hook in code comments.

4. **Keep current behavior stable**
   - `/query` response schema should stay the same.
   - Prompt should still be saved to `data/prompts/final_prompt.txt`.

## Acceptance Criteria (Pass/Fail)

After calling `/query` with a valid question:

1. `data/prompts/final_prompt.txt` is generated.
2. File includes rendered values for:
   - `top_k=...`
   - `policy_version=...`
   - `response_language=...`
3. File includes v2 sections:
   - `NON-OVERRIDABLE RULES`
   - `OUTPUT CONTRACT`
   - `FEW-SHOT EXAMPLE`
4. No API schema break in `/query` response.

## Common Mistakes

1. **Template KeyError**
   - Cause: placeholder missing in `template.format(...)`.
   - Fix: ensure all placeholders in v2 template are provided.

2. **Prompt generated but metadata not replaced**
   - Cause: values passed as literal braces or wrong variable names.
   - Fix: check format kwargs names exactly match template placeholders.

3. **Over-editing scope**
   - Cause: changing retrieval or response models.
   - Fix: keep work inside prompt generation path only.

## Optional Bonus (Small)

Add one config field in `app/core/config.py`:

- `company_policy_version: str = "v1"`

Then use this config value in prompt formatting.
