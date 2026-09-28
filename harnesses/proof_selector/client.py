"""Native open-thinking extended reasoning over the local vLLM completion API.

This is a separate experiment, not the released pipeline's chat-based extended reasoning. The
server renders the initial chat once; subsequent requests carry exact token IDs
in the same assistant thinking channel. No initial final answer is generated.
"""
import hashlib
import json
import math
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


POLICY = "native_open_thinking_role_bf_v1"
MODELS = {"gemma": "google/gemma-4-31B-it", "qwen": "Qwen/Qwen3.6-27B"}
# Match the released reviewer/Fusion sampling controls; do not inherit a served
# checkpoint's generation_config.json defaults for these parameters.
SAMPLING = {"top_p": 1.0, "top_k": -1, "min_p": 0.0,
            "repetition_penalty": 1.0, "presence_penalty": 0.0,
            "frequency_penalty": 0.0}
MARKERS = {
    "gemma": {"open": "<|channel>thought\n", "end": "<channel|>",
              "turn_end": "<turn|>", "template_suffix": "<|turn>model\n"},
    "qwen": {"open": "<think>\n", "end": "</think>",
             "turn_end": "<|im_end|>", "template_suffix": "<think>\n"},
}


def _hash(value):
    data = value.encode("utf-8") if isinstance(value, str) else json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _write(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def _positive_int(name, value):
    if type(value) is not int or value <= 0:
        raise ValueError("%s must be a positive integer" % name)
    return value


def _endpoint(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1")
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path.rstrip("/") != "/v1"):
        raise ValueError("Selector endpoints must be literal loopback HTTP URLs ending in /v1")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid loopback endpoint port") from exc
    if port is not None and not 0 < port < 65536:
        raise ValueError("Invalid loopback endpoint port")
    return value.rstrip("/")


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "Redirects are disabled for selector requests", headers, fp)


class NativeBFError(RuntimeError):
    """Execution failure; this is never a mathematical rejection."""


class _PreflightError(NativeBFError):
    pass


class _FormatError(NativeBFError):
    def __init__(self, feedback):
        self.feedback = str(feedback)[:1600]
        super().__init__("Final answer failed the required output parser: " + self.feedback)


