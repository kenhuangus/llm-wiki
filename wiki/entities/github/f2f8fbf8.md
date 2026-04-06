---
id: f2f8fbf8
title: F2F8Fbf8
domain: github
source_count: 1
confidence: 0.8
verified: false
last_updated: '2026-04-06'
status: current
---

## Claims
- A LangChain serialization injection vulnerability exists in the dumps() and dumpd() functions. (Confidence: 1.0, Source: [[f2f8fbf8]])
- The vulnerability allows attackers to extract environment variable secrets by injecting specific JSON structures during deserialization. (Confidence: 1.0, Source: [[f2f8fbf8]])
- CVE-2025-68664 has a critical severity rating. (Confidence: 1.0, Source: [[f2f8fbf8]])
- The dumps() and dumpd() functions fail to escape dictionaries containing 'lc' keys when serializing free-form dictionaries. (Confidence: 1.0, Source: [[f2f8fbf8]])
- Attackers can instantiate any Serializable subclass within trusted namespaces (langchain_core, langchain, langchain_community) with controlled parameters. (Confidence: 1.0, Source: [[f2f8fbf8]])
- The vulnerability is particularly exploitable via LLM response fields like additional_kwargs or response_metadata through prompt injection. (Confidence: 1.0, Source: [[f2f8fbf8]])
- A security patch has been released that fixes the escaping bug and introduces restrictive defaults for load() and loads(). (Confidence: 1.0, Source: [[f2f8fbf8]])
- The default value for secrets_from_env has changed from True to False. (Confidence: 1.0, Source: [[f2f8fbf8]])
- Jinja2 templates are now blocked by default via the init_validator parameter to prevent arbitrary code execution. (Confidence: 1.0, Source: [[f2f8fbf8]])
- A new allowed_objects parameter defaults to 'core' to enforce an allowlist of classes that can be deserialized. (Confidence: 1.0, Source: [[f2f8fbf8]])
