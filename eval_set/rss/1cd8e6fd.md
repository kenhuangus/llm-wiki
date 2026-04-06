---
id: 1cd8e6fd
title: Normalized 2026-04-05_https___blog_trailofbits_com_2026_04_03_.md
source_url: local://C:\Users\kenhu\llm-wiki\raw\auto_ingest\rss\2026-04-05_https___blog_trailofbits_com_2026_04_03_.md
source_type: doc
domain: rss
ingested_at: '2026-04-05T19:44:42.948976+00:00'
confidence: 0.8
verified: false
---

Title: Simplifying MBA obfuscation with CoBRA
URL: https://blog.trailofbits.com/2026/04/03/simplifying-mba-obfuscation-with-cobra/
Feed: The Trail of Bits Blog
Published: Fri, 03 Apr 2026 07:00:00 -0400

## Summary

<p>Mixed Boolean-Arithmetic (MBA) obfuscation disguises simple operations like <code>x + y</code> behind tangles of arithmetic and bitwise operators. Malware authors and software protectors rely on it because no standard simplification technique covers both domains simultaneously; algebraic simplifiers don’t understand bitwise logic, and Boolean minimizers can’t handle arithmetic.</p>
<p>We&rsquo;re releasing <a href="https://github.com/trailofbits/CoBRA">CoBRA</a>, an open-source tool that simplifies the full range of MBA expressions used in the wild. Point it at an obfuscated expression and it recovers a simplified equivalent:</p>
<p><code>$ cobra-cli --mba &quot;(x&amp;y)+(x|y)&quot;</code><br />
<code>x + y</code></p>
<p><code>$ cobra-cli --mba &quot;((a^b)|(a^c)) + 65469 * ~((a&amp;(b&amp;c))) + 65470 * (a&amp;(b&amp;c))&quot; --bitwidth 16</code><br />
<code>67 + (a | b | c)</code></p>
<p>CoBRA simplifies 99.86% of the 73,000+ expressions drawn from seven independent datasets. It ships as a CLI tool, a C++ library, and an LLVM pass plugin. If you&rsquo;ve hit MBA obfuscation during malware analysis, reversing software protection schemes, or tearing apart VM-based obfuscators, CoBRA gives you readable expressions back.</p>
<h2 id="why-existing-approaches-fall-short">Why existing approaches fall short</h2>
<p>The core difficulty is that verifying MBA identities requires reasoning about how bits and arithmetic interact under modular wrapping, where values silently overflow and wrap around at fixed bit-widths. An identity like <code>(x ^ y) + 2 * (x &amp; y) == x + y</code> is true precisely because of this interaction, but algebraic simplifiers only see the arithmetic and Boolean minimizers only see the logic; neither can verify it alone. Obfuscators layer these substitutions to build arbitrarily complex expressions from simpler operations.</p>
<p>Previous MBA simplifiers have tackled parts of this problem. <a href="https://github.com/DenuvoSoftwareSolutions/SiMBA">SiMBA</a> handles linear expressions well. <a href="https://github.com/DenuvoSoftwareSolutions/GAMBA">GAMBA</a> extends support to polynomial cases. Until CoBRA, no single tool achieved high success rates across the full range of MBA expression types that security engineers encounter in the wild.</p>
<h2 id="how-cobra-works">How CoBRA works</h2>
<p>CoBRA uses a worklist-based orchestrator that classifies each input expression and selects the right combination of simplification techniques. The orchestrator manages 36 discrete passes organized across four families—linear, semilinear, polynomial, and mixed—and routes work items based on the expression&rsquo;s structure.</p>
<p>Most MBA expressions in the wild are <strong>linear</strong>: sums of bitwise terms like <code>(x &amp; y)</code>, <code>(x | y)</code>, and <code>~x</code>, each multiplied by a constant. For these, the orchestrator evaluates the expression on all Boolean inputs to produce a signature, then races multiple recovery techniques against each other and picks the cheapest verified result. Here’s what that looks like for <code>(x ^ y) + 2 * (x &amp; y)</code>:</p>
<table>
<thead>
<tr><th align="center" colspan="3">CoBRA linear simplification flow: (x ^ y) + 2 * (x &amp; y)</th></tr>
</thead>
<tbody>
<tr><td align="center" colspan="3"><em>Step 1: Classification</em><br />Input expression is identified as <strong>Linear MBA</strong></td></tr>
<tr><td align="center" colspan="3">↓</td></tr>
<tr><td align="center" colspan="3"><em>Step 2: Truth Table Generation</em><br />Evaluate on all boolean inputs → <code>[0, 1, 1, 2] truth table</code></td></tr>
<tr><td align="center" colspan="3">↓</td></tr>
<tr>
<td align="center"><em>Step 3a: Pattern Match</em><br />Scan identity database</td>
<td align="center"><em>Step 3b: ANF Conversion</em><br />Bitwise normal form</td>
<td align="center"><em>Step 3c: Interpolation</em><br />Solve basis coefficients</td>
</tr>
<tr><td align="center" colspan="3">↓</td></tr>
<tr><td align="center" colspan="3"><em>Step 4: Competition</em><br />Compare candidate results → <strong>Winner: x + y</strong> (Lowest Cost)</td></tr>
<tr><td align="center" colspan="3">↓</td></tr>
<tr><td align="center" colspan="3"><em>Step 5: Verification</em><br />Spot-check against random 64-bit inputs or prove with Z3 → <strong>Pass</strong></td></tr>
</tbody>
</table>
<p>When constant masks appear (like <code>x &amp; 0xFF</code>), the expression enters CoBRA&rsquo;s <strong>semi-linear</strong> pipeline, which breaks it down into its smallest bitwise building blocks, recovers structural patterns, and reconstructs a simplified result through bit-partitioned assembly. For expressions involving products of bitwise subexpressions (like <code>(x &amp; y) * (x | y)</code>), a decomposition engine extracts <strong>polynomial</strong> cores and solves residuals.</p>
<p><strong>Mixed</strong> expressions that combine products with bitwise operations often contain repeated subexpressions. A lifting pass replaces these with temporary variables, simplifying the inner pieces first, then solving the expression that connects them. Here’s what that looks like for a product identity <code>(x &amp; y) * (x | y) + (x &amp; ~y) * (~x &amp; y)</code>:</p>
<table>
<thead>
<tr><th align="center" colspan="2">CoBRA mixed simplification flow: (x &amp; y) * (x | y) + (x &amp; ~y) * (~x &amp; y)</th></tr>
</thead>
<tbody>
<tr><td align="center" colspan="2"><em>Step 1: Classification</em><br />Input is identified as <strong>Mixed MBA</strong></td></tr>
<tr><td align="center" colspan="2">↓</td></tr>
<tr><td align="center" colspan="2"><em>Step 2: Decompose</em><br />Decompose into subexpressions<br />↓</td></tr>
<tr>
<td align="center">(x &amp; y) * (x | y)</td>
<td align="center">(x &amp; ~y) * (~x &amp; y)</td>
</tr>
<tr>
<td align="center">↓</td>
<td align="center">↓</td>
</tr>
<tr><td align="center" colspan="2"><em>Step 3: Lift &amp; Solve</em><br />Lift products, solve inner pieces</td></tr>
<tr><td align="center" colspan="2">↓</td></tr>
<tr><td align="center" colspan="2"><em>Step 4: Collapse Identity</em><br />Collapse product identity → <strong>x * y</strong></td></tr>
<tr><td align="center" colspan="2">↓</td></tr>
<tr><td align="center" colspan="2"><em>Step 5: Verification</em><br />Spot-check against random 64-bit inputs or prove with Z3 → <strong>Pass</strong></td></tr>
</tbody>
</table>
<p>Regardless of which pipeline an expression passes through, the final step is the same: CoBRA verifies every result against random inputs or proves equivalence with Z3. No simplification is returned unless it is confirmed correct.</p>
<h2 id="what-you-can-do-with-it">What you can do with it</h2>
<p>CoBRA runs in three modes:</p>
<ul>
<li><strong>CLI tool</strong>: Pass an expression directly and get the simplified form back. Use <code>--bitwidth</code> to set modular arithmetic width (1 to 64 bits) and <code>--verify</code> for Z3 equivalence proofs.</li>
<li><strong>C++ library</strong>: Link against CoBRA&rsquo;s core library to integrate simplification into your own tools. If you’re building an automated analysis pipeline, the <code>Simplify</code> API takes an expression and returns a simplified result or reports it as unsupported.</li>
<li><strong>LLVM pass plugin</strong>: Load <code>libCobraPass.so</code> into <code>opt</code> to deobfuscate MBA patterns directly in LLVM IR. If you’re building deobfuscation pipelines on top of tools like <a href="https://github.com/lifting-bits/remill">Remill</a>, this integrates directly as a pass. It handles patterns spanning multiple basic blocks and applies a cost gate, only replacing instructions when the simplified form is smaller, and supports LLVM 19 through 22.</li>
</ul>
<h2 id="validated-against-seven-independent-datasets">Validated against seven independent datasets</h2>
<p>We tested CoBRA against 73,066 expressions from <a href="https://github.com/DenuvoSoftwareSolutions/SiMBA">SiMBA</a>, <a href="https://github.com/DenuvoSoftwareSolutions/GAMBA">GAMBA</a>, <a href="https://github.com/fvrmatteo/oracle-synthesis-meets-equality-saturation">OSES</a>, and four other independent sources. These cover the full spectrum of MBA complexity, from two-variable linear expressions to deeply nested mixed-product obfuscations.</p>
<table>
 <thead>
 <tr>
 <th style="text-align: left;">Category</th>
 <th style="text-align: left;">Expressions</th>
 <th style="text-align: left;">Simplified</th>
 <th style="text-align: left;">Rate</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td style="text-align: left;">Linear</td>
 <td style="text-align: left;">~55,000</td>
 <td style="text-align: left;">~55,000</td>
 <td style="text-align: left;">~100%</td>
 </tr>
 <tr>
 <td style="text-align: left;">Semilinear</td>
 <td style="text-align: left;">~1,000</td>
 <td style="text-align: left;">~1,000</td>
 <td style="text-align: left;">~100%</td>
 </tr>
 <tr>
 <td style="text-align: left;">Polynomial</td>
 <td style="text-align: left;">~5,000</td>
 <td style="text-align: left;">~4,950</td>
 <td style="text-align: left;">~99%</td>
 </tr>
 <tr>
 <td style="text-align: left;">Mixed</td>
 <td style="text-align: left;">~9,000</td>
 <td style="text-align: left;">~8,900</td>
 <td style="text-align: left;">~99%</td>
 </tr>
 <tr>
 <td style="text-align: left;"><strong>Total</strong></td>
 <td style="text-align: left;"><strong>73,066</strong></td>
 <td style="text-align: left;"><strong>72,960</strong></td>
 <td style="text-align: left;"><strong>99.86%</strong></td>
 </tr>
 </tbody>
</table>
<p>The 106 unsupported expressions are carry-sensitive mixed-domain cases where bitwise and arithmetic operations interact in ways that current techniques can’t decompose. CoBRA reports these as unsupported rather than guessing wrong. The full benchmark breakdown is in <a href="https://github.com/trailofbits/CoBRA/blob/master/DATASETS.md">DATASETS.md</a>.</p>
<h2 id="whats-next">What&rsquo;s next</h2>
<p>CoBRA&rsquo;s remaining failures fall into two categories: expressions with heavy subexpression duplication that exhaust the worklist budget even with lifting, and carry-sensitive residuals where bitwise masks over arithmetic products create bit-level dependencies that no current decomposition technique can recover. We’re also exploring broader integration options beyond just an LLVM pass, like native plugins for IDA Pro and Binary Ninja.</p>
<p>The source is available on GitHub under the Apache 2.0 license. If you run into expressions CoBRA can&rsquo;t simplify, please open an issue on the repository. We want the hard problems.</p>
