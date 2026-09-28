"""Native BF contract tests: no GPU, model downloads, or network requests."""
import copy
import importlib.util
import json
from pathlib import Path
from urllib.error import HTTPError

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("proof_selector_client", ROOT / "harnesses/proof_selector/client.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class Server:
    """Tiny exact tokenizer and scripted completion server, below HTTP boundary."""
    def __init__(self, outputs, context=1000000):
        self.outputs = list(outputs)
        self.context = context
        self.requests = []
        self.vocab = {x: index + 1 for index, x in enumerate(
            ("<think>", "</think>", "<|im_start|>", "<|im_end|>", "<|channel>",
             "<channel|>", "<|turn>", "<turn|>"))}
        self.counter = 100

    def encode(self, text):
        result = []
        while text:
            token = next((x for x in self.vocab if x.startswith("<") and text.startswith(x)), text[0])
            if token not in self.vocab:
                self.counter += 1
                self.vocab[token] = self.counter
            result.append(self.vocab[token])
            text = text[len(token):]
        return result

    def decode(self, ids):
        inverse = {v: k for k, v in self.vocab.items()}
        return "".join(inverse[x] for x in ids)

    def post(self, url, payload):
        self.requests.append((url, copy.deepcopy(payload)))
        if url.endswith("/tokenize"):
            if "messages" in payload:
                suffix = "<|turn>model\n" if "gemma" in payload["model"] else "<think>\n"
                text = "SYSTEM:" + payload["messages"][0]["content"] + "\nUSER:" + payload["messages"][1]["content"] + "\n" + suffix
            else:
                text = payload["prompt"]
            ids = self.encode(text)
            return json.dumps({"tokens": ids, "count": len(ids), "max_model_len": self.context})
        if url.endswith("/detokenize"):
            return json.dumps({"prompt": self.decode(payload["tokens"])})
        assert url.endswith("/v1/completions")
        output = self.outputs.pop(0)
        if isinstance(output, Exception):
            raise output
        text, finish = output[:2]
        ids = self.encode(text)
        choice = {"text": text, "token_ids": ids, "prompt_token_ids": payload["prompt"], "finish_reason": finish,
                  "stop_reason": ids[-1] if finish == "stop" and ids[-1] in payload["stop_token_ids"] else None}
        if len(output) > 2:
            choice.update(output[2])
        return json.dumps({"choices": [choice],
                           "usage": {"prompt_tokens": len(payload["prompt"]), "completion_tokens": len(ids),
                                     "total_tokens": len(payload["prompt"]) + len(ids)}})

    @property
    def completions(self):
        return [p for u, p in self.requests if u.endswith("/v1/completions")]


def run(tmp_path, monkeypatch, outputs, family="qwen", parser=None, **config):
    server = Server(outputs, config.pop("context", 1000000))
    defaults = dict(thinking_budget=100, answer_max_tokens=50, max_input_tokens=1000,
                    max_continuation_input_tokens=2000, attempts=1)
    defaults.update(config)
    instance = client.NativeBFClient(**defaults)
    monkeypatch.setattr(instance, "_http_post", server.post)
    kwargs = dict(role="review", model=family, system="ROLE", user="PROBLEM AND PROOF",
                  continuation="Wait. Check the missing obligation.", temperature=0.2,
                  seed=4294967295, output_dir=tmp_path / "call",
                  parser=parser or (lambda text: {"valid": text.strip() == "OK", "errors": ["Expected OK"]}))
    return instance, server, kwargs


@pytest.mark.parametrize("family,end,turn", [("qwen", "</think>", "<|im_end|>"),
                                            ("gemma", "<channel|>", "<turn|>")])
def test_native_think_force_think_answer_exact_prefix(tmp_path, monkeypatch, family, end, turn):
    obj, server, args = run(tmp_path, monkeypatch,
        [("first thought" + end, "stop"), ("more thought" + end, "stop"), ("OK" + turn, "stop")], family)
    result = obj.call(**args)
    calls = server.completions
    assert len(calls) == 3
    p0, p1, p2 = [server.decode(x["prompt"]) for x in calls]
    assert p0.endswith(client.MARKERS[family]["open"])
    assert p1 == p0 + "first thought\n\nWait. Check the missing obligation.\n"
    assert p2 == p1 + "more thought" + end + "\n\n"
    assert p1.count("USER:") == p2.count("USER:") == 1
    assert end not in p1 and "OK" not in p1 and "OK" not in p2
    assert all(x["return_token_ids"] and not x["skip_special_tokens"] for x in calls)
    assert all(not x["add_special_tokens"] and not x["ignore_eos"] for x in calls)
    assert all(x["top_p"] == 1.0 and x["top_k"] == -1 and x["repetition_penalty"] == 1.0 for x in calls)
    assert len({x["seed"] for x in calls}) == 3
    assert all(0 <= x["seed"] < 2**32 for x in calls)
    assert result["actual_bf_extensions"] == 1
    assert result["generated_reasoning_body_tokens"] == len("first thoughtmore thought")
    assert result["generated_thinking_tokens"] == len("first thoughtmore thought") + 2
    assert result["injected_cue_tokens"] == len(server.encode("\n\nWait. Check the missing obligation.\n"))
    assert [x["usage"]["prompt_tokens"] for x in result["usage"]] == [len(x["prompt"]) for x in calls]
    assert all("reasoning_tokens" not in x["usage"] for x in result["usage"])
    template = next(p for u, p in server.requests if u.endswith("/tokenize") and "messages" in p)
    assert template["chat_template_kwargs"]["enable_thinking"] is True
    if family == "gemma":
        assert template["chat_template_kwargs"]["reasoning_effort"] == "max"
    assert all(not u.endswith("/v1/tokenize") for u, _ in server.requests)
    assert json.loads((args["output_dir"] / "result.json").read_text())["policy"] == client.POLICY
    assert (args["output_dir"] / "attempt_1/thinking_0.response.json").exists()
    assert (args["output_dir"] / "attempt_1/tokenizer_provenance.json").exists()


def test_initial_budget_cap_closes_thought_without_claiming_extension(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch, [("x" * 10, "length"), ("OK<|im_end|>", "stop")], thinking_budget=10)
    result = obj.call(**args)
    assert len(server.completions) == 2
    assert result["thinking_cap_hit"] and result["actual_bf_extensions"] == 0
    assert result["injected_cue_tokens"] == 0
    assert server.decode(server.completions[1]["prompt"]).endswith("x" * 10 + "</think>\n\n")


def test_extension_budget_is_remaining_total_not_reset(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch,
        [("abc</think>", "stop"), ("z" * 6, "length"), ("OK<|im_end|>", "stop")], thinking_budget=10)
    result = obj.call(**args)
    assert [x["max_tokens"] for x in server.completions] == [10, 6, 50]
    assert result["generated_thinking_tokens"] == 10
    assert result["thinking_cap_hit"] and result["actual_bf_extensions"] == 1


def test_multiple_extensions_share_the_same_total_thinking_budget(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch,
        [("abc</think>", "stop"), ("def</think>", "stop"), ("zz", "length"), ("OK<|im_end|>", "stop")],
        bf_extensions=2, thinking_budget=10)
    result = obj.call(**args)
    assert [p["max_tokens"] for p in server.completions] == [10, 6, 2, 50]
    assert result["actual_bf_extensions"] == 2 and result["generated_thinking_tokens"] == 10
    assert result["thinking_cap_hit"] is True
    final_prompt = server.decode(server.completions[-1]["prompt"])
    assert final_prompt.count("Wait.") == 2 and final_prompt.count("USER:") == 1


def test_disabled_bf_goes_from_initial_thinking_to_one_answer(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch,
        [("first thought</think>", "stop"), ("OK<|im_end|>", "stop")], bf_extensions=0)
    result = obj.call(**args)
    assert len(server.completions) == 2
    assert result["actual_bf_extensions"] == result["requested_bf_extensions"] == 0
    assert result["injected_cue_tokens"] == 0 and not result["thinking_cap_hit"]
    assert "Wait." not in server.decode(server.completions[-1]["prompt"])


@pytest.mark.parametrize("outputs,match", [
    ([("abc</think>", "stop", {"token_ids": None})], "actual nonnegative token IDs"),
    ([("</think>", "stop")], "Missing reasoning body"),
    ([("abc<|im_end|>", "stop")], "before its thinking-end marker"),
    ([("abc</think>", "stop"), ("</think>", "stop")], "Missing reasoning body"),
    ([("abc</think>", "stop"), ("xyz</think>", "stop"), ("OK", "length")], "did not finish completely"),
    ([("abc</think>", "stop"), ("xyz</think>", "stop"), ("OK", "stop")], "without the verified turn-end"),
    ([("abc</think>", "stop"), ("xyz</think>", "stop"), ("OK<|im_end|>", "stop", {"stop_reason": 999})], "without the verified turn-end"),
])
def test_native_failures_never_accept_or_fallback(tmp_path, monkeypatch, outputs, match):
    obj, server, args = run(tmp_path, monkeypatch, outputs)
    with pytest.raises(client.NativeBFError, match=match):
        obj.call(**args)
    status = json.loads((args["output_dir"] / "status.json").read_text())
    assert status["state"] == "failed"
    assert not (args["output_dir"] / "result.json").exists()


@pytest.mark.parametrize("config,match", [({"max_input_tokens": 3}, "input limit"),
                                         ({"context": 110}, "exceeds model context")])
def test_initial_context_limits_fail_before_generation_without_truncation(tmp_path, monkeypatch, config, match):
    obj, server, args = run(tmp_path, monkeypatch, [], **config)
    with pytest.raises(client.NativeBFError, match=match):
        obj.call(**args)
    assert not server.completions
    assert json.loads((args["output_dir"] / "status.json").read_text())["usage"] == []
    request = next(p for u, p in server.requests if "messages" in p)
    assert request["messages"][1]["content"] == args["user"]


def test_continuation_input_limit_fails_without_truncation(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch, [("abc</think>", "stop")], max_continuation_input_tokens=5)
    with pytest.raises(client.NativeBFError, match="no truncation"):
        obj.call(**args)
    assert len(server.completions) == 1


def test_parser_retry_is_fresh_bounded_and_records_all_usage(tmp_path, monkeypatch):
    one = [("first</think>", "stop"), ("second</think>", "stop"), ("FAILED_FINAL_SENTINEL<|im_end|>", "stop")]
    two = [("new first</think>", "stop"), ("new second</think>", "stop"), ("OK<|im_end|>", "stop")]
    obj, server, args = run(tmp_path, monkeypatch, one + two, attempts=2,
        parser=lambda text: {"valid": text.strip() == "OK", "errors": ["expected format " + "x" * 2500]})
    # Permit the deliberately long (but capped) parser feedback in this test.
    obj.max_input_tokens = 4000
    obj.max_continuation_input_tokens = 5000
    result = obj.call(**args)
    templates = [p for _, p in server.requests if "messages" in p]
    second_user = templates[1]["messages"][1]["content"]
    assert "FAILED_FINAL_SENTINEL" not in second_user and "first" not in second_user
    assert len(second_user.split("fresh attempt:\n", 1)[1]) == 1600
    assert result["accepted_attempt"] == 2 and len(result["usage"]) == 6
    assert len({p["seed"] for p in server.completions}) == 6


def test_failed_generation_requests_counted_when_fresh_retry_succeeds(tmp_path, monkeypatch):
    outputs = [("old thought</think>", "stop"), OSError("connection reset"),
               ("new thought</think>", "stop"), ("more thought</think>", "stop"), ("OK<|im_end|>", "stop")]
    obj, server, args = run(tmp_path, monkeypatch, outputs, attempts=2)
    result = obj.call(**args)
    assert result["accepted_attempt"] == 2 and len(server.completions) == 5
    assert len(result["usage"]) == 5
    assert result["usage"][1]["phase"] == "thinking_1"
    assert result["usage"][1]["usage"] is None and result["usage"][1]["state"] == "request_failed"
    assert "old thought" not in server.decode(server.completions[2]["prompt"])
    assert (args["output_dir"] / "attempt_1/thinking_0.response.json").exists()
    assert (args["output_dir"] / "attempt_1/thinking_1.transport.json").exists()


def test_existing_output_directory_is_never_overwritten(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch, [])
    args["output_dir"].mkdir()
    (args["output_dir"] / "evidence").write_text("preserve")
    with pytest.raises(FileExistsError):
        obj.call(**args)
    assert (args["output_dir"] / "evidence").read_text() == "preserve"
    assert not server.requests


def test_tokenize_unavailable_fails_clearly_without_generation(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch, [], attempts=2)
    monkeypatch.setattr(obj, "_http_post", lambda *a: (_ for _ in ()).throw(OSError("404 tokenize unavailable")))
    with pytest.raises(client.NativeBFError, match="/tokenize is required"):
        obj.call(**args)
    assert not (args["output_dir"] / "attempt_2").exists()


def test_multi_token_thinking_end_is_rejected(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch, [])
    del server.vocab["</think>"]
    with pytest.raises(client.NativeBFError, match="unambiguous single token"):
        obj.call(**args)
    assert not server.completions


def test_wrong_actual_template_is_rejected(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch, [])
    original = server.post
    def wrong(url, payload):
        response = json.loads(original(url, payload))
        if url.endswith("/tokenize") and "messages" in payload:
            response["tokens"] = server.encode("closed template")
            response["count"] = len(response["tokens"])
        return json.dumps(response)
    monkeypatch.setattr(obj, "_http_post", wrong)
    with pytest.raises(client.NativeBFError, match="open thinking prefix"):
        obj.call(**args)


@pytest.mark.parametrize("endpoint", ["https://127.0.0.1:8030/v1", "http://example.com/v1",
    "http://127.0.0.2:8030/v1", "http://localhost.evil/v1", "http://user@localhost/v1",
    "http://localhost/v1?x=1", "http://localhost/other", "http://localhost/v1#fragment"])
def test_only_literal_loopback_endpoints(endpoint):
    with pytest.raises(ValueError, match="loopback"):
        client.NativeBFClient(gemma_endpoint=endpoint)


def test_redirect_is_disabled_and_keyboard_interrupt_not_swallowed(tmp_path, monkeypatch):
    with pytest.raises(HTTPError, match="Redirects are disabled"):
        client._NoRedirect().redirect_request(type("Request", (), {"full_url": "http://localhost/v1"})(),
                                             None, 307, "redirect", {}, "http://example.com/")
    obj, server, args = run(tmp_path, monkeypatch, [])
    def interrupt(*unused):
        raise KeyboardInterrupt()
    monkeypatch.setattr(obj, "_http_post", interrupt)
    with pytest.raises(KeyboardInterrupt):
        obj.call(**args)


def test_seed_reproducibility(tmp_path, monkeypatch):
    outputs = [("a</think>", "stop"), ("b</think>", "stop"), ("OK<|im_end|>", "stop")]
    a, sa, ka = run(tmp_path / "one", monkeypatch, outputs)
    b, sb, kb = run(tmp_path / "two", monkeypatch, outputs)
    ra, rb = a.call(**ka), b.call(**kb)
    assert [p["seed"] for p in sa.completions] == [p["seed"] for p in sb.completions]
    assert ra["thinking_phases"] == rb["thinking_phases"]


@pytest.mark.parametrize("location", ["choice", "top"])
@pytest.mark.parametrize("changed", [False, True])
def test_real_choice_level_and_compatible_top_level_prompt_ids(tmp_path, monkeypatch, location, changed):
    outputs = [("a</think>", "stop"), ("b</think>", "stop"), ("OK<|im_end|>", "stop")]
    obj, server, args = run(tmp_path, monkeypatch, outputs)
    original = server.post
    def with_ids(url, payload):
        response = json.loads(original(url, payload))
        if url.endswith("/v1/completions"):
            ids = response["choices"][0].pop("prompt_token_ids")
            if changed:
                ids = ids + [999]
            target = response if location == "top" else response["choices"][0]
            target["prompt_token_ids"] = ids
        return json.dumps(response)
    monkeypatch.setattr(obj, "_http_post", with_ids)
    if changed:
        with pytest.raises(client.NativeBFError, match="different prompt token IDs"):
            obj.call(**args)
    else:
        assert obj.call(**args)["parsed"]["valid"]


def test_verified_turn_end_as_default_eos_is_accepted(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch,
        [("a</think>", "stop"), ("b</think>", "stop"), ("OK<|im_end|>", "stop", {"stop_reason": None})])
    assert obj.call(**args)["answer_stop_reason"] is None


def test_inconsistent_completion_usage_is_rejected(tmp_path, monkeypatch):
    obj, server, args = run(tmp_path, monkeypatch, [("a</think>", "stop")])
    original = server.post
    def wrong_usage(url, payload):
        response = json.loads(original(url, payload))
        if url.endswith("/v1/completions"):
            response["usage"]["completion_tokens"] += 1
        return json.dumps(response)
    monkeypatch.setattr(obj, "_http_post", wrong_usage)
    with pytest.raises(client.NativeBFError, match="completion usage differs"):
        obj.call(**args)