class NativeBFClient:
    def __init__(self, gemma_endpoint="http://127.0.0.1:8030/v1",
                 qwen_endpoint="http://127.0.0.1:8027/v1", timeout=2400,
                 thinking_budget=65536, answer_max_tokens=8192, bf_extensions=1,
                 max_input_tokens=24576, max_continuation_input_tokens=98304, attempts=2):
        self.endpoints = {"gemma": _endpoint(gemma_endpoint), "qwen": _endpoint(qwen_endpoint)}
        self.timeout = float(timeout)
        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError("timeout must be positive and finite")
        for key, value in (("thinking_budget", thinking_budget), ("answer_max_tokens", answer_max_tokens),
                           ("max_input_tokens", max_input_tokens),
                           ("max_continuation_input_tokens", max_continuation_input_tokens),
                           ("attempts", attempts)):
            setattr(self, key, _positive_int(key, value))
        if type(bf_extensions) is not int or bf_extensions < 0:
            raise ValueError("bf_extensions must be a nonnegative integer")
        self.bf_extensions = bf_extensions
        # Environment proxy settings must never send local proof inputs elsewhere.
        self.opener = build_opener(ProxyHandler({}), _NoRedirect())

    def _http_post(self, url, payload):
        request = Request(url, data=json.dumps(payload).encode("utf-8"),
                          headers={"Content-Type": "application/json"}, method="POST")
        with self.opener.open(request, timeout=self.timeout) as response:
            return response.read().decode("utf-8")

    def _exchange(self, endpoint, route, payload, directory, name):
        url = endpoint + route if route.startswith("/completions") else endpoint[:-3] + route
        _write(directory / (name + ".request.json"), payload)
        started = time.monotonic()
        record = {"url": url, "request_sha256": _hash(payload)}
        try:
            raw = self._http_post(url, payload)
            with (directory / (name + ".response.txt")).open("x", encoding="utf-8") as stream:
                stream.write(raw)
            record["response_sha256"] = _hash(raw)
            result = json.loads(raw)
            if not isinstance(result, dict) or result.get("error"):
                raise NativeBFError("Server returned an error or a non-object response")
            _write(directory / (name + ".response.json"), result)
            return result
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, NativeBFError) as exc:
            record["error"] = "%s: %s" % (type(exc).__name__, exc)
            if isinstance(exc, HTTPError):
                body = exc.read().decode("utf-8", errors="replace")
                with (directory / (name + ".http_error.txt")).open("x", encoding="utf-8") as stream:
                    stream.write(body)
            raise NativeBFError("Local vLLM request %s failed: %s" % (route, exc)) from exc
        finally:
            record["elapsed_seconds"] = time.monotonic() - started
            _write(directory / (name + ".transport.json"), record)

    @staticmethod
    def _ids(value, label):
        if not isinstance(value, list) or any(type(x) is not int or x < 0 for x in value):
            raise NativeBFError("%s must contain actual nonnegative token IDs; approximate fallback is disabled" % label)
        return value

    def _tokenize(self, endpoint, payload, directory, name):
        try:
            result = self._exchange(endpoint, "/tokenize", payload, directory, name)
        except NativeBFError as exc:
            raise _PreflightError("vLLM /tokenize is required for exact native extended reasoning: %s" % exc) from exc
        ids = self._ids(result.get("tokens"), "/tokenize tokens")
        if type(result.get("count")) is not int or result["count"] != len(ids):
            raise _PreflightError("/tokenize count does not match returned token IDs")
        length = result.get("max_model_len")
        if type(length) is not int or length <= 0:
            raise _PreflightError("/tokenize must report a positive max_model_len")
        return ids, length

    def _text_tokens(self, endpoint, model, text, directory, name):
        return self._tokenize(endpoint, {"model": model, "prompt": text,
                                        "add_special_tokens": False}, directory, name)

    def _detokenize(self, endpoint, model, ids, directory, name):
        result = self._exchange(endpoint, "/detokenize", {"model": model, "tokens": ids}, directory, name)
        if not isinstance(result.get("prompt"), str):
            raise _PreflightError("vLLM /detokenize must return the exact decoded prompt")
        return result["prompt"]

    @staticmethod
    def _check_budget(ids, output_tokens, input_limit, context_limit, phase):
        if len(ids) > input_limit:
            raise _PreflightError("%s input has %d tokens, exceeding input limit %d; no truncation performed" %
                                  (phase, len(ids), input_limit))
        if len(ids) + output_tokens > context_limit:
            raise _PreflightError("%s input (%d) + requested output (%d) exceeds model context (%d); no truncation performed" %
                                  (phase, len(ids), output_tokens, context_limit))

    def _generate(self, endpoint, model, ids, max_tokens, stop_id, seed,
                  temperature, directory, name, usage, context_limit, input_limit):
        self._check_budget(ids, max_tokens, input_limit, context_limit, name)
        payload = {"model": model, "prompt": ids, "max_tokens": max_tokens,
                   "temperature": temperature, "seed": seed, "n": 1, "stream": False,
                   "stop_token_ids": [stop_id], "include_stop_str_in_output": True,
                   "return_token_ids": True, "skip_special_tokens": False,
                   "add_special_tokens": False, "ignore_eos": False,
                   "echo": False, "stop": [], "min_tokens": 0, **SAMPLING}
        # Preserve attempted generation counts across successful retries. Input
        # preflight alone is not a generation request and adds no usage entry.
        accounting = {"phase": name, "usage": None, "input_tokens": len(ids),
                      "output_cap": max_tokens, "state": "request_started"}
        usage.append(accounting)
        started = time.monotonic()
        try:
            response = self._exchange(endpoint, "/completions", payload, directory, name)
        except Exception:
            accounting["state"] = "request_failed"
            raise
        finally:
            accounting["elapsed_seconds"] = time.monotonic() - started
        accounting.update({"usage": response.get("usage"), "state": "response_received"})
        choices = response.get("choices")
        if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
            raise NativeBFError("Native completion must return exactly one choice")
        choice = choices[0]
        generated = self._ids(choice.get("token_ids"), "completion token_ids")
        if not generated or len(generated) > max_tokens:
            raise NativeBFError("Native completion returned empty or over-budget token IDs")
        # vLLM 0.24.0 places prompt_token_ids on the choice. Also verify the
        # top-level field if a compatible server returns it there.
        for source in (choice, response):
            if source.get("prompt_token_ids") is not None and source["prompt_token_ids"] != ids:
                raise NativeBFError("Server reported different prompt token IDs")
        measured = response.get("usage") or {}
        if measured.get("prompt_tokens") is not None and measured["prompt_tokens"] != len(ids):
            raise NativeBFError("Server prompt usage differs from exact input token IDs")
        if measured.get("completion_tokens") is not None and measured["completion_tokens"] != len(generated):
            raise NativeBFError("Server completion usage differs from returned token IDs")
        return generated, choice

    def call(self, *, role, model, system, user, continuation, temperature, seed, output_dir, parser):
        if model not in MODELS:
            raise ValueError("model must be gemma or qwen")
        if any(not isinstance(value, str) or not value.strip() for value in (role, system, user, continuation)):
            raise ValueError("role, system, user and continuation must be nonempty strings")
        if type(seed) is not int or not 0 <= seed < 2 ** 32:
            raise ValueError("seed must be a uint32")
        if type(temperature) not in (int, float) or not math.isfinite(temperature) or temperature < 0:
            raise ValueError("temperature must be nonnegative and finite")
        markers = MARKERS[model]
        if any(marker in continuation for marker in ("<think>", "</think>", "<|channel>",
                   "<channel|>", "<|turn>", "<turn|>", "<|im_start|>", "<|im_end|>")):
            raise ValueError("Continuation must contain prose only, without channel or turn markers")
        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=False)
        started = time.monotonic()
        config = {"policy": POLICY, "role": role, "model": MODELS[model], "seed": seed,
                  "temperature": temperature, "thinking_budget": self.thinking_budget,
                  "answer_max_tokens": self.answer_max_tokens, "bf_extensions": self.bf_extensions,
                  "max_input_tokens": self.max_input_tokens,
                  "max_continuation_input_tokens": self.max_continuation_input_tokens,
                  "attempts": self.attempts, "timeout": self.timeout,
                  "sampling": SAMPLING, "answer_boundary_policy": "verified_turn_end_required",
                  "endpoint": self.endpoints[model], "system_sha256": _hash(system),
                  "user_sha256": _hash(user), "continuation_sha256": _hash(continuation)}
        _write(directory / "config.json", config)
        all_usage, errors, feedback = [], [], ""
        for attempt in range(1, self.attempts + 1):
            target = directory / ("attempt_%d" % attempt)
            target.mkdir()
            usage = []
            attempt_started = time.monotonic()
            attempt_seed = int(_hash([seed, role, model, attempt])[:8], 16)
            try:
                current_user = user + ("\n\nOutput-format correction for this fresh attempt:\n" + feedback if feedback else "")
                result = self._attempt(model, system, current_user, continuation, temperature,
                                       attempt_seed, target, usage)
                parsed = parser(result["text"])
                _write(target / "parsed.json", parsed)
                if not isinstance(parsed, dict) or parsed.get("valid") is not True:
                    raise _FormatError(json.dumps(parsed.get("errors", "Invalid output format")
                                                  if isinstance(parsed, dict) else "Parser did not return a result object",
                                                  ensure_ascii=False)[:1600])
                result.update({"parsed": parsed, "artifact_dir": str(directory),
                               "accepted_attempt": attempt, "attempt_seed": attempt_seed,
                               "usage": all_usage + [{"attempt": attempt, **entry} for entry in usage],
                               "elapsed_seconds": time.monotonic() - started, "policy": POLICY})
                _write(directory / "result.json", result)
                _write(directory / "status.json", {"state": "completed", "accepted_attempt": attempt,
                                                     "elapsed_seconds": result["elapsed_seconds"]})
                return result
            except Exception as exc:
                error = {"attempt": attempt, "attempt_seed": attempt_seed,
                         "error_type": type(exc).__name__, "error": str(exc),
                         "elapsed_seconds": time.monotonic() - attempt_started}
                _write(target / "error.json", error)
                errors.append(error)
                all_usage.extend({"attempt": attempt, **entry} for entry in usage)
                feedback = exc.feedback if isinstance(exc, _FormatError) else ""
                if isinstance(exc, _PreflightError):
                    break
        _write(directory / "status.json", {"state": "failed", "errors": errors,
                                             "usage": all_usage, "elapsed_seconds": time.monotonic() - started})
        raise NativeBFError("%s failed; see %s: %s" % (role, directory, errors[-1]["error"]))

    def _attempt(self, family, system, user, continuation, temperature, seed, directory, usage):
        endpoint, model, markers = self.endpoints[family], MODELS[family], MARKERS[family]
        kwargs = {"enable_thinking": True}
        if family == "gemma":
            kwargs["reasoning_effort"] = "max"
        initial, context = self._tokenize(endpoint, {"model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "add_generation_prompt": True, "continue_final_message": False,
            "add_special_tokens": False, "chat_template_kwargs": kwargs}, directory, "initial_template")
        rendered = self._detokenize(endpoint, model, initial, directory, "initial_template_decode")
        if family == "gemma" and rendered.endswith(markers["template_suffix"]):
            opening, opening_context = self._text_tokens(endpoint, model, markers["open"], directory, "thought_open")
            if opening_context != context:
                raise _PreflightError("Tokenizer context changed while building the thought prefix")
            initial += opening
        elif not rendered.endswith(markers["open"]):
            raise _PreflightError("Actual server chat template does not end with the expected open thinking prefix")
        rendered_open = self._detokenize(endpoint, model, initial, directory, "open_prefix_decode")
        if not rendered_open.endswith(markers["open"]):
            raise _PreflightError("Native reasoning prefix failed exact tokenizer round-trip")
        self._check_budget(initial, self.thinking_budget, self.max_input_tokens, context, "initial thinking")
        ids_by_name = {}
        for name, text in (("end", markers["end"]), ("turn_end", markers["turn_end"]),
                           ("cue", "\n\n" + continuation.strip() + "\n"),
                           ("close", markers["end"] + "\n\n")):
            ids, marker_context = self._text_tokens(endpoint, model, text, directory, name + "_tokens")
            decoded = self._detokenize(endpoint, model, ids, directory, name + "_decode")
            if marker_context != context or decoded != text or not ids:
                raise _PreflightError("Tokenizer could not reproduce the %s marker/cue exactly" % name)
            if name in ("end", "turn_end") and len(ids) != 1:
                raise _PreflightError("%s must be an unambiguous single token on the actual server" % name)
            ids_by_name[name] = ids
        end_id, turn_id = ids_by_name["end"][0], ids_by_name["turn_end"][0]
        if end_id == turn_id or ids_by_name["close"][0] != end_id:
            raise _PreflightError("Thinking and turn boundaries are ambiguous on this tokenizer")
        _write(directory / "tokenizer_provenance.json", {"model": model, "max_model_len": context,
            "markers": markers, "marker_token_ids": ids_by_name, "initial_token_ids_sha256": _hash(initial),
            "initial_rendered_sha256": _hash(rendered_open), "initial_prompt_tokens": len(initial)})
        prefix, generated_total, body_total, extensions = list(initial), 0, 0, 0
        phases, cap_hit = [], False
        for index in range(self.bf_extensions + 1):
            remaining = self.thinking_budget - generated_total
            phase = "thinking_%d" % index
            phase_seed = int(_hash([seed, phase])[:8], 16)
            generated, choice = self._generate(endpoint, model, prefix, remaining, end_id,
                phase_seed, temperature, directory, phase, usage, context,
                self.max_input_tokens if index == 0 else self.max_continuation_input_tokens)
            generated_total += len(generated)
            natural_end = choice.get("finish_reason") == "stop"
            if natural_end:
                if generated[-1] != end_id or choice.get("stop_reason") not in (None, end_id):
                    raise NativeBFError("Thinking stopped at EOS/turn or an unexpected token before its thinking-end marker")
                body = generated[:-1]
            elif choice.get("finish_reason") == "length":
                if len(generated) != remaining:
                    raise NativeBFError("Thinking length stop did not consume the declared remaining budget")
                body = generated
                cap_hit = True
            else:
                raise NativeBFError("Unexpected thinking finish reason")
            if not body or end_id in body or turn_id in body:
                raise NativeBFError("Missing reasoning body or unexpected channel/turn end inside reasoning")
            reasoning = self._detokenize(endpoint, model, body, directory, phase + "_decode")
            if not reasoning.strip():
                raise NativeBFError("Empty reasoning body; extended reasoning cannot be counted as completed")
            body_total += len(body)
            prefix.extend(body)
            extensions += int(index > 0)
            phases.append({"phase": phase, "seed": phase_seed, "finish_reason": choice.get("finish_reason"),
                "stop_reason": choice.get("stop_reason"), "generated_tokens": len(generated),
                "reasoning_body_tokens": len(body), "reasoning_chars": len(reasoning),
                "reasoning_sha256": _hash(reasoning), "generated_token_ids_sha256": _hash(generated),
                "remaining_thinking_budget": self.thinking_budget - generated_total})
            if generated_total >= self.thinking_budget:
                cap_hit = True
                break
            if not natural_end or index == self.bf_extensions:
                break
            prefix.extend(ids_by_name["cue"])
        # A stopped thought-end was removed above; insert exactly one closure,
        # including when the reasoning cap, rather than a natural stop, was hit.
        prefix.extend(ids_by_name["close"])
        answer_seed = int(_hash([seed, "answer"])[:8], 16)
        answer_ids, choice = self._generate(endpoint, model, prefix, self.answer_max_tokens,
            turn_id, answer_seed, temperature, directory, "answer", usage, context,
            self.max_continuation_input_tokens)
        if choice.get("finish_reason") != "stop":
            raise NativeBFError("Final answer did not finish completely; truncated answers are never accepted")
        # finish_reason='stop' alone also covers an unexpected EOS. A known
        # turn-end may itself be the model EOS, in which case vLLM reports None
        # rather than the stop ID; accept that only with the actual terminal ID.
        if answer_ids[-1] != turn_id or choice.get("stop_reason") not in (None, turn_id):
            raise NativeBFError("Final answer stopped without the verified turn-end token; unknown EOS/stop is not accepted")
        answer_body = answer_ids[:-1]
        if not answer_body or turn_id in answer_body or end_id in answer_body:
            raise NativeBFError("Invalid or empty final answer token sequence")
        text = self._detokenize(endpoint, model, answer_body, directory, "answer_decode")
        if not text.strip():
            raise NativeBFError("Final answer was empty")
        result = {"text": text, "actual_bf_extensions": extensions, "requested_bf_extensions": self.bf_extensions,
            "thinking_cap_hit": cap_hit, "generated_thinking_tokens": generated_total,
            "generated_reasoning_body_tokens": body_total, "injected_cue_tokens": extensions * len(ids_by_name["cue"]),
            "injected_closing_tokens": len(ids_by_name["close"]), "thinking_phases": phases,
            "answer_seed": answer_seed, "answer_tokens": len(answer_ids),
            "answer_finish_reason": choice.get("finish_reason"), "answer_stop_reason": choice.get("stop_reason"),
            "answer_boundary_policy": "verified_turn_end_required", "answer_sha256": _hash(text)}
        _write(directory / "generation.json", result)
        return result
